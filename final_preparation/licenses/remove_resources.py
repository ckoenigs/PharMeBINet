"""
Remove the data of the given resources from PharMeBINet, e.g. to create a subset without data from sources with
problematic licenses.

For every node and relationship that lists at least one of the given resources in its "resource" property:
* If all of its resources are removed, it is deleted. Deleting a node also deletes all of its relationships.
* If other resources remain, it is kept but stripped, because it cannot be determined which property originates from
  which source: all properties are removed except
    - relationships: "resource" (without the removed resources) and "licenses" (regenerated from the remaining
      resources with the resource-to-license map, so a license shared with a remaining resource is kept),
    - nodes: the same plus "id", "identifier" and "name" (see --keep-node-properties).
  Labels and relationship types are kept.
Nodes and relationships without any removed resource are not changed.

Hetionet rule: "Hetionet" only carried the data of its original sources ("Hetionet>Source"). If all "Hetionet>..."
resources of an entity are removed, "Hetionet" no longer counts as a remaining resource either, so the entity is deleted
unless another resource remains. Removing "Hetionet" itself also removes all "Hetionet>..." resources.

The list file contains one resource per line; empty lines and everything after # are ignored. Names must match the
resource values exactly (see resource_to_license.tsv); "*" and "?" can be used as wildcards, e.g. "Hetionet>DrugBank*".
Every entry must match at least one resource of the graph and every remaining resource must be in the map, otherwise
nothing is changed.

The database is changed in place, so run the script on a copy, e.g. a database loaded from the corrected dump.
Without --execute the script only reports what would be changed.

Usage:
    python remove_resources.py --uri bolt://localhost:7687 --user neo4j --password secret --database pharmebinet \
        --remove-list resources_to_remove.txt --map resource_to_license.tsv [--execute]
"""
import argparse
import fnmatch
import os
import sys
import time

import neo4j

from fix_resources_and_licenses import load_map

HETIONET = 'Hetionet'
HETIONET_PREFIX = 'Hetionet>'


def any_removed(v: str) -> str:
    """Cypher predicate: entity v lists at least one removed resource."""
    return f'any(r IN {v}.resource WHERE r IN $remove)'


def kept(v: str) -> str:
    """Cypher expression: remaining resources of entity v, applying the Hetionet rule."""
    return f'''CASE WHEN any(r IN {v}.resource WHERE r STARTS WITH '{HETIONET_PREFIX}')
                 AND NOT any(r IN {v}.resource WHERE r STARTS WITH '{HETIONET_PREFIX}' AND NOT r IN $remove)
            THEN [r IN {v}.resource WHERE NOT r IN $remove AND r <> '{HETIONET}']
            ELSE [r IN {v}.resource WHERE NOT r IN $remove] END'''


def all_removed(v: str) -> str:
    """Cypher predicate: entity v is affected and nothing remains -> delete."""
    return f'{any_removed(v)} AND size({kept(v)}) = 0'


def some_kept(v: str) -> str:
    """Cypher predicate: entity v is affected but resources remain -> strip."""
    return f'{any_removed(v)} AND size({kept(v)}) > 0'


ANY_REMOVED = any_removed('e')
ALL_REMOVED = all_removed('e')
SOME_KEPT = some_kept('e')

# Cypher subquery body computing the remaining resources (kept) and their licenses (licenses) of the entity e.
# The [null] fallback keeps one row for entities whose remaining resources have no license (-> empty list).
KEPT_AND_LICENSES = f'''
    WITH e, {kept('e')} AS kept
    WITH e, kept, reduce(acc = [], r IN kept | acc + coalesce($map[r], [])) AS all_licenses
    UNWIND CASE WHEN size(all_licenses) = 0 THEN [null] ELSE all_licenses END AS license
    WITH e, kept, license ORDER BY license
    WITH e, kept, collect(DISTINCT license) AS licenses'''


