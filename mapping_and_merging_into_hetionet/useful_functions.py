

def resource_add_and_prepare(resource, source):
    """
    add to resource a new source and generate a sort join string
    :param resource: lsit/set
    :param source: string
    :return: string
    """
    resource = set(resource)
    resource.add(source)
    return '|'.join(sorted(resource, key=lambda s: s.lower()))