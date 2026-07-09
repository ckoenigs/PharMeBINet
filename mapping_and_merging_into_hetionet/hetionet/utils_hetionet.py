import sys
sys.path.append("../..")
import pharmebinetutils

def write_to_file(mondo_id,doid, mapping_method, dict_id_to_resource_and_licenses, tsv_mapping):
    licenses = dict_id_to_resource_and_licenses[mondo_id][1]
    licenses.add(pharmebinetutils.dict_source_to_license['hetionet'])
    tsv_mapping.writerow([mondo_id, doid, mapping_method,
                            pharmebinetutils.resource_add_and_prepare(dict_id_to_resource_and_licenses[mondo_id][0],
                                                                      'Hetionet'), "|".join(licenses)])