#!/usr/bin/env python

__author__ = "L.J. Brown"
__version__ = "1.0.1"

import hashlib
import requests
from urllib.parse import urljoin
import logging
import sys

# external
from bs4 import BeautifulSoup

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def normalize_urls(base_url, raw_links):
    """ takes in list of raw links both relative and absolute and returns list of absolute links. """
    raw_links = [l for l in raw_links if l is not None]
    absolute_links = [l if l.startswith('http') else urljoin(base_url, l) for l in raw_links]
    return list(absolute_links)


def get_response_summary(url, url_resolver):
    """ access a given url and return a python dictonary of page data. """

    response_summary = {
        'requested_url': None,
        'response_url': None,
        'broken': True,
        'content_type': None,
        'binary_response_content': None,  # http://docs.python-requests.org/en/master/user/quickstart/#raw-response-content
        'document_hash': None,
        'resolved_normalized_a_hrefs': [],
        'resolved_normalized_img_srcs': [],
     }

    # set 'requested_url' value
    response_summary['requested_url'] = url

    try:
        #
        #	make request, continue if status code is 200.
        #
        response = requests.get(url)
        logger.info("Response Status Code: %d" % response.status_code)

        if response.status_code == 200:

            # set 'broken' page_data value to True
            response_summary['broken'] = False

            # set 'response_url' page_data value
            if response.history and (response.url is not None):
                response_summary['response_url'] = response.url
            else:
                response_summary['response_url'] = response_summary['requested_url']

            # set 'content_type' page_data value
            if 'content-type' in response.headers:
                response_summary['content_type'] = response.headers['content-type']

            # set 'document_hash' page_data value
            #response_summary['document_hash'] = str(hashlib.md5(str.encode(response.text)).hexdigest())    ?????

            # set 'binary_response_content' value
            response_summary['binary_response_content'] = response.content

            # set 'document_hash' page_data value
            response_summary['document_hash'] = str(hashlib.md5(response_summary['binary_response_content']).hexdigest())


            # if type "text/html" - read links
            if response_summary['content_type'][:9] == "text/html":

                soup = BeautifulSoup(response_summary['binary_response_content'], 'html.parser')
                #soup = BeautifulSoup(response.text, 'html.parser')

                # set 'resolved_normalized_a_hrefs' page_data value
                a_hrefs = [l.get('href') for l in soup.find_all('a')]
                normalized_a_hrefs = normalize_urls(response_summary['response_url'], a_hrefs)
                response_summary['resolved_normalized_a_hrefs'] = url_resolver.resolve_list(normalized_a_hrefs, collapse=True)

                # set 'resolved_normalized_img_srcs' page_data value
                img_src = [l.get('src') for l in soup.find_all('img', src=True)]
                normalized_img_srcs = normalize_urls(response_summary['response_url'], img_src)
                response_summary['resolved_normalized_img_srcs'] = url_resolver.resolve_list(normalized_img_srcs, collapse=True)


    except:
        logger.error("Requested Page: %s, Failed to read." % response_summary['requested_url'])
        logger.error(sys.exc_info()[0])

    return response_summary