def parse_args():
    parser = argparse.ArgumentParser(description='Remove the data of the given resources from PharMeBINet')
    parser.add_argument('--uri', default='bolt://localhost:7687', help='Neo4j bolt URI (default: %(default)s)')
    parser.add_argument('--user', default='neo4j', help='Neo4j user (default: %(default)s)')
    parser.add_argument('--password', default=None, help='Neo4j password (omit if auth is disabled)')
    parser.add_argument('--database', default=None, help='Neo4j database name (default: server default database)')
    parser.add_argument('--remove-list', required=True, help='File with one resource (or wildcard pattern) per line')
    parser.add_argument('--map', default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                      'resource_to_license.tsv'),
                        help='Resource to license map TSV (default: resource_to_license.tsv next to this script)')
    parser.add_argument('--keep-node-properties', default='id,identifier,name',
                        help='Comma separated node properties kept on stripped nodes in addition to resource and '
                             'licenses (default: %(default)s)')
    parser.add_argument('--batch-size', type=int, default=10000,
                        help='Nodes or relationships per transaction (default: %(default)s)')
    parser.add_argument('--execute', action='store_true',
                        help='Actually change the database; without this flag only the numbers are reported')
    return parser.parse_args()


def load_patterns(path: str) -> list:
    patterns = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            entry = line.split('#', 1)[0].strip()
            if entry and entry not in patterns:
                patterns.append(entry)
    if not patterns:
        raise ValueError('No resources found in %s' % path)
    return patterns


def graph_resources(session) -> set:
    resources = set()
    for pattern in ('(e)', '()-[e]->()'):
        query = f'MATCH {pattern} WHERE e.resource IS NOT NULL UNWIND e.resource AS r RETURN DISTINCT r'
        resources.update(record['r'] for record in session.run(query))
    return resources


def count(session, query: str, remove: list) -> int:
    return session.run(query, remove=remove).single()['count']


def report(session, remove: list):
    cascade = session.run(f'''
        MATCH (e) WHERE {ALL_REMOVED}
        MATCH (e)-[rel]-()
        WITH DISTINCT rel
        WHERE NOT coalesce({all_removed('rel')}, false)
        RETURN count(rel) AS total,
               count(CASE WHEN {any_removed('rel')} THEN rel END) AS stripped''',
                          remove=remove).single()
    numbers = [
        ('nodes deleted (no resource remains)',
         count(session, f'MATCH (e) WHERE {ALL_REMOVED} RETURN count(e) AS count', remove)),
        ('nodes kept but stripped',
         count(session, f'MATCH (e) WHERE {SOME_KEPT} RETURN count(e) AS count', remove)),
        ('relationships deleted (no resource remains)',
         count(session, f'MATCH ()-[e]->() WHERE {ALL_REMOVED} RETURN count(e) AS count', remove)),
        ('relationships kept but stripped',
         count(session, f'MATCH ()-[e]->() WHERE {SOME_KEPT} RETURN count(e) AS count', remove)),
        ('relationships deleted with a deleted node', cascade['total']),
        ('  of these otherwise stripped', cascade['stripped']),
    ]
    for name, value in numbers:
        print('    %-50s %12d' % (name, value))


def totals(session) -> tuple:
    nodes = session.run('MATCH (n) RETURN count(n) AS count').single()['count']
    relationships = session.run('MATCH ()-[r]->() RETURN count(r) AS count').single()['count']
    return nodes, relationships


def run_batched(session, query: str, params: dict) -> int:
    # CALL { } IN TRANSACTIONS requires an implicit (auto-commit) transaction, which session.run provides
    return session.run(query, params).single()['count']


