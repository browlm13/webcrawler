import json

#
#   use:
#           idd = ID_Dict()
#           idd.add('value0')
#
class ID_Dict(dict):
    """ Dictonary subclass where values are determend by a running count. """

    def __init__(self, start_ID=0):
        self.cur_id = start_ID

    def add(self, key):
        """ Store key with Current ID as value, Then increment ID  """
        assert key not in self
        dict.__setitem__(self, key, self.cur_id)
        self.cur_id += 1

    def get_map(self):
        return self

    def get_inverse_map(self):
        return {v:k for k,v in self.items()}

    def save(self, file_path):
        with open(file_path, 'w') as file:
            file.write(json.dumps(self.get_map()))

    def load(self, file_path):
        with open(file_path) as json_data:
            dict.clear(self)
            self.update(json.load(json_data))
            self.cur_id = max(self.values()) + 1

#
#   use:
#           s = Seen()
#           s.add('value0')
#           'value0' in s
class Seen():
    """ Simply for keeping track of items you've already seen, fast implimentation using python dictonary"""
    def __init__(self):
        self.index = {}

    def add(self, item):
        self.index[item] = True

    def remove(self, item):
        del self.index[item]

    def __contains__(self, item):
        if item in self.index: return True
        return False

    def __str__(self):
        return str(self.index)

class URL_Frontier():
    """ A queue data structure that ignores added duplicates"""

    def __init__(self):
        self.q = Queue()

    def add(self, data):
        if data not in self.q:
            self.q.add(data)

    def add_list(self, list):
        for d in list:
            self.add(d)

    def remove(self):
        return self.q.remove()

    def __len__(self):
        return len(self.q)

    def __contains__(self, item):
        return item in self.q

    def to_list(self):
        return self.q.to_list()

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
        :param data: Data (any type) to add to the tail of queue.
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
        if self.head is not None:
            n = self.head
            self.head = n['next']
            return n['data']
        return None

    def __len__(self):
        count = 0
        cur = self.head
        while cur is not None:
            cur = cur['next']
            count +=1
        return count

    def __contains__(self, key):
        in_queue = False
        cur = self.head
        while cur is not None:
            if cur['data'] == key:
                in_queue = True
            cur = cur['next']
        return in_queue

    def to_list(self):
        queue_list = []
        cur = self.head
        while cur is not None:
            queue_list.append(cur['data'])
            cur = cur['next']
        return queue_list