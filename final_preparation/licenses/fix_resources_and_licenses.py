"""
Fix the "resource" and regenerate the "licenses" property of all nodes and relationships of PharMeBINet.

Step 1 - Hetionet sources:
    Nodes/relationships integrated from Hetionet have "Hetionet" in their resource list and a "source" property like
    "DisGeNET via Hetionet" or "Bgee,TISSUES via Hetionet". Each of these sources is added to the resource list as
    "Hetionet>DisGeNET", "Hetionet>Bgee", ... (the source property itself is kept). Existing "Hetionet>..." entries are
    regenerated from the source property, so the step can be repeated safely; entities without such a source property
    (e.g. stripped by remove_resources.py) keep their existing entries. Duplicate entries in any resource list are
    removed as well.

Step 2 - Licenses:
    The licenses of a node/relationship are rebuilt as the set (stored as sorted list) of the licenses of all its
    resources, using a resource-to-license map TSV. Every resource in the graph must be in the map, otherwise nothing
    is changed. A resource may map to no license (empty column), e.g. tools like rdKit.

Only nodes/relationships whose values actually change are written, so the script can be run repeatedly, e.g. at the
end of every PharMeBINet build.

The map TSV (resource_to_license.tsv) has a header; the first two columns are used, further columns are comments:
    resource    licenses    note
Multiple licenses of one resource are separated by "|".

Usage:
    python fix_resources_and_licenses.py --uri bolt://localhost:7687 --user neo4j --password secret \
        --database pharmebinet --map resource_to_license.tsv [--dry-run]
"""
import argparse
import csv
import sys
import time

import neo4j

HETIONET = 'Hetionet'
HETIONET_PREFIX = 'Hetionet>'
VIA_HETIONET = ' via Hetionet'


def parse_args():
    parser = argparse.ArgumentParser(description='Fix resources and regenerate licenses of PharMeBINet nodes and edges')
    parser.add_argument('--uri', default='bolt://localhost:7687', help='Neo4j bolt URI (default: %(default)s)')
    parser.add_argument('--user', default='neo4j', help='Neo4j user (default: %(default)s)')
    parser.add_argument('--password', default=None, help='Neo4j password (omit if auth is disabled)')
    parser.add_argument('--database', default=None, help='Neo4j database name (default: server default database)')
    parser.add_argument('--map', default='resource_to_license.tsv',
                        help='Resource to license map TSV (default: %(default)s)')
    parser.add_argument('--batch-size', type=int, default=10000,
                        help='Number of entities per transaction (default: %(default)s)')
    parser.add_argument('--concurrency', type=int, default=0,
                        help='Number of concurrent transactions (Neo4j >= 5.21); 0 runs them sequentially '
                             '(default: %(default)s)')
    parser.add_argument('--dry-run', action='store_true', help='Only count the entities that would change')
    return parser.parse_args()


def load_map(path: str) -> dict:
    resource_to_licenses = {}
    with open(path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        header = next(reader)
        if [h.strip().lower() for h in header[:2]] != ['resource', 'licenses']:
            raise ValueError('Expected header "resource<TAB>licenses" in %s but found %s' % (path, header))
        for line_number, row in enumerate(reader, start=2):
            if not row or not row[0].strip():
                continue
            resource = row[0].strip()
            licenses = sorted({x.strip() for x in (row[1] if len(row) > 1 else '').split('|') if x.strip()})
            if resource in resource_to_licenses:
                raise ValueError('Resource "%s" (line %d) is listed twice in %s' % (resource, line_number, path))
            resource_to_licenses[resource] = licenses
    return resource_to_licenses


# Cypher predicate: the entity has a Hetionet source property to derive its "Hetionet>..." entries from
HAS_VIA_SOURCE = f"'{HETIONET}' IN e.resource AND e.source IS :: STRING AND e.source ENDS WITH '{VIA_HETIONET}'"
# Cypher expression of the resource list without Hetionet source entries
KEPT = f"[r IN e.resource WHERE NOT r STARTS WITH '{HETIONET_PREFIX}']"
# Cypher expression of the Hetionet source entries derived from the source property
DERIVED = f"""[s IN split(left(e.source, size(e.source) - {len(VIA_HETIONET)}), ',') WHERE trim(s) <> ''
               | '{HETIONET_PREFIX}' + trim(s)]"""
# Cypher expression of the resource list after step 1. Entities without such a source property (e.g. stripped by
# remove_resources.py) keep their existing "Hetionet>..." entries.
EFFECTIVE = f'CASE WHEN {HAS_VIA_SOURCE} THEN {KEPT} + {DERIVED} ELSE e.resource END'

PATTERNS = (('nodes', '(e)'), ('relationships', '()-[e]->()'))


class Fixer:
    def __init__(self, session, args, resource_to_licenses):
        self.session = session
        self.args = args
        self.map = resource_to_licenses
        if args.concurrency == 1:
            concurrency = 'CONCURRENT '
        elif args.concurrency > 1:
            concurrency = '%d CONCURRENT ' % args.concurrency
        else:
            concurrency = ''
        # dry runs only read, a plain subquery is sufficient
        self.in_transactions = '' if args.dry_run else f'IN {concurrency}TRANSACTIONS OF {args.batch_size} ROWS'
        self.verb = 'would change' if args.dry_run else 'changed'

    def run_per_type(self, description: str, where: str, body: str, params: dict):
        """Run body as batched subquery for all nodes and then per relationship type."""
        rel_types = sorted(r['relationshipType'] for r in self.session.run('CALL db.relationshipTypes()'))
        matches = [('all nodes', 'MATCH (e)')] + [
            ('[%d/%d] %s' % (i, len(rel_types), t), f'MATCH ()-[e:`{t}`]->()') for i, t in enumerate(rel_types, 1)]
        changed_total = {'nodes': 0, 'relationships': 0}
        print(description)
        for name, match in matches:
            start = time.time()
            query = f'''{match} WHERE {where}
                        CALL (e) {{ {body} }} {self.in_transactions}
                        RETURN sum(changed) AS changed, count(*) AS total'''
            # CALL { } IN TRANSACTIONS requires an implicit (auto-commit) transaction, which session.run provides
            record = self.session.run(query, params).single()
            if record['total']:
                print('    %s: %s of %s %s (%.1f s)' % (name, record['changed'], record['total'], self.verb,
                                                      time.time() - start))
            changed_total['nodes' if match == 'MATCH (e)' else 'relationships'] += record['changed']
        print('    total: %s nodes and %s relationships %s' % (changed_total['nodes'],
                                                               changed_total['relationships'], self.verb))
        return changed_total

    def validate(self) -> bool:
        """Check that all (effective) resources of the graph are in the map and report entities without resource."""
        print('Validating that all resources of the graph are in the map')
        unmapped = set()
        for kind, pattern in PATTERNS:
            query = f'''MATCH {pattern} WHERE e.resource IS NOT NULL
                        UNWIND {EFFECTIVE} AS resource
                        WITH DISTINCT resource WHERE NOT resource IN $known
                        RETURN resource'''
            unmapped.update(r['resource'] for r in self.session.run(query, known=list(self.map)))
            count = self.session.run(f'MATCH {pattern} WHERE e.resource IS NULL OR size(e.resource) = 0 '
                                     f'RETURN count(e) AS count').single()['count']
            if count:
                print('WARNING: %d %s have no resource, their licenses are left untouched' % (count, kind))
        if unmapped:
            print('ERROR: the following resources are not in the map, nothing was changed:')
            for resource in sorted(unmapped, key=lambda s: str(s).lower()):
                print('    %r' % resource)
            return False
        return True

    def add_hetionet_sources(self):
        # Sort case-insensitive like pharmebinetutils.resource_add_and_prepare; only write if the set changed
        body = f'''
            WITH e, {EFFECTIVE} AS effective
            UNWIND effective AS resource
            WITH DISTINCT e, resource ORDER BY toLower(resource), resource
            WITH e, collect(resource) AS resources
            WHERE size(resources) <> size(e.resource) OR any(r IN resources WHERE NOT r IN e.resource)
            {'' if self.args.dry_run else 'SET e.resource = resources'}
            RETURN count(*) AS changed'''
        where = (f"('{HETIONET}' IN e.resource OR any(r IN e.resource WHERE r STARTS WITH '{HETIONET_PREFIX}') "
                 f"OR any(i IN range(1, size(e.resource) - 1) WHERE e.resource[i] IN e.resource[0..i]))")
        return self.run_per_type('Step 1: adding Hetionet sources to resource and removing duplicate resources',
                                 where, body, {})

    def rebuild_licenses(self):
        # Licenses are computed from the effective resources so that dry runs show the final result.
        # The [null] fallback keeps one row for entities whose resources have no license (-> empty list).
        body = f'''
            WITH e, reduce(acc = [], r IN {EFFECTIVE} | acc + coalesce($map[r], [])) AS all_licenses
            UNWIND CASE WHEN size(all_licenses) = 0 THEN [null] ELSE all_licenses END AS license
            WITH e, license ORDER BY license
            WITH e, collect(DISTINCT license) AS licenses
            WHERE e.licenses IS NULL OR e.licenses <> licenses
            {'' if self.args.dry_run else 'SET e.licenses = licenses'}
            RETURN count(*) AS changed'''
        return self.run_per_type('Step 2: regenerating licenses', 'size(e.resource) > 0', body, {'map': self.map})


def main():
    args = parse_args()
    resource_to_licenses = load_map(args.map)
    print('Loaded %d resources from %s' % (len(resource_to_licenses), args.map))

    auth = (args.user, args.password) if args.password is not None else None
    driver = neo4j.GraphDatabase.driver(args.uri, auth=auth)
    driver.verify_connectivity()
    start = time.time()
    with driver.session(database=args.database) as session:
        fixer = Fixer(session, args, resource_to_licenses)
        if not fixer.validate():
            return 1
        fixer.add_hetionet_sources()
        fixer.rebuild_licenses()
    driver.close()
    print('Finished in %.1f min%s' % ((time.time() - start) / 60, ' (dry run, nothing was written)'
                                      if args.dry_run else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())
