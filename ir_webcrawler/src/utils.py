import os

def sub_directory(check_url, parent_url):
    """
    :param check_url: resolved, normalized url string. Child URL in question.
    :param parent_url: resolved, normalized url string. Parent URL in question.
    :return: Boolean return. True if check_url is a sub directory of the parent url.
    """
    common_path = os.path.commonprefix([check_url, parent_url])
    if common_path == parent_url:
        return True
    return False

def filter_sub_directories(list_check_urls, list_parent_urls, filter_if_sub=False):
    """
    :param list_check_urls: list of urls (resolved, normalized url strings) to filter.
    :param list_parent_urls: list of urls (resolved, normalized url strings) to act as bounds, all must be satisfied.
    :param filter_if_sub: Boolean, default False. If set to True, filters directories that are sub directories.
    :return: reduced list of check_urls satisfying condition.
    """
    child_urls = []
    for parent in list_parent_urls:
        get_child = lambda check_url: sub_directory(check_url, parent)
        child_urls += list(filter(get_child, list_check_urls))

    child_urls = set(child_urls)
    if filter_if_sub:
        return list(set(list_check_urls).difference(child_urls))
    return list(child_urls)


check_urls = ["this/is/fine/man", 'this/is/not/fine', "no/way", "this/is/fine/also"]
parent_urls = ["this/is/fine/"]

print(filter_sub_directories(check_urls, parent_urls, filter_if_sub=True))
