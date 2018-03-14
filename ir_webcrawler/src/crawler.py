#!/usr/bin/env python

__author__ = "L.J. Brown"
__version__ = "1.0.1"

from urllib.parse import urljoin
import os
import logging
import json
import glob

# my lib
from src import url_resolution as url_resolution
from src import url_accessor
from src import file_parser as fp
from src import file_io_handler
from src import data_structures as ds
from src import text_processing

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# helper should proably be moved alog with normalizer in url accessor, possibly in same file as url_resolution


def is_sub_url(url, parent_url, url_resolver=None):
    if url_resolver is not None:
        # resolve url names
        parent_url, url = url_resolver.resolve_list([parent_url, url])

    common_path = os.path.commonprefix([parent_url, url])
    if common_path == parent_url:
        return True
    return False


class Crawler():

    def __init__(self):
        # self.site_graph = {}
        # self.url_alternates_map = {}
        # self.url_id_map = ds.DoubleDict()

        self.url_frontier = ds.URL_Frontier()
        self.url_id_map = ds.ID_Dict()
        self.indexed_document_hashes = ds.Seen()
        self.url_resolver = url_resolution.URL_Resolver()
        self.file_parser = fp.File_Parser()
        self.directory_structure_dict = file_io_handler.load_directory_structure()

    def filter_urls(self, urls):

        # map urls
        accepted_urls = self.url_resolver.resolve_list(urls, collapse=True)

        # excluded_urls
        excluded_urls = set()

        # remove urls not within seed urls scope
        for url in accepted_urls:
            if not is_sub_url(url, self.seed_url, self.url_resolver):
                excluded_urls.add(url)
                logger.info("Out Of Bounds: %s" % url)

        # remove urls not permitted by robot.txt
        for url in accepted_urls:
            for furl in self.forbidden_urls:
                if is_sub_url(url, furl, self.url_resolver):
                    excluded_urls.add(url)
                    logger.info("Access Not Permitted Robots.txt: %s" % url)

        # remove urls already in url_id_map (index)
        for url in accepted_urls:
            if url in self.url_id_map:
                excluded_urls.add(url)

        # remove excluded urls
        accepted_urls = set(accepted_urls).difference(excluded_urls)

        # return unique accepted urls
        return list(accepted_urls)


    def read_robots(self):

        # find forbidden urls
        self.forbidden_urls = []

        # get the robots.txt url for the seed url
        robots_url = self.seed_url + "robots.txt"

        # extract the forbidden routes
        response_summary = url_accessor.get_response_summary(robots_url, self.url_resolver)

        robots_string = self.file_parser.extract_plain_text(response_summary['binary_response_content'],
                                                            response_summary['content_type'])
        if robots_string is not None:
            for line in robots_string.split("\n"):
                if line.startswith('Disallow'):
                    forbidden = line.split(':')[1].strip()

                    if forbidden[0] == '/':
                        forbidden = forbidden[1:]

                    seed_url = self.seed_url
                    if self.seed_url[-1] == '/':
                        seed_url = self.seed_url[:-1]

                    # add site prefix
                    self.forbidden_urls.append(seed_url + '/' + forbidden)

    def continue_indexing(self):

        # stop if url queue is empty
        if len(self.url_frontier) == 0:
            return False

        # stop if max_urls_to_index param has been reached
        if self.max_urls_to_index is not None:
            return len(self.url_id_map) < self.max_urls_to_index

        return True

    def crawl_site(self, seed_url, output_directory_name, max_urls_to_index=None, stopwords_file=None):

        self.output_directory_name = output_directory_name
        self.max_urls_to_index = max_urls_to_index
        self.stopwords_file = stopwords_file

        # resolve seed url
        self.seed_url = self.url_resolver.resolve(seed_url)

        # set forbidden_urls
        self.read_robots()

        # add seed url to url frontier
        self.url_frontier.add(self.seed_url)

        # log info
        logger.info("Beginning Site Crawl: %s" % self.seed_url)
        if self.max_urls_to_index is not None:
            logger.info("Number of Sites to Index: %d" % self.max_urls_to_index)
        else:
            logger.info("Index Forever")

        # begin crawl
        while self.continue_indexing():

            # retrieve url to index
            target_url = self.url_frontier.remove()

            # ensure it is resolved
            target_url = self.url_resolver.resolve(target_url)

            # add it to url_id_map (index)
            self.url_id_map.add(target_url)

            # log info
            logger.info("Crawling URL Number: %d" % self.url_id_map[target_url])
            logger.info("Crawling URL: %s" % target_url)

            # access site and get response summary
            response_summary = url_accessor.get_response_summary(target_url, self.url_resolver)

            if not response_summary['broken']:

                # save response summary (add id , remove binary_response_content)
                written_response_summary = {k: v for k, v in response_summary.items() if k != 'binary_response_content'}
                written_response_summary['url_id'] = self.url_id_map[target_url]


                response_summary_directory = self.directory_structure_dict['path_templates'][
                                                 'response_summaries_directory_path_template'] \
                                             % (self.output_directory_name)

                # if response_summary_directory does not exist, create it
                if not os.path.exists(response_summary_directory):
                    os.makedirs(response_summary_directory)

                response_summary_file_path = self.directory_structure_dict['path_templates']['response_summaries_file_path_template'] \
                    % (self.output_directory_name, written_response_summary['url_id'])


                # write response summary file
                with open(response_summary_file_path, 'w') as file:
                    file.write(json.dumps(written_response_summary))

                if response_summary['document_hash'] not in self.indexed_document_hashes:

                    # extract and tokenize plain text, then save to document file
                    plain_text = self.file_parser.extract_plain_text(response_summary['binary_response_content'], response_summary['content_type'])
                    tokens = text_processing.plain_text_to_tokens(plain_text, self.stopwords_file)



                    # write tokens to document file
                    document_directory = self.directory_structure_dict['path_templates'][
                                                     'document_directory_path_template'] \
                                                 % (self.output_directory_name, response_summary['document_hash'])

                    # if document_directory does not exist, create it
                    if not os.path.exists(document_directory):
                        os.makedirs(document_directory)

                    document_tokens_file_path = self.directory_structure_dict['path_templates'][
                                                     'document_tokens_file_path_template'] \
                                                 % (self.output_directory_name, response_summary['document_hash'])

                    with open(document_tokens_file_path, 'w') as file:
                        file.write(json.dumps(tokens))

                    # update document hash index if document has not been seen
                    self.indexed_document_hashes.add(response_summary['document_hash'])

            # Add New Urls To Queue And Continue Crawling
            #self.url_frontier.add_list(self.filter_urls(response_summary['resolved_normalized_a_hrefs']))
            for filtered_url in self.filter_urls(response_summary['resolved_normalized_a_hrefs']):
                self.url_frontier.add(filtered_url)


            print("Before Filter")
            print(response_summary['resolved_normalized_a_hrefs'])
            print("After Filter")
            print(self.filter_urls(response_summary['resolved_normalized_a_hrefs']))
            print("Queue")
            print(self.url_frontier.to_list())
