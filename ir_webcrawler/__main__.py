url1 = "http://lyle.smu.edu/~fmoore"
url2 = 'https://s2.smu.edu/~fmoore/'
url3 = "https://s2.smu.edu/~fmoore/CSE5337_syllabus.pdf"
url4 = "https://s2.smu.edu/~fmoore/dontgohere/stopwords.txt"
url = url4


from src import crawler

SEED_URL = "http://lyle.smu.edu/~fmoore/"  # "https://s2.smu.edu/~fmoore/dontgohere/wordlist.txt"
MAX_URLS_TO_INDEX = None
STOPWORDS_FILE = "stopwords.txt"
OUTPUT_DIRECTORY = "fmore"

c = crawler.Crawler()
c.crawl_site(SEED_URL, OUTPUT_DIRECTORY, MAX_URLS_TO_INDEX, STOPWORDS_FILE)


from src import file_io_handler

#file_io_handler.load_directory_structure()
"""
from src import data_structures as ds

url_id = ds.ID_Dict()
indexed_document_hashes = ds.Seen()

from src import url_resolution as url_resolution

url_resolver = url_resolution.URL_Resolver()

from src import url_accessor

ua = url_accessor.get_response_summary(url, url_resolver)
brc = ua['binary_response_content']

from src import file_parser
fp = file_parser.File_Parser()
plain_text = fp.extract_plain_text(brc, ua['content_type'])

from src import text_processing

tokens = text_processing.plain_text_to_tokens(plain_text)

from src import filter_urls

print(filter_urls.is_sub_url("https://s2.smu.edu/", 'https://s2.smu.edu/~fmoore/', url_resolver))
print(filter_urls.is_sub_url("https://s2.smu.edu/", 'https://s2.smu.edu/~fmoore/'))
"""