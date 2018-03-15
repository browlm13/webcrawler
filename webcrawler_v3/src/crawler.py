#!/usr/bin/env python

__author__ = "L.J. Brown"
__version__ = "1.0.1"

import hashlib
import requests
from urllib.parse import urljoin
import logging
import sys

# mylib
from src import file_parser
from src import text_processing
from src import utils
from src import file_io

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def normalize_urls(base_url, raw_links):
    """ takes in list of raw links both relative and absolute and returns list of absolute links. """
    raw_links = [l for l in raw_links if l is not None]
    absolute_links = [l if l.startswith('http') else urljoin(base_url, l) for l in raw_links]
    return list(absolute_links)


def pull_summary(requested_url, included_attributes=("requested_url", "redirect_history", "status_code", "content_type","content_hash", "normalized_a_hrefs", 'normalized_img_srcs')):
    """ access a given url and return a python dictionary of page data. """

    response_summary = {
        'requested_url': requested_url,
        'status_code' : 404
    }

    # set 'requested_url' value

    try:

        # make request
        response = requests.get(requested_url)

        # set "status_code" value
        response_summary['status_code'] = response.status_code

        # log status code
        logger.info("Response Status Code: %d" % response.status_code)

        # continue if status is 200
        if response.status_code == 200:

            # set 'content_hash' value
            response_summary['content_hash'] = str(hashlib.md5(str.encode(response.text)).hexdigest())

            # set 'redirect_history'  value
            response_summary['redirect_history'] = []
            for redirect in response.history:
                response_summary['redirect_history'].append((redirect.url, redirect.status))

            # set 'content_type' value
            if 'content-type' in response.headers:
                response_summary['content_type'] = response.headers['content-type']

            # set 'binary_response_content' value
            if 'binary_response_content' in included_attributes:
                response_summary['binary_response_content'] = response.content

            # set 'plain_text' value
            if 'plain_text' in included_attributes:
                response_summary['plain_text'] = None
                if response_summary['content_type'] in file_parser.acepted_content_types():
                    response_summary['plain_text'] = file_parser.extract_plain_text(response.text, response_summary['content_type'])

            # set 'tokens' value
            if 'tokens' in included_attributes:
                if response_summary['content_type'].split(';')[0] in file_parser.acepted_content_types():
                    plain_text = file_parser.extract_plain_text(response.text, response_summary['content_type'])
                    response_summary['tokens'] = text_processing.plain_text_to_tokens(plain_text)

            if 'term_frequency_dict' in included_attributes:
               if response_summary['content_type'].split(';')[0] in file_parser.acepted_content_types():
                   plain_text = file_parser.extract_plain_text(response.text, response_summary['content_type'])
                   tokens = text_processing.plain_text_to_tokens(plain_text)
                   response_summary['term_frequency_dict'] = text_processing.word_frequency_dict(tokens)

            # if type "text/html" - read links
            if ('normalized_a_hrefs' or 'normalized_img_srcs') in included_attributes:
                if response.headers['content-type'][:9] == "text/html":

                    # Note: base_url is requested_url

                    # set 'normalized_a_hrefs'
                    response_summary['normalized_a_hrefs'] = normalize_urls(requested_url, file_parser.extract_a_hrefs_list(response.text))

                    # set 'normalized_img_srcs'
                    response_summary['normalized_img_srcs'] = normalize_urls(requested_url, file_parser.extract_img_srcs_list(response.text))

    except:
        logger.error("Requested Page: %s, Failed to read." % response_summary['requested_url'])
        logger.error(sys.exc_info())

    # filter attributes not in included_attributes tuple parameter
    response_summary = {k: v for k, v in response_summary.items() if k in included_attributes}

    return response_summary


class Crawler():

    def __init__(self, base_station):
        self.base_station = base_station

    def crawl_site(self, requested_url):

        # retrieve web page summary
        web_page_summary = pull_summary(requested_url)

        # report to base station
        index_document = self.base_station.report_web_page_summary(web_page_summary)

        # finish if content has already been indexed (duplicate on content hash)
        if not index_document:
            return

        # create document term frequency dictonary
        tfdict = pull_summary(requested_url, ('term_frequency_dict'))

        # report to base station
        self.base_station.report_term_frequency_dictionary(tfdict, web_page_summary['content_hash'])
        
