#!/usr/bin/env python

__author__ 	= "L.J. Brown"
__version__ = "1.0.1"

from urllib.parse import urljoin
import os
import logging

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

# give stopwords
class Crawler():

	def __init__(self):
		self.site_graph = {}
		self.queue = ds.Queue()
		self.url_alternates_map = {}

	def filter_urls(self, urls):

		# update url_alternates_map
		self.url_alternates_map = create_url_alternates_map(urls, self.url_alternates_map)

		# map urls
		accepted_urls = list(set([self.url_alternates_map[url] for url in urls]))

		#
		# remove urls not within seed urls scope
		#

		for url in accepted_urls:
			if not is_suburl(url, self.seed_url):
				accepted_urls.remove(url)

				logger.info("Out Of Bounds: %s" % url)

		#
		# remove urls not permitted by robot.txt
		#

		for url in accepted_urls:
			for furl in self.forbidden_urls:
				if is_suburl(url, furl):
					accepted_urls.remove(url)

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
				accepted_urls.remove(url)

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
				accepted_urls.remove(url)

		# return unique accepted urls
		return list(set(accepted_urls))

	def read_robots(self):

		# create or update map
		self.url_alternates_map = create_url_alternates_map([self.seed_url], self.url_alternates_map)

		# map url
		seed_url = self.url_alternates_map[self.seed_url]

		# find forbidden urls
		self.forbidden_urls = []

		# get the robots.txt url for the seed url
		robots_url = urljoin(seed_url, "robots.txt")

		# extract the forbidden routes
		page_data = access_page.get_page_data(robots_url)
		if page_data['plain_text'] is not None:
			for line in page_data['plain_text'].split("\n"):
				if line.startswith('Disallow'): 
					forbidden = line.split(':')[1].strip()

					# add site prefix
					self.forbidden_urls.append(urljoin(seed_url,forbidden))
	

	def keep_indexing(self):

		# stop if url queue is empty
		if len(self.queue) == 0: 
			return False

		# stop if max_urls_to_index param has been reached
		if self.max_urls_to_index is not None:
			return len(self.site_graph) < self.max_urls_to_index

		return True

	def crawl_site(self, seed_url, max_urls_to_index=None, stopwords_file=None):

		self.seed_url = seed_url
		self.max_urls_to_index = max_urls_to_index
		self.stopwords_file = stopwords_file

		# set forbidden_urls
		self.read_robots()

		# add seed url to queue
		self.queue.add(seed_url)

		# log info
		logger.info("Begining Site Crawl: %s" % seed_url)
		if self.max_urls_to_index is not None:	logger.info("Number of Sites to Index: %d" % self.max_urls_to_index)
		else:	logger.info("Index Forever")

		# for log info
		count = 1
		while self.keep_indexing():

			# log info
			logger.info("\nCrawling Site Number: %d" % count)

			# remove url from queue and get page data
			target_url = self.queue.remove()
			page_data = access_page.get_page_data(target_url)

			# log info
			logger.info("Crawled: %s" % target_url)
			logger.info("\tContent Type: %s" % page_data['content_type'])
			logger.info("\tBroken: %s" % page_data['broken'])

			# add page data to graph
			assert target_url not in self.site_graph
			self.site_graph[target_url] = page_data

			# filter new found urls and add to queue
			new_urls = self.filter_urls(page_data['absolute_out_links'])
			logger.info("Adding New URLs to Queue:")
			if len(new_urls) > 0:
				for u in new_urls:
					logger.info("\t\t- %s" % u)
					self.queue.add(u)

			# for log info
			count += 1

		# log info
		logger.info("Finished Site Crawl: %s" % self.seed_url)

		#
		#	term frequency matrix
		#


		# tmp print
		print("\n\n")

		for url,val in self.site_graph.items():
			print(url) 
			print(val['broken'])
			print(val['content_type'])
			print(val['document_hash'])
			#
			# tokenize plain text if applicable
			#
			if val['plain_text'] is not None:
				val['tokens'] = text_processing.plain_text_to_tokens(val['plain_text'], self.stopwords_file)

				print(val['tokens'])

if __name__ == '__main__':

	SEED_URL = "http://lyle.smu.edu/~fmoore/"
	MAX_URLS_TO_INDEX = 3
	STOPWORDS_FILE = "stopwords.txt"
	c = Crawler()
	c.crawl_site(SEED_URL, MAX_URLS_TO_INDEX, STOPWORDS_FILE)
