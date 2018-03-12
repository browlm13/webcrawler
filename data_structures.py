#!/usr/bin/env python

__author__ 	= "L.J. Brown"
__version__ = "1.0.1"

class Queue():
	""" 
		This class impliments a minimal queue data structure capable of storing any type of data. 

		use:
			q = Queue()			# create queue
			q.add(data)			# add data to tail of queue
			data = q.remove()	# remove and return data from head of queue
	"""

	def __init__(self):
		self.head, self.tail = None, None
		self.node = lambda data, next: {'data':data, 'next':next}

	def add(self, data):
		"""
		:param add: Data (any type) to add to the tail of queue.
		"""
		n = self.node(data, None)

		if self.head == None:
			self.head, self.tail = n, n

		else:
			self.tail['next'] = n
			self.tail = n

	def remove(self):
		"""
		:returns: Returns and removes data at the head of the queue or None.
		"""
		if self.head != None:
			n = self.head
			self.head = n['next']
			return n['data']
		return None

class DoubleDict(dict):
	def __getitem__(self, key):
		if key not in self:
			inv_dict = {v:k for k,v in self.items()}
			return inv_dict[key]
		return dict.__getitem__(self, key)

	def __delitem__(self, key):
		if key not in self:
			inv_dict = {v:k for k,v in self.items()}
			dict.__delitem__(self, inv_dict[key])
		else:
			dict.__delitem__(self, key)
