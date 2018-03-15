
"""
    -URL Resolver
    -Indexed Resolved URL : ID
    -Indexed Document Hash : ID
    -URL Filter
    -URL Frontier
    ------------------------

    -URL Filter
        -Resolve URLs
        -Site Bounds
        -Robot.txt
        -Indexed URLs

    -------------------------

    ## Site Bounds / Robot.txt - ip like mask opearator if ur feeling it

    -------------------------

    URL Resolver

    -Resolve URLS as they enter first stage of filers
    -Resolve URLS before writing to webpage_summary file

    * persistant dictonary to minimize network resolves

    -----------------------------

    Indexed Resolved URL : ID

    -when writing webpage summary to a file add the URL ID value to the Indexed Resolved URL : ID Map

    Indexed Document Hash : ID

    -when writing document tokens to file add the document hash to the Indexed Document Hash : ID

    -----------------------------

    Robots True/False function (*2)

    -----------------------------

    In/Out of Bounds function   (*3)

    -----------------------------


# mock 1 - one site at a time, no pdfs
------------
Base Station
------------

URL Filter - (web page summary urls from crawler) : (filtered resolved normalized web page summary urls from crawler)

    XXX- Resolves URLs -> URL Resolver Running Cache/Dict for speed increase (collapses)
    - Removes Web Pages/Resolved URLs already indexed (*1)
    - Removes Disallowed By "robots.txt" (*2)
    - Removes Out of Bounds of seed site (*3)

Indexer -

    - Can inform (crawler) if Document has already been indexed
    - Can inform (filter) if Web Page/Resolved URL has already been indexed (*1)
    - Writing Documents / Updating Indexed Document Hash : ID
        - Writes only if Document has not yet been indexed
    - Writing Web Page Summaries / Indexed Resolved URL : ID
         - Resolves Web Page Summary URL's before writing -> URL Resolver Running Cache/Dict for speed increase (collapses)

URL Frontier -
---------------


base_station.next_url() : string, url
base_station.duplicate_document(document_hash) : boolean
base_station.report_web_page_summary(web_page_summary)              # ("requested_url", "redirect_history", "status_code", "content_type", "document_hash", "normalized_a_hrefs", 'normalized_img_srcs'
base_station.report_token_frequency_matrix(token_frequency_matrix)

------------


index urls by content
'requested_url', "redirect_history",
-----------

class Craler()

    def __init__(self):
        self.base_station = base_station

"""

from src import utils
from src import file_parser
from src import webpage_accessor

url ="https://s2.smu.edu/~fmoore/"
#url = "https://s2.smu.edu/~fmoore/dontgohere/"
#url = "https://s2.smu.edu/~fmoore/dontgohere/badfile2.htm"
#url = "http://lyle.smu.edu/~fmoore/index-fall2017.htm"
#url = "http://lyle.smu.edu/~fmoore/index-final.htm"
#url = "http://lyle.smu.edu/~fmoore/syl_7330.pdf" # not found
#url = "http://lyle.smu.edu/~fmoore/timeline.pdf" # notworking but looks like works in browser
#url = "https://s2.smu.edu/~fmoore/CSE5337_syllabus.pdf"
#url = "http://lyle.smu.edu"
#url = "https://s2.smu.edu/~fmoore/dontgohere/stopwords.txt"
#url = "https://s2.smu.edu/~fmoore/dontgohere/bayes.js"
#url = "https://s2.smu.edu/~fmoore/dontgohere/wordlist.txt"
#url = "http://lyle.smu.edu/~fmoore"

SEED_URL = url

url_resolver = utils.URL_Resolver()
resolved_url = url_resolver.resolve(SEED_URL)

feilds = ("tokens", "requested_url", "status_code", "content_type")
#summary = webpage_accessor.pull_summary(resolved_url, feilds)
#print(summary)
