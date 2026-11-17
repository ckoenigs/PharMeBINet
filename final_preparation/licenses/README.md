# Resources and licenses

Every node and relationship of PharMeBINet has a `resource` list (contributing data sources) and a `licenses` list
(the licenses of these sources). The scripts in this directory keep both consistent.

* `resource_to_license.tsv` – map from every resource value to its license(s). Multiple licenses of a resource are
  separated by `|`; an empty value means the resource adds no license (e.g. the tools rdKit and OpenBabel). The `note`
  column documents where each license comes from. Resources of the form `Hetionet>Source` are the original sources of
  Hetionet content. Their licenses follow the
  [Hetionet source license table](https://github.com/dhimmel/integrate/blob/d482033bcaa913a976faf4a6ee08497281c739c3/licenses/README.md),
  updated where a source has published a license since or Hetionet recorded a permission
  ([Thinklab discussion](https://think-lab.github.io/d/107/)).
* `collect_resources.py` – lists all distinct resource values of nodes and relationships with counts and the licenses
  currently stored on single-resource entities (helps to extend/check the map).
* `fix_resources_and_licenses.py` – 1) adds the sources of Hetionet content (`source` property `"X,Y via Hetionet"`) as
  `Hetionet>X`, `Hetionet>Y` to `resource` (the `source` property is kept; duplicate resource entries are removed) and
  2) regenerates `licenses` from
  `resource` with the map. It aborts without changes if a resource is missing in the map, only writes changed entities
  and can be re-run at any time (e.g. after every build). Use `--dry-run` to only count the changes.
* `remove_resources.py` – creates a license-filtered subset without the resources of a list file (one name per line,
  `*` wildcards allowed, `#` comments). Nodes and relationships whose resources are *all* in the list are deleted
  (deleting a node also deletes its relationships). Those that also have other resources are kept but stripped, since
  it cannot be determined which property comes from which source: relationships keep only `resource` (without the
  removed resources) and `licenses` (regenerated from the remaining resources with the map); nodes additionally keep
  `id`, `identifier` and `name` (`--keep-node-properties`). Labels and relationship types stay. `Hetionet` only
  carried its original sources: if all `Hetionet>…` resources of an entity are removed, `Hetionet` does not count as
  remaining either (removing `Hetionet` removes all `Hetionet>…` too). Every list entry must
  match a resource of the graph and every remaining resource must be in the map, otherwise nothing is changed. The
  database is changed in place, so run it on a copy (e.g. loaded from the corrected dump); without `--execute` it only
  reports the numbers. `resources_to_remove.example.txt` lists the non-commercial, academic-only, unlicensed and
  CC BY-SA-incompatible resources as a starting point for a release under CC BY-SA 4.0.

```bash
pip install neo4j
python collect_resources.py --uri bolt://localhost:7687 --user neo4j --password <pw> --database pharmebinet --output resources.tsv
python fix_resources_and_licenses.py --uri bolt://localhost:7687 --user neo4j --password <pw> --database pharmebinet --map resource_to_license.tsv --dry-run
python fix_resources_and_licenses.py --uri bolt://localhost:7687 --user neo4j --password <pw> --database pharmebinet --map resource_to_license.tsv
python remove_resources.py --uri bolt://localhost:7687 --user neo4j --password <pw> --database pharmebinet --remove-list resources_to_remove.example.txt --map resource_to_license.tsv
python remove_resources.py --uri bolt://localhost:7687 --user neo4j --password <pw> --database pharmebinet --remove-list resources_to_remove.example.txt --map resource_to_license.tsv --execute
```

Note: `neo4j-admin database dump --overwrite-destination=true` (5.26.4) does not truncate an existing larger dump file,
which leaves a corrupt dump. Delete an old dump file before dumping again.

Requires Neo4j 5.23 or newer (`CALL (e) { ... }` subquery syntax); used with Neo4j 5.26.4.
