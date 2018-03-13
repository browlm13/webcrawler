#!/usr/bin/env python

__author__ 	= "L.J. Brown"
__version__ = "1.0.1"

from urllib.parse import urljoin
import os
import logging
import json
import glob

#my lib
from data_structures import data_structures as ds
from utils import access_page
from utils import text_processing


# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# cache for storing url refrences (save url map)
def get_url_alternates(url):
	""" Expands url to list of url and its alternates"""
	url_alternates = [url]
	redirect_link = access_page.resolve_url(url)
	if redirect_link and redirect_link != url:
		url_alternates.append(redirect_link)
	return url_alternates

# create url alternates map that resolves all alternates to last element of resolve
def create_url_alternates_map(url_list, url_alternates_map={}):
	for url in url_list:
		if url not in url_alternates_map:
			url_alternates = get_url_alternates(url)
			reslove_url = url_alternates[-1]			# always resolve to last value
			for a in url_alternates:
				url_alternates_map[a] = reslove_url
	return url_alternates_map

def collapse_url_alternates(urls, url_alternates_map={}):
	""" Takes list of urls some or all of which can have alternates present, returns one representive url for each """

	# create or update map
	url_alternates_map = create_url_alternates_map(urls, url_alternates_map)

	# map
	mapped_urls = [url_alternates_map[url] for url in urls]

	# collapse and return
	return list(set(mapped_urls))

def is_suburl(url, parent_url, url_alternates_map={}):

	# create or update map
	url_alternates_map = create_url_alternates_map([url,parent_url], url_alternates_map)

	# map urls
	parent_url = url_alternates_map[parent_url]
	url = url_alternates_map[url]

	# find common path
	common_path = os.path.commonprefix([parent_url, url])

	if common_path == parent_url:
		return True
	return False

#
#	output file name mthods
#
def document_directory_path(output_directory, url_id):
	# document directory
	directory_name = "doc_%s" % str(url_id)
	directory_path = os.path.join(output_directory, directory_name)
	return directory_path

# URL meta data file name
def url_meta_data_file_path(output_directory, url_id):
	directory_path = document_directory_path(output_directory, url_id)
	filename = "url_meta_data_%s.json" % str(url_id)
	return os.path.join(directory_path, filename)
	
# Document ('tokens')file name
def document_file_path(output_directory, url_id):
	directory_path = document_directory_path(output_directory, url_id)
	filename = "tokens_%s.json" % str(url_id)
	return os.path.join(directory_path, filename)


# give stopwords
class Crawler():

	def __init__(self):
		self.site_graph = {}
		self.queue = ds.Queue()
		self.url_alternates_map = {}
		self.url_id_map = ds.DoubleDict()

	def filter_urls(self, urls):

		# update url_alternates_map
		self.url_alternates_map = create_url_alternates_map(urls, self.url_alternates_map)

		# map urls
		accepted_urls = list(set([self.url_alternates_map[url] for url in urls]))

		# excluded_urls
		excluded_urls = set()

		#
		# remove urls not within seed urls scope
		#

		for url in accepted_urls:
			if not is_suburl(url, self.seed_url):
				excluded_urls.add(url)
				logger.info("Out Of Bounds: %s" % url)

		#
		# remove urls not permitted by robot.txt
		#

		for url in accepted_urls:
			for furl in self.forbidden_urls:
				if is_suburl(url, furl):
					excluded_urls.add(url)
					logger.info("Access Not Permitted Robots.txt: %s" % url)

		#
		#	remove urls already in index (site_graph)
		#

		indexed_urls = [k for k,v in self.site_graph.items()]

		# add to map (shouldn't have to)
		self.url_alternates_map = create_url_alternates_map(indexed_urls, self.url_alternates_map)
		
		# map
		indexed_urls = [self.url_alternates_map[iurl] for iurl in indexed_urls]

		for url in accepted_urls:
			if url in indexed_urls:
				excluded_urls.add(url)

		#
		#	remove urls already in queue 
		#

		queued_urls = self.queue.to_list()

		# add to map
		self.url_alternates_map = create_url_alternates_map(queued_urls, self.url_alternates_map)
		
		# map
		queued_urls = [self.url_alternates_map[qurl] for qurl in queued_urls]

		for url in accepted_urls:
			if url in queued_urls:
				excluded_urls.add(url)

		# remove excluded urls
		accepted_urls = set(accepted_urls).difference(excluded_urls)

		# return unique accepted urls
		return list(accepted_urls)

	def read_robots(self):

		# create or update map
		#self.url_alternates_map = create_url_alternates_map([self.seed_url], self.url_alternates_map)

		# map url
		#seed_url = self.url_alternates_map[self.seed_url]

		# find forbidden urls
		self.forbidden_urls = []

		# get the robots.txt url for the seed url
		robots_url = self.seed_url + "robots.txt"

		# extract the forbidden routes
		page_data = access_page.get_page_data(robots_url)
		if page_data['plain_text'] is not None:
			for line in page_data['plain_text'].split("\n"):
				if line.startswith('Disallow'): 
					forbidden = line.split(':')[1].strip()

					if forbidden[0] == '/':
						forbidden = forbidden[1:]

					seed_url = self.seed_url
					if self.seed_url[-1] == '/':
						seed_url = self.seed_url[:-1]

					# add site prefix
					self.forbidden_urls.append(seed_url + '/' + forbidden)
	
	def keep_indexing(self):

		# stop if url queue is empty
		if len(self.queue) == 0: 
			return False

		# stop if max_urls_to_index param has been reached
		if self.max_urls_to_index is not None:
			return len(self.site_graph) < self.max_urls_to_index

		return True

	def document_directory_path(self, url_id):
		# document directory
		directory_name = "doc_%d" % url_id
		directory_path = os.path.join(self.output_directory, directory_name)
		return directory_path

	# URL meta data (page_data w/out 'plain_text', add url_id)
	def save_url_meta_data(self, url_meta_data):

		logger.info("Saving URL Meta Data...")

		# document directory
		directory_path = document_directory_path(self.output_directory, url_meta_data['url_id']) #self.document_directory_path(url_meta_data['url_id'])

		# if output directory does not exist, create it
		if not os.path.exists(directory_path): 
			os.makedirs(directory_path)

		#
		# save url meta data file
		#

		filepath = url_meta_data_file_path(self.output_directory, url_meta_data['url_id'])

		with open(filepath, 'w') as file:
			file.write(json.dumps(url_meta_data))


		logger.info("Saved URL Meta Data.")


	# Document ('tokens')
	def save_document(self, tokens, url_id):

		logger.info("Saving Document ('Tokens')...")

		# document directory
		directory_path = document_directory_path(self.output_directory, url_id) #self.document_directory_path(url_id)

		# if output directory does not exist, create it
		if not os.path.exists(directory_path): 
			os.makedirs(directory_path)

		#
		# save document ('tokens') file
		#

		filepath = document_file_path(self.output_directory, url_id)

		with open(filepath, 'w') as file:
			file.write(json.dumps(tokens))

		logger.info("Saved Document ('Tokens').")


	def crawl_site(self, seed_url, output_directory, max_urls_to_index=None, stopwords_file=None):

		self.output_directory = output_directory
		self.max_urls_to_index = max_urls_to_index
		self.stopwords_file = stopwords_file

		# resolve seed url
		self.url_alternates_map = create_url_alternates_map([seed_url], self.url_alternates_map)
		self.seed_url = self.url_alternates_map[seed_url]

		# set forbidden_urls
		self.read_robots()

		# add seed url to queue
		self.queue.add(self.seed_url)

		# log info
		logger.info("Begining Site Crawl: %s" % self.seed_url)
		if self.max_urls_to_index is not None:	logger.info("Number of Sites to Index: %d" % self.max_urls_to_index)
		else:	logger.info("Index Forever")


		while self.keep_indexing():

			#
			#	Crawl Next Site In Queue
			#

			# log info
			logger.info("\nCrawling URL Number: %d" % len(self.site_graph))

			# remove url from queue and get page data
			target_url = self.queue.remove()
			page_data = access_page.get_page_data(target_url)

			# log info
			logger.info("Crawled: %s" % target_url)
			logger.info("\tContent Type: %s" % page_data['content_type'])
			logger.info("\tBroken: %s" % page_data['broken'])

			# update map with new links
			self.url_alternates_map = create_url_alternates_map(page_data['absolute_out_links'], self.url_alternates_map)

			# map absolute_out_links
			page_data['absolute_out_links'] = list(set([self.url_alternates_map[aol] for aol in page_data['absolute_out_links']]))

			#
			#	Update Graph And Save:
			#			* URL meta data (page_data w/out 'plain_text', add url_id)
			#			* Document ('tokens')

			assert target_url not in self.site_graph

			# assign url "unique" id
			url_id = len(self.site_graph)
			self.url_id_map[target_url] = url_id

			### 	URL meta data (page_data w/out 'plain_text', add url_id, add seed_url, mapped_url)

			# create url meta data
			url_meta_data = {k:v for k,v in page_data.items() if k != 'plain_text' }
			url_meta_data['url_id'] = url_id
			url_meta_data['seed_url'] = self.seed_url
			url_meta_data['mapped_url'] = target_url

			# save URL meta data
			self.save_url_meta_data(url_meta_data)

			# add url_meta_data to graph 
			self.site_graph[target_url] = url_meta_data

			### 	Document ('tokens')

			# create Document ('tokens')
			tokens = ""
			if page_data['plain_text'] is not None:
				tokens = text_processing.plain_text_to_tokens(page_data['plain_text'], self.stopwords_file)

			# save Document ('tokens')
			self.save_document(tokens, url_id)

			#
			#	Add New Urls To Queue And Continue Crawling
			#

			# filter new found urls and add to queue
			new_urls = self.filter_urls(page_data['absolute_out_links'])
			logger.info("Adding New URLs to Queue:")
			if len(new_urls) > 0:
				for u in new_urls:
					logger.info("\t\t- %s" % u)
					self.queue.add(u)

		# log info
		logger.info("Finished Site Crawl: %s" % self.seed_url)


		# save url id dictonary!?


