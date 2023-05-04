

def prepare_url_id(identifier):
    """
    Get the different identifier form refseq. All identifier have the form 'rna-*'. So the first letterst are removed.
    Then I try to get only the refseq identifier which have the form '$$_*.N' $=one character, N=number.
    The number at the end need to be removed
    :param identifier:
    :return:
    """
    url = ''
    prepare_url = identifier[4:]
    if prepare_url[2] == '_':
        url = prepare_url.split('.')[0]
    return url