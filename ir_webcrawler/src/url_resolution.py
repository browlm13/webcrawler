import requests
import json


"""
            maintain a growing dictionary that resolves urls to the final redirection address or itself
            keep this dictionary in memory to minimize requests being made
            will accept list of urls and return mapped values
            implement methods to save and load this dictionary

            class URL_Resolver():

                def __init__(self):
                    self.url_resolution_map = {}

                def resolve(self, list_of_urls):
                    returns list_of_resolved_urls

                def save(self, output_file):
                def load(self, input_file):

url_resolver.resolve_list([url,'https://s2.smu.edu/~fmoore/'], collapse=True)
"""


class URL_Resolver():

    def __init__(self):
        self.url_resolution_map = {}

    def _network_url_resolution(self, url):
        try:
            response = requests.get(url)
            if response.url is None:
                return url
            return response.url
        except:
            return url

    def resolve(self, url):
        if url not in self.url_resolution_map:
            self.url_resolution_map[url] = self._network_url_resolution(url)
        return self.url_resolution_map[url]

    def resolve_list(self, list_of_urls, collapse=False):
        """
        :param list_of_urls:
        :return: list of resolved urls
        """

        for url in list_of_urls:
            if url not in self.url_resolution_map:
                self.url_resolution_map[url] = self._network_url_resolution(url)

        if collapse:
            return list(set([self.url_resolution_map[url] for url in list_of_urls]))
        return [self.url_resolution_map[url] for url in list_of_urls]

    def get_map(self):
        return self.url_resolution_map

    def save(self, file_path):
        with open(file_path, 'w') as file:
            file.write(json.dumps(self.get_map()))

    def load(self, file_path):
        with open(file_path) as json_data:
            self.url_resolution_map = json.load(json_data)