def build_site_graph(crawler_output_directory):

	# url meta data list
	site_graph = []

	glob_phrase = document_directory_path(crawler_output_directory,'*')

	for path in glob.glob(glob_phrase):
		directory = os.path.split(path)[1]
		url_id = int(directory.split('_')[-1])
		
		url_meta_data = {}
		umd_file_path = url_meta_data_file_path(crawler_output_directory, url_id)

		with open(umd_file_path) as json_data:
			umd = json.load(json_data)
		site_graph.append(umd)

	return site_graph

def build_url_id_map(crawler_output_directory):
	site_graph = build_site_graph(crawler_output_directory)

	url_id_map = ds.DoubleDict()
	for umd in site_graph:
		url = umd['mapped_url']
		doc_id = umd['url_id']
		url_id_map[doc_id] = url
	return url_id_map


if __name__ == '__main__':

	SEED_URL = "http://lyle.smu.edu/~fmoore/"
	MAX_URLS_TO_INDEX = None
	STOPWORDS_FILE = "stopwords.txt"
	OUTPUT_DIRECTORY = "output2"

	#
	# 	Crawl
	#

	#c = Crawler()
	#c.crawl_site(SEED_URL, OUTPUT_DIRECTORY, MAX_URLS_TO_INDEX, STOPWORDS_FILE)

	#
	#	display Url Meta Data
	#


	site_graph = build_site_graph(OUTPUT_DIRECTORY)
	url_id_map = build_url_id_map(OUTPUT_DIRECTORY)
	

	for umd in site_graph:
		doc_id = umd['url_id']
		url = umd['mapped_url']
		seed_url = umd['seed_url']
		non_image_links = umd['absolute_out_links']
		image_links = umd['absolute_image_links']
		document_hash = umd['document_hash']

		# duplicates
		url_ids_with_duplicate_content = []
		for umd2 in site_graph:
			if (umd2['document_hash'] == document_hash) and (umd2['url_id'] is not doc_id):
				url_ids_with_duplicate_content.append(umd2['url_id'])

		print(doc_id)
		print(url)
		print("Broken: %s" % umd['broken'])

		print("duplicates:")
		print(url_ids_with_duplicate_content)

	
		print("image links:")
		print(image_links)

		internal_links = []
		outbound_links = []
		for l in non_image_links:
			if is_suburl(l, seed_url):
				internal_links.append(l)
			else: 
				outbound_links.append(l)
		print("internal links:")
		print(internal_links)
		print("outbound_links:")
		print(outbound_links)
		print("\n\n")



		

	# for each page
	#	report title
	# 	report all 'inbounds' links
	#	report all outgoing (out of bounds)

	# report all broken
	# read all type : "content_type": ... (gif, jpg, jpeg, png)
	# report all duplicate documents
	# create term document frequency matrix
	# list 20 most common words

"""

	#
	#	term frequency matrix
	#

	input:
		-Seed websites (add to queue)
		-N number of pages to index

"""
