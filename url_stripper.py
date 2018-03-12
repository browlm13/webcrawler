#!/usr/bin/env python

__author__  = "L.J. Brown"
__version__ = "1.0.1"

import re

"""
                                url stripper

"""

#settings
ERROR_STRING = "-1"

def strip_url_prefix(url):
    """  strip url prefix (remove http:// and or www.) """

    global ERROR_STRING

    try :
        regex = r'(https://)?(http://)?(www\.)?(?P<target>.*)'
        match_obj = re.match(regex, url)
        stripped_url = match_obj.group('target')

    except re.error: 
        strip_url = None
        print ("f: url_hanlder\nf():strip_url\n\tregex error")
        stripped_url = ERROR_STRING
    except: stripped_url = ERROR_STRING

    return stripped_url

def get_url_base(url):
    """ strip url prefix and tail, return url domain up to first / """

    global ERROR_STRING

    stripped_url = strip_url_prefix(url)
    try :
        stripped_url = stripped_url.split('/')
        stripped_url = stripped_url[0]
    except: 
        stripped_url = ERROR_STRING
        print ("f: url_hanlder\nf():get_url_base\n\texception thrown")

    return stripped_url
