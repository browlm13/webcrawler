import os

# MAYBE DONT MAKE THIS SEPERATE CLASS
def is_sub_url(url, parent_url, url_resolver=None):

    if url_resolver is not None:
        # resolve url names
        parent_url, url = url_resolver.resolve_list([parent_url, url])

    common_path = os.path.commonprefix([parent_url, url])
    if common_path == parent_url:
        return True
    return False


"""
def filter_urls(self, urls):
    # update url_alternates_map
    self.url_alternates_map = create_url_alternates_map(urls, self.url_alternates_map)

    # map urls
    accepted_urls = list(set([self.url_alternates_map[url] for url in urls]))

    # excluded_urls
    excluded_urls = set()

    #
    # remove urls not within seed urls scope
    #

    for url in accepted_urls:
        if not is_suburl(url, self.seed_url):
            excluded_urls.add(url)
            logger.info("Out Of Bounds: %s" % url)

    #
    # remove urls not permitted by robot.txt
    #

    for url in accepted_urls:
        for furl in self.forbidden_urls:
            if is_suburl(url, furl):
                excluded_urls.add(url)
                logger.info("Access Not Permitted Robots.txt: %s" % url)

    #
    #	remove urls already in index (site_graph)
    #

    indexed_urls = [k for k, v in self.site_graph.items()]

    # add to map (shouldn't have to)
    self.url_alternates_map = create_url_alternates_map(indexed_urls, self.url_alternates_map)

    # map
    indexed_urls = [self.url_alternates_map[iurl] for iurl in indexed_urls]

    for url in accepted_urls:
        if url in indexed_urls:
            excluded_urls.add(url)

    #
    #	remove urls already in queue
    #

    queued_urls = self.queue.to_list()

    # add to map
    self.url_alternates_map = create_url_alternates_map(queued_urls, self.url_alternates_map)

    # map
    queued_urls = [self.url_alternates_map[qurl] for qurl in queued_urls]

    for url in accepted_urls:
        if url in queued_urls:
            excluded_urls.add(url)

    # remove excluded urls
    accepted_urls = set(accepted_urls).difference(excluded_urls)

    # return unique accepted urls
    return list(accepted_urls)
"""