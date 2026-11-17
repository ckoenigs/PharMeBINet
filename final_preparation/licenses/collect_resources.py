"""
Collect all distinct (unrolled) values of the "resource" list property of all nodes and relationships of
PharMeBINet and write them to a TSV file together with their usage counts.

Additionally, for every resource the license values currently stored on nodes/relationships that have exactly this
single resource are collected. These observed licenses are only meant as a help when creating or checking the
resource-to-license map (resource_to_license.tsv), they are not used for the rebuild.

Usage:
    python collect_resources.py --uri bolt://localhost:7687 --user neo4j --password secret --database pharmebinet \
        --output resources.tsv
"""
import argparse
import csv
import sys
import time

import neo4j


def parse_args():
    parser = argparse.ArgumentParser(description='Collect all distinct resource values of PharMeBINet nodes and edges')
    parser.add_argument('--uri', default='bolt://localhost:7687', help='Neo4j bolt URI (default: %(default)s)')
    parser.add_argument('--user', default='neo4j', help='Neo4j user (default: %(default)s)')
    parser.add_argument('--password', default=None, help='Neo4j password (omit if auth is disabled)')
    parser.add_argument('--database', default=None, help='Neo4j database name (default: server default database)')
    parser.add_argument('--resource-property', default='resource',
                        help='Name of the list property holding the data sources (default: %(default)s)')
    parser.add_argument('--licenses-property', default='licenses',
                        help='Name of the list property holding the licenses (default: %(default)s)')
    parser.add_argument('--output', default='resources.tsv', help='Output TSV file (default: %(default)s)')
    return parser.parse_args()


def as_list(variable: str, prop: str) -> str:
    """Cypher expression returning the property as list, also if it is wrongly stored as single value."""
    return f'CASE WHEN {variable}.`{prop}` IS :: LIST<ANY> THEN {variable}.`{prop}` ELSE [{variable}.`{prop}`] END'


def run(session, query, **params):
    start = time.time()
    result = list(session.run(query, **params))
    print('    done in %.1f s' % (time.time() - start))
    return result


def main():
    args = parse_args()
    res = args.resource_property
    lic = args.licenses_property
    auth = (args.user, args.password) if args.password is not None else None
    driver = neo4j.GraphDatabase.driver(args.uri, auth=auth)
    driver.verify_connectivity()

    # resource -> {'nodes': int, 'edges': int, 'licenses': {license: count}}
    resources = {}

    def entry(resource):
        if resource not in resources:
            resources[resource] = {'nodes': 0, 'edges': 0, 'licenses': {}}
        return resources[resource]

    with driver.session(database=args.database, default_access_mode=neo4j.READ_ACCESS) as session:
        for kind, pattern, var in (('nodes', '(e)', 'e'), ('edges', '()-[e]->()', 'e')):
            print('Checking value types of "%s" on %s' % (res, kind))
            for record in run(session, f'MATCH {pattern} RETURN valueType({var}.`{res}`) AS type, count(*) AS count'):
                print('    %s: %s' % (record['type'], record['count']))

            print('Collecting distinct resources of %s' % kind)
            query = f'''MATCH {pattern} WHERE {var}.`{res}` IS NOT NULL
                        UNWIND {as_list(var, res)} AS resource
                        RETURN resource, count(*) AS count'''
            for record in run(session, query):
                entry(record['resource'])[kind] += record['count']

            print('Collecting currently stored licenses of single-resource %s' % kind)
            query = f'''MATCH {pattern} WHERE {var}.`{lic}` IS NOT NULL
                        WITH {var}, {as_list(var, res)} AS resources WHERE size(resources) = 1
                        UNWIND {as_list(var, lic)} AS license
                        RETURN resources[0] AS resource, license, count(*) AS count'''
            for record in run(session, query):
                licenses = entry(record['resource'])['licenses']
                licenses[record['license']] = licenses.get(record['license'], 0) + record['count']
    driver.close()

    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerow(['resource', 'node_count', 'edge_count', 'observed_licenses_single_resource'])
        for resource in sorted(resources, key=lambda s: s.lower()):
            values = resources[resource]
            observed = ' || '.join('%s (%d)' % (k, v) for k, v in
                                   sorted(values['licenses'].items(), key=lambda kv: -kv[1]))
            writer.writerow([resource, values['nodes'], values['edges'], observed])
    print('Wrote %d distinct resources to %s' % (len(resources), args.output))


if __name__ == '__main__':
    sys.exit(main())
