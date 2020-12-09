# dictionary wrong (not fitting) source to real source
dict_wrong_source_to_source = {
    'MIM': 'OMIM',
    'RxCUI':'RxNorm_CUI'
}


#set of sources where the id depends on the label
set_source_where_source_depend_on_label=set(['ctd','drugbank','drugcentral', 'kegg'])

def go_through_xrefs_and_change_if_needed_source_name(xrefs, label):
    """
    go through all xrefs entry and check if the xref source is in dictionary and change to the rigth one also it depends
    on the label
    :param xrefs:list of string
    :param label: string
    :return: sorted list of xrefs
    """
    new_xref=set()
    for xref in xrefs:
        source=xref.split(':',1)[0]
        if source in dict_wrong_source_to_source:
            xref=xref.replace(source,dict_wrong_source_to_source[source])
        if source.lower() in set_source_where_source_depend_on_label:
            xref=xref.replace(source, source+' '+label)
        new_xref.add(xref)
    new_xref=list(new_xref)
    new_xref.sort()
    return new_xref
