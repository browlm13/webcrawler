#!/usr/bin/env python

__author__ 	= "L.J. Brown"
__version__ = "1.0.1"

import hashlib
import requests
from urllib.parse import urljoin
import logging

import PyPDF2 
from io import BytesIO
from bs4 import BeautifulSoup

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def to_absolute_links(base_url, raw_links):
	""" takes in list of raw links both relative and absolute and returns list of absolute links. """
	raw_links = [l for l in raw_links if l is not None]
	absolute_links = [l if l.startswith('http') else urljoin(base_url, l) for l in raw_links]
	return list(absolute_links)

def get_page_data(url):
	""" access a given url and return a python dictonary of page data. """

	page_data = {
		'requested_url' : None,
		'broken' : True,
		'redirection_url' : None,
		'content_type' : None,
		'document_hash' : None,
		'absolute_out_links' : [],
		'absolute_image_links' : [],
		'title' : None,
		'plain_text' : None
	}

	# set 'requested_url' page_data value
	page_data['requested_url'] = url

	try:

		#
		#	make request, continue if status code is 200.
		#
		response = requests.get(url)
		logger.info("Response Status Code: %d" % response.status_code)

		if response.status_code == 200:

			# set 'broken' page_data value to True
			page_data['broken'] = False

			# set 'redirection_url' page_data value
			if response.history:
				page_data['redirection_url'] = response.url

			# set 'content_type' page_data value
			if 'content-type' in response.headers:
				page_data['content_type'] = response.headers['content-type']

			# set 'document_hash' page_data value
			page_data['document_hash'] = str(hashlib.md5(str.encode(response.text)).hexdigest())

			# set base_url for absolute paths
			base_url = page_data['requested_url']
			if page_data['redirection_url'] is not None:
				base_url = page_data['redirection_url']

			#
			# handling diffrent 'content_type''s  
			#	
			#										(.txt, .htm, .html, .php)
			#

			### type "text/html"
			if page_data['content_type'][:9] == "text/html":

				soup = BeautifulSoup(response.text, 'html.parser')

				# set 'title' page_data value
				try:	page_data['title'] = soup.title.string
				except: pass

				# set 'plain_text' page_data value
				page_data['plain_text'] = soup.get_text()

				# set 'absolute_image_links' page_data value
				all_links = [l.get('href') for l in soup.find_all('a')]
				page_data['absolute_out_links'] = to_absolute_links(base_url, all_links)

				# set 'absolute_image_links' page_data value
				all_image_links = [l.get('src') for l in soup.find_all('img', src=True)]
				page_data['absolute_image_links'] = to_absolute_links(base_url, all_image_links)

			### type "application/pdf"
			elif page_data['content_type'] == 'application/pdf':

				pdf = BytesIO(response.content)
				pdfReader = PyPDF2.PdfFileReader(pdf)
				for page_number in range(pdfReader.numPages):
					page = pdfReader.getPage(page_number)

					# set 'plain_text' page_data value
					page_data['plain_text'] = page.extractText()

			### type "text/plain"
			elif page_data['content_type'] == 'text/plain':

				# set 'plain_text' page_data value
				page_data['plain_text'] = response.text

			### type ""


	except:
		logger.error("Requested Page: %s, Failed to read." % page_data['requested_url'])


	return page_data
