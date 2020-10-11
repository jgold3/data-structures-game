""" Handles AVL tree state """

import re
from .avl import TreeNode
from .avl import AVLTree
from random import seed
from random import randint
seed(42)  # fixed seed for debugging


def tryint(s):
	try:
		return int(s)
	except ValueError:
		return s
		
def alphanum_key(s):
	""" Turn string into a list of strings and numbers 
	
	"node20test" --> ["node", 20, "test"]
	"""
	return [tryint(c) for c in re.split('([0-9]+)', s)]

class AVLHandler(object):
	
	
	def __init__(self):
		
		self.root = None
		self.tree = None
		
	@classmethod
	def from_scratch(cls, expected_height, point_cap):	
		
		handler = cls()
		handler.uid = 0
		handler.golden_id = None  # id of golden node
		handler.balanced = True  # currently balancing is done in tandem when insert/remove is called
		handler.point_cap = point_cap
		handler.expected_height = expected_height
		handler.__generate_board()  # generate new game board at runtime
		return handler
	
	
	@classmethod
	def from_graph(cls, graph):
		
		handler = cls()
		handler.uid = tryint(graph['uid'])
		handler.golden_id = tryint(graph['gold_node'][4:])  # remove 'node' from id
		handler.balanced = graph['balanced']
		handler.__parse_graph(graph)  # deserialize graph
		return handler
		
	
	def __generate_board(self):
		""" generate game board if it doesnt exists """
		if self.tree:
			return
			
		self.tree = AVLTree()
		self.addNewNode(randint(0, self.point_cap))	
		while(self.root.height < self.expected_height):
			self.addNewNode(randint(0, self.point_cap))	
		
		self.golden_id = randint(0, self.uid - 1) # randomly choose golden node
		if(self.root.nid == self.golden_id):
			self.golden_id = self.root.left.nid
			
			
	def __parse_graph(self, graph):
		""" deseralize tree from existing tree graph """
		if self.tree:
			return
		
		self.tree = AVLTree()
		insertion_dict = {}
		nids = graph['adjacency_list']
		keys = graph['node_points']
		
		for i in nids:
			i_int = i[4:]
			if i_int not in insertion_dict:
				insertion_dict[i_int] = keys[i]
			
			if len(nids[i]) > 0:  # node has children
				for k in nids[i]:
					k_int = k[4:]
					if k_int not in insertion_dict:
						insertion_dict[k_int] = keys[k]
		
		# ~ for nid in insertion_dict:
			# ~ print(f'nid: {nid}, entry: {insertion_dict[nid]}')
		for nid in sorted(insertion_dict, key=alphanum_key):
			self.addNode(tryint(insertion_dict[nid]), tryint(nid)) 

	
	# ~ def __parse_graph_helper(self, entry): 
		# ~ """ turn inner node dict into a key and insertion dict """
		
		# ~ nid = entry['nid'][4:]  # strip 'node' from id
		# ~ out = {'key': entry['key'], 'val': entry['val']}
		# ~ return nid, out
		
	
	def addNewNode(self, key, b=True):
		""" add node to tree by value """
		self.root = self.tree.insert_node(self.root, key, self.uid, balance=b)
		self.balanced = self.tree.isBalanced(self.root)
		self.uid += 1
	
		
	def addNode(self, key, nid, b=True):
		""" add node to tree by value """
		self.root = self.tree.insert_node(self.root, key, nid, balance=b)
		self.balanced = self.tree.isBalanced(self.root)
		
	def delNode(self, key, b=True):
		""" remove node from tree by value """
		self.root = self.tree.delete_node(self.root, key, balance=b)
		self.balanced = self.tree.isBalanced(self.root)
		
		
	def delNodeByID(self, nid, b=True):
		""" remove node from tree by value """
		self.root = self.tree.delete_node_id(self.root, nid, balance=b)
		self.balanced = self.tree.isBalanced(self.root)		
			
		
	def get_gamestate(self):
		""" return dictionary with the gamestate """
		out_dict = {}
		out_dict['adjacency_list'] = self.tree.getAdjList(self.root)
		out_dict['node_points'] = self.tree.getKeys(self.root)
		out_dict['gold_node'] = 'node' + str(self.golden_id)
		out_dict['root_node'] = 'node' + str(self.root.nid)
		out_dict['balanced'] = self.balanced
		out_dict['uid'] = self.uid
		return out_dict


	def debug_print(self, use_id=False):
		#print(f"Tree with {self.num_nodes} nodes. . .")
		if use_id:
			self.tree.printIds(self.root, "", True)
		else:
			self.tree.printKeys(self.root, "", True)
		
		
		
##### API Callable Functions #####
def avlNew(height, point_cap, debug=False):
	""" create new avl tree of depth with max point value of point_cap """
	
	handler = AVLHandler.from_scratch(height, point_cap)
	if debug:
		handler.debug_print(use_id=False)
		print('\n\nNow with ids. . .')
		handler.debug_print(use_id=True)
	return handler.get_gamestate()


def avlAction(command, graph, debug=False):
	""" take an action on the tree """
	
	handler = AVLHandler.from_graph(graph)
	c,t = command.split()  # get command and target
	if c == 'Delete':
		nid = tryint(t[4:])
		handler.delNodeByID(nid, b=False)
		if debug:
			print(f'Tried to delete node of id {nid}')
	elif c == 'Insert':
		key = tryint(t)
		handler.addNewNode(key, b=False) 
		if debug:
			print(f'Tried to add new node with key {key}')
	else:
		raise Exception('Invalid command passed to AVL Handler')
	
	if debug:
		handler.debug_print(use_id=False)
		print('\n\nNow with ids. . .')
		handler.debug_print(use_id=True)
	return handler.get_gamestate()
	
	
def avlRebalance(graph, debug=False):
	handler = AVLHandler.from_graph(graph)
	if debug:
		handler.debug_print(use_id=False)
		print('\n\nNow with ids. . .')
		handler.debug_print(use_id=True)
	return handler.get_gamestate()
	""" rebalance graph and return """
	
	
	
	