def main():
    args = parse_args()
    patterns = load_patterns(args.remove_list)
    resource_to_licenses = load_map(args.map)
    keep_node_properties = [p.strip() for p in args.keep_node_properties.split(',')
                            if p.strip() and p.strip() not in ('resource', 'licenses')]
    batch = f'IN TRANSACTIONS OF {args.batch_size} ROWS'
    auth = (args.user, args.password) if args.password is not None else None
    start = time.time()
    with neo4j.GraphDatabase.driver(args.uri, auth=auth) as driver, driver.session(database=args.database) as session:
        print('Collecting the resources of the graph')
        available = graph_resources(session)
        remove = set()
        unmatched = []
        for pattern in patterns:
            matched = {r for r in available if fnmatch.fnmatchcase(r, pattern)}
            if not matched:
                unmatched.append(pattern)
            remove.update(matched)
        if HETIONET in remove:
            # the Hetionet sources only came with Hetionet
            remove.update(r for r in available if r.startswith(HETIONET_PREFIX))
        if unmatched:
            print('ERROR: these entries match no resource of the graph, nothing was changed:')
            for pattern in unmatched:
                print('    %r' % pattern)
            return 1
        unmapped = sorted(available - remove - set(resource_to_licenses), key=str.lower)
        if unmapped:
            print('ERROR: these remaining resources are not in the map %s, nothing was changed:' % args.map)
            for resource in unmapped:
                print('    %r' % resource)
            return 1
        remove = sorted(remove, key=str.lower)
        print('Resources to remove (%d):' % len(remove))
        for resource in remove:
            print('    %s' % resource)

        nodes_before, rels_before = totals(session)
        print('Graph: %d nodes, %d relationships' % (nodes_before, rels_before))
        print('Changes:')
        report(session, remove)
        if not args.execute:
            print('Dry run, nothing was changed (use --execute to apply)')
            return 0

        params = {'remove': remove, 'map': resource_to_licenses}
        node_map = ', '.join(['resource: kept', 'licenses: licenses'] +
                             [f'`{p}`: e.`{p}`' for p in keep_node_properties])

        # 1. relationships, per type to keep the queries small: delete those without remaining resources (incl. the
        #    Hetionet rule), strip the others to their remaining resources and licenses (SET e = {...} replaces all
        #    properties)
        print('Relationships (deleted / stripped)')
        rel_types = sorted(r['relationshipType'] for r in session.run('CALL db.relationshipTypes()'))
        for rel_type in rel_types:
            deleted = run_batched(session, f'''
                MATCH ()-[e:`{rel_type}`]->() WHERE {ALL_REMOVED}
                CALL (e) {{ DELETE e }} {batch}
                RETURN count(*) AS count''', params)
            stripped = run_batched(session, f'''
                MATCH ()-[e:`{rel_type}`]->() WHERE {SOME_KEPT}
                CALL (e) {{ {KEPT_AND_LICENSES}
                    SET e = {{resource: kept, licenses: licenses}} }} {batch}
                RETURN count(*) AS count''', params)
            if deleted or stripped:
                print('    %s: %d / %d' % (rel_type, deleted, stripped))

        # 2. nodes without remaining resources: first their relationships, in batches of relationships so that
        #    high-degree nodes do not create huge transactions (outgoing first, then incoming, so that a relationship
        #    between two such nodes is only deleted once), then the nodes themselves
        print('Deleting relationships of nodes without remaining resources')
        for direction, pattern in (('outgoing', '(e)-[rel]->()'), ('incoming', '(e)<-[rel]-()')):
            deleted = run_batched(session, f'''
                MATCH {pattern} WHERE {ALL_REMOVED}
                CALL (rel) {{ DELETE rel }} {batch}
                RETURN count(*) AS count''', params)
            print('    %s: %d' % (direction, deleted))
        print('Deleting nodes without remaining resources')
        deleted = run_batched(session, f'''
            MATCH (e) WHERE {ALL_REMOVED}
            CALL (e) {{ DETACH DELETE e }} {batch}
            RETURN count(*) AS count''', params)
        print('    %d nodes' % deleted)

        # 3. nodes with remaining resources: strip to remaining resources, licenses and the kept properties
        print('Stripping nodes with remaining resources (keeping %s)' % ', '.join(
            ['resource', 'licenses'] + keep_node_properties))
        stripped = run_batched(session, f'''
            MATCH (e) WHERE {SOME_KEPT}
            CALL (e) {{ {KEPT_AND_LICENSES}
                SET e = {{{node_map}}} }} {batch}
            RETURN count(*) AS count''', params)
        print('    %d nodes' % stripped)

        nodes_after, rels_after = totals(session)
        print('Graph now: %d nodes (-%d), %d relationships (-%d)' % (
            nodes_after, nodes_before - nodes_after, rels_after, rels_before - rels_after))
        left = count(session, f'MATCH (e) WHERE {ANY_REMOVED} RETURN count(e) AS count', remove) + count(
            session, f'MATCH ()-[e]->() WHERE {ANY_REMOVED} RETURN count(e) AS count', remove)
        if left:
            print('ERROR: %d nodes/relationships still list a removed resource' % left)
            return 1
    print('Finished in %.1f min' % ((time.time() - start) / 60))
    return 0


if __name__ == '__main__':
    sys.exit(main())
