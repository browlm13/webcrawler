#!/usr/bin/env python

__author__ = "L.J. Brown"
__version__ = "1.0.1"

import hashlib
import requests
from urllib.parse import urljoin
import logging

# mylib
from src import file_parser
from src import text_processing

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def normalize_urls(base_url, raw_links):
    """ takes in list of raw links both relative and absolute and returns list of absolute links. """
    raw_links = [l for l in raw_links if l is not None]
    absolute_links = [l if l.startswith('http') else urljoin(base_url, l) for l in raw_links]
    return list(absolute_links)


def pull_summary(requested_url, included_attributes=("requested_url", "redirect_history", "status_code", "content_type", "document_hash", "normalized_a_hrefs", 'normalized_img_srcs')):
    """ access a given url and return a python dictionary of page data. """

    response_summary = {}

    # set 'requested_url' value
    response_summary['requested_url'] = requested_url

    try:

        # make request
        response = requests.get(requested_url)

        # set "status_code" value
        response_summary['status_code'] = response.status_code

        # log status code
        logger.info("Response Status Code: %d" % response.status_code)

        # continue if status is 200
        if response.status_code == 200:

            # set 'document_hash' value
            response_summary['document_hash'] = str(hashlib.md5(str.encode(response.text)).hexdigest())

            # set 'redirect_history'  value
            response_summary['redirect_history'] = []
            for redirect in response.history:
                response_summary['redirect_history'].append((redirect.url, redirect.status))

            # set 'content_type' value
            if 'content-type' in response.headers:
                response_summary['content_type'] = response.headers['content-type']

            # set 'binary_response_content' value
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
                    tokens = response_summary['tokens'] = text_processing.plain_text_to_tokens(plain_text)
                    response_summary['tokens'] = tokens

            # if type "text/html" - read links
            if response.headers['content-type'][:9] == "text/html":

                # Note: base_url is requested_url

                # set 'normalized_a_hrefs'
                response_summary['normalized_a_hrefs'] = normalize_urls(requested_url, file_parser.extract_a_hrefs_list(response.text))

                # set 'normalized_img_srcs'
                response_summary['normalized_img_srcs'] = normalize_urls(requested_url, file_parser.extract_img_srcs_list(response.text))

    except:
        logger.error("Requested Page: %s, Failed to read." % response_summary['requested_url'])
        logger.error(sys.exc_info())

    # filter atributes not in included_attributes tuple parameter
    response_summary = {k:v for k,v in response_summary.items() if k in included_attributes}

    return response_summary


"""

    # set 'requested_url' value
    if 'requested_url' in included_attributes:
        response_summary['requested_url'] = requested_url

    #try:

    # make request
    response = requests.get(requested_url)
    logger.info("Response Status Code: %d" % response.status_code)

    # set "status_code" value
    if 'status_code' in included_attributes:
        response_summary['status_code'] = response.status_code

    # continue if status is 200
    if response.status_code == 200:

        # set 'redirect_history'  value
        if 'redirect_history' in included_attributes:
            response_summary['redirect_history'] = []
            for redirect in response.history:
                response_summary['redirect_history'].append((redirect.url, redirect.status))

        # set 'content_type' page_data value
        if 'content_type' in included_attributes:
            if 'content-type' in response.headers:
                response_summary['content_type'] = response.headers['content-type']

        # set 'document_hash' page_data value
        if 'document_hash' in included_attributes:
            response_summary['document_hash'] = str(hashlib.md5(str.encode(response.text)).hexdigest())

        # set 'binary_response_content' value
        if 'binary_response_content' in included_attributes:
            response_summary['binary_response_content'] = response.content

        # set 'plain_text' value
        if 'plain_text' in included_attributes:
            response_summary['plain_text'] = None
            if response_summary['content_type'] in file_parser.excepted_content_types():
                response_summary['plain_text'] = file_parser.extract_plain_text(response.text, response_summary['content_type'])

        # set 'tokens' value
        if 'tokens' in included_attributes:
            if response_summary['content_type'].split(';')[0] in file_parser.excepted_content_types():
                plain_text = file_parser.extract_plain_text(response.content, response_summary['content_type'])
                tokens = response_summary['tokens'] = text_processing.plain_text_to_tokens(plain_text)
                response_summary['tokens'] = tokens

        # if type "text/html" - read links
        if response.headers['content-type'][:9] == "text/html":

            # assume base url is requested url

            # set a hrefs
            if 'normalized_a_hrefs' in included_attributes:
                response_summary['normalized_a_hrefs'] = normalize_urls(requested_url, file_parser.extract_a_hrefs_list(response.text))

            # set img srcs
            if 'normalized_img_srcs' in included_attributes:
                response_summary['normalized_img_srcs'] = normalize_urls(requested_url, file_parser.extract_img_srcs_list(response.text))


        #except:
    #    logger.error("Requested Page: %s, Failed to read." % response_summary['requested_url'])
    #    logger.error(sys.exc_info())

    return response_summary
"""

