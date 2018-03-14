url1 = "http://lyle.smu.edu/~fmoore"
url2 = 'https://s2.smu.edu/~fmoore/'
url3 = "https://s2.smu.edu/~fmoore/CSE5337_syllabus.pdf"
url4 = "https://s2.smu.edu/~fmoore/dontgohere/stopwords.txt"
url = url4

SEED_URL = "http://lyle.smu.edu/~fmoore/"  # "https://s2.smu.edu/~fmoore/dontgohere/wordlist.txt"
MAX_URLS_TO_INDEX = None
STOPWORDS_FILE = "stopwords.txt"
OUTPUT_DIRECTORY = "fmore"

from src import crawler

c = crawler.Crawler()
c.crawl_site(SEED_URL, OUTPUT_DIRECTORY, MAX_URLS_TO_INDEX, STOPWORDS_FILE)