"""

    Index Web Page Summaries
    Index Term Frequency Dictionaries
    
    Indexer
    
        -URL_in_Index(url) # resolves and checks
    
        -Writing Web Page Summaries (Resolves URLs before writing) 
        -URL : Indexed Resolved URL (URL_Resolver)
        -URL : ID
        
        -Document_Content_in_Index(content_hash) # checks
        
        -Writing Document Content / Updating Indexed Document Hash : ID
        -Hash : ID

"""
class URL_Indexer():

    def __init__(self):
        self.url_resolver = utils.URL_Resolver()
        self.url_id_index = utils.Incremental_Hash_ID()

    def url_in_index(self, url):
        """ Resolves passed in url and checks if it is in index. returns boolean."""
        
        resolved_url = self.url_resolver.resolve(url)
        if resolved_url in self.url_id_index:
            return True
        return False

    def add_web_page_summary(self, web_page_summary, output_directory_name):
        """ Resolves web page links, Indexes and writes web page summary only if resolved requested url is not in index."""

        # resolved requested url
        requested_url = web_page_summary['requested_url']
        resolved_requested_url = self.url_resolver.resolve(requested_url)

        # check if resolved requested url is in index. if it is, return
        if resolved_requested_url in self.url_id_index:
            return

        # add new url to index
        self.url_id_index.add(resolved_requested_url)

        # if not in index, resolve all web page links and write to file
        resolved_normalized_a_hrefs = self.url_resolver.resolve_list(web_page_summary['normalized_a_hrefs'])
        resolved_normalized_img_srcs = self.url_resolver.resolve_list(web_page_summary['normalized_img_srcs'])

        # add web_page_summary  resolved links
        # and add the additional url_id key value pair before writing to file
        written_web_page_summary = web_page_summary.copy()
        written_web_page_summary['id'] = self.url_id_index[resolved_requested_url]
        written_web_page_summary['resolved_requested_url'] = resolved_requested_url
        written_web_page_summary['resolved_normalized_a_hrefs'] = resolved_normalized_a_hrefs
        written_web_page_summary['resolved_normalized_img_srcs'] = resolved_normalized_img_srcs

        # write file
        file_io.save('web_page_summary_file_path', written_web_page_summary, [output_directory_name, written_web_page_summary['id']])
 
class Document_Indexer():

    def __init__(self):
        self.hash_id_index = utils.Incremental_Hash_ID()

    def document_in_index(self, content_hash):
        """ checks if document/content hash it is in index. returns boolean."""

        if content_hash in self.hash_id_index:
            return True
        return False

    def save_term_frequency_dictionary(self, term_frequency_dictionary, content_hash, output_directory_name):

        # add new document hash to index
        self.hash_id_index.add(content_hash)
        document_id = self.hash_id_index[content_hash]

        # write file
        file_io.save('document_frequency_dict_file_path', term_frequency_dictionary, [output_directory_name, document_id])
        
class Base_Station():
    
    def __init__(self):
        self.output_directory_name = "OUTPUT"
        self.url_indexer = URL_Indexer()
        self.document_indexer = Document_Indexer()
        
    def report_web_page_summary(self, web_page_summary):
        """ Recieves a web page summary dictonary from a crawler. Checks the content hash for content already indexed. Returns True if Not yet indexed"""

        self.url_indexer.add_web_page_summary(web_page_summary,self.output_directory_name)

        # checks if document has been indexed
        content_hash = web_page_summary['content_hash']
        return not self.document_indexer.document_in_index(content_hash)  # condinue indexing...  


    def report_term_frequency_dictionary(self, term_frequency_dictionary, content_hash):
         """ Recieves a web page summary dictonary from a crawler. Checks the content hash for contnet already indexed."""
         self.document_indexer.save_term_frequency_dictionary(term_frequency_dictionary, content_hash, self.output_directory_name)
        


url ="https://s2.smu.edu/~fmoore/"
bs = Base_Station()
c = Crawler(bs)
c.crawl_site(url)