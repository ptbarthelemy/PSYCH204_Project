from random import choice, seed
import pydot
from state import State


class Regex:
	def __init__(self, str=None):
		self.states_ = dict()
		self.lastStateID_ = -1
		self.start_ = None
		if str:
			self.stringIs(str)

	def stateIs(self, state):
		self.lastStateID_ = self.lastStateID_ + 1
		self.states_[self.lastStateID_] = state
		state.ID_ = self.lastStateID_

	def stateRemove(self, state):
		assert state.ID_ != self.start_.ID_

		# remove from next values
		for k, s in state.next_.items():
			# print "Removing", state.ID_, "from", list(s.ID_ for s in s.prev_[k]), "with key", k
			state.nextRemove(k)

		# remove from prev values
		for k, sSet in state.prev_.items():
			for s in sSet:
				s.nextRemove(k)

		# remove from map
		if self.states_.get(state.ID_, None) is not None:
			del self.states_[state.ID_]

	def state(self, ID):
		return self.states_.get(ID, None)

	def stringIs(self, str):
		if self.start_ == None:		
			self.start_ = State(self, True)
			# self.stateIs(self.start_)
		lastState = self.start_
		for a in str:
			nextState = State(self)
			lastState.nextIs(a, nextState)
			lastState = nextState
		lastState.accept_ = True

	def string(self, str):
		state = self.start_
		while len(str) != 0:
			state = state.next(str[0])
			str = str[1:]
			if state is None:
				return False
		return state.accept_

	def copyRegex(self):
		copy = Regex(None)

		# add all of the nodes
		for ID, s in self.states_.items():
			newState = State(self)
			newState.accept_ = s.accept_
			newState.ID_ = ID
			copy.states_[ID] = newState

		# add all of the edges
		for ID, s1 in self.states_.items():
			for k, s2 in s1.next_.items():
				copy.states_[ID].nextIs(k, copy.states_[s2.ID_])

		# set the start node
		copy.lastStateID_ = self.lastStateID_
		copy.start = copy.states_[self.start_.ID_]

		return copy

	def merge(self, ID1=None, ID2=None):
		# return if only one state remains
		if len(self.states_) == 1:
			return
		if ID1 is None or ID2 is None:
			ID1 = choice(self.states_.keys())
			ID2 = choice(list(a for a in self.states_.keys() if a != ID1))
		print "Merging states", ID1, "and", ID2
		self.states_[ID1].merge(self.states_[ID2])

	def wildcardize(self):
		for s1 in self.states_.values():
			s1.wildcardize()

	def printText(self):
		print "All states:", self.states_.keys()
		for state in self.states_.values():
			print state.ID_, "accept:", state.accept_
			print "  reached from:", dict((k, list(s.ID_ for s in sSet))
				for k, sSet in state.prev_.items())
			if len(state.next_) > 0:
				print "  leads to:", dict((k, s.ID_) for k, s in state.next_.items())

	def printGraph(self, filename):
		graph = pydot.Dot(graph_type='digraph')

		# identify nodes and add to graph
		nodes = dict()
		for ID in self.states_.keys():
			if self.states_[ID].accept_:
				nodes[ID] = pydot.Node("%d"%ID, style="filled", fillcolor="grey")
			else:
				nodes[ID] = pydot.Node("%d"%ID)
			graph.add_node(nodes[ID])

		# identify edges
		edges = dict()
		for s1ID, s1 in self.states_.items():
			edges[s1ID] = dict()
			for k, s2 in s1.next_.items():
				if edges[s1ID].get(s2.ID_, None) == None:
					edges[s1ID][s2.ID_] = k
				else:
					edges[s1ID][s2.ID_] += k

		# add edges to graph
		for s1ID in edges.keys():
			for s2ID in edges[s1ID].keys():
				edge = pydot.Edge("%d"% s1ID, "%d"% s2ID, label=edges[s1ID][s2ID])
				graph.add_edge(edge)

		# display graph
		graph.write_png(filename)

if __name__ == '__main__':
	seed(7)
	re = Regex("testa")
	re.stringIs("bSsa")
	# re.stringIs("bootcamp")

	re.printGraph("output/merge0.png")	
	for i in range(len(re.states_)):
		re.merge()
		print "*** Loop stage", (1 + i)
		re.printText()
		re.printGraph("output/merge%d.png"%(1 + i))

	# re = Regex("aba")
	# re.printGraph("output/before.png")
	# re.stringIs("abba")
	# re.printGraph("output/before.png")
	# # re.merge(1,3)
	# #re.wildcardize()
	# re.printGraph("output/after.png")

