from src import crawler

SEED_URL = "http://lyle.smu.edu/~fmoore/"  # "https://s2.smu.edu/~fmoore/dontgohere/wordlist.txt"
MAX_URLS_TO_INDEX = None
STOPWORDS_FILE = "stopwords.txt"
OUTPUT_DIRECTORY = "fmore"

c = crawler.Crawler()
c.crawl_site(SEED_URL, OUTPUT_DIRECTORY, MAX_URLS_TO_INDEX, STOPWORDS_FILE)
