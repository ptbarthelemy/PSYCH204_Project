from random import choice, seed
import pydot
from state import State

DEBUG = False

class Regex:
	def __init__(self, str=None):
		self.mergeQueue_ = list()
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
		for k, s in state.next_:
			state.nextRemove(k, s)

		# remove from prev values
		for k, s in state.prev_:
			s.nextRemove(k, state)

		# remove from map
		if self.states_.get(state.ID_, None) is not None:
			del self.states_[state.ID_]

	def state(self, ID):
		return self.states_.get(ID, None)

	def stringIs(self, str):
		if self.start_ == None:		
			self.start_ = State(self, True)
		lastState = self.start_
		for a in str:
			nextState = State(self)
			lastState = lastState.nextIs(a, nextState)
			# nextState = State(self)
			# lastState.nextIs(a, nextState)
			# lastState = nextState
		lastState.accept_ = True

		if DEBUG: print "need to merge", list((s1.ID_, s2.ID_) for s1, s2 in self.mergeQueue_)
		while len(self.mergeQueue_) > 0:
			s1, s2 = self.mergeQueue_.pop(0)
			s1.merge(s2)

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
		if DEBUG: print "Merging states", ID1, "and", ID2
		self.states_[ID1].merge(self.states_[ID2])
		
		while len(self.mergeQueue_) > 0:
			s1, s2 = self.mergeQueue_.pop(0)
			s1.merge(s2)

	def wildcardize(self):
		for s1 in self.states_.values():
			s1.wildcardize()

	def printText(self):
		print "All states:", self.states_.keys()
		for state in self.states_.values():
			print state.ID_, "accept:", state.accept_
			print "  reached from:", list((k, s.ID_)
				for k, s in state.prev_)
			if len(state.next_) > 0:
				print "  leads to:", list((k, s.ID_)
					for k, s in state.next_)

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
			for k, s2 in s1.next_:
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
	# # test 1: should end in the Kleene star
	# re = Regex("abc")
	# re.stringIs("sS")
	# re.printGraph("output/test1-1.png")
	# print "\n***about to add S"
	# re.stringIs("S")
	# re.printGraph("output/test1-2.png")
	# re.merge(0, 3)
	# re.printGraph("output/test1-3.png")
	# re.merge(0, 5)
	# re.printGraph("output/test1-4.png")

	# # test 2: should create the following cleanly (without orphans)
	# seed(7)
	# re = Regex("testa")
	# re.stringIs("tesSa")
	# re.stringIs("bootcamp")
	# re.printGraph("output/merge0.png")
	# for i in range(len(re.states_)):
	# 	re.merge()
	# 	print "*** Loop stage", (1 + i)
	# 	re.printText()
	# 	re.printGraph("output/merge%d.png"%(1 + i))

	# # test 3: should be Kleene star by merge9
	# seed(5)
	# re = Regex("testa")
	# re.stringIs("tesSa")
	# re.stringIs("bootcamp")
	# re.printGraph("output/merge-0.png")
	# for i in range(len(re.states_)):
	# 	re.merge()
	# 	print "\n*** Loop stage", (1 + i)
	# 	re.printText()
	# 	re.printGraph("output/merge-%d.png"%(1 + i))

	# test 4: should be Kleene star by merge9

	# test 5: try out wildcards
	seed()
	re = Regex("testa")
	re.stringIs("tesSa")
	re.stringIs("bootcamp")
	re.printGraph("output/merge0.png")
	for i in range(len(re.states_)):
		re.wildcardize()
		print "\n*** Loop stage", (1 + i)
		re.printText()
		re.printGraph("output/merge%d.png"%(1 + i))
