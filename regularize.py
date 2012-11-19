from random import choice
import pydot

class State:
	def __init__(self):
		self.prev_ = dict() # maps letter to all predecessors
		self.next_ = dict() # maps letter to single successor
		self.accept_ = False
		self.ID_ = None
		pass

	def next(self, letter):
		return self.next_.get(letter, None)

	def prev(self, letter):
		return self.prev_.get(letter, None)

	def nextIs(self, letter, state):
		self.next_[letter] = state

		if state.prev(letter) is None:
			state.prev_[letter] = [self]
		else:
			state.prev_[letter].append(self)

	def nextNew(self, letter):
		if self.next_.get(letter, None) is None:
			self.nextIs(letter, State())
		return self.next_[letter]


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

	def stateDel(self, state):
		assert state.ID_ != self.start_.ID_

		# remove from next values
		for k, s in state.next_.items():
			s.prev_[k].remove(state)

		# remove from prev values
		for k, sSet in state.prev_.items():
			for s in sSet:
				if s.next_[k].ID_ == state.ID_:
					del self.next_[k]

		# remove from map
		del self.states_[state.ID_]

	def state(self, ID):
		return self.states_.get(ID, None)

	def stringIs(self, str):
		if self.start_ == None:		
			self.start_ = State()
			self.stateIs(self.start_)
		lastState = self.start_
		for a in str:
			lastState = lastState.nextNew(a)
			if lastState.ID_ is None:
				self.stateIs(lastState)
		lastState.accept_ = True

	def string(self, str):
		state = self.start_
		while len(str) != 0:
			state = state.next(str[0])
			str = str[1:]
			if state is None:
				return False
		return state.accept_

	def mergeStates(self, state1, state2):
		# return if merging the same state
		if state1.ID_ == state2.ID_:
			return

		# return if state no longer exists
		if self.state(state1.ID_) == None or \
			self.state(state2.ID_) == None:
			return

		# if one of the states is the start state, make it start1
		if state2.ID_ == self.start_.ID_:
			temp = state1
			state1 = state2
			state2 = temp

		# add outgoing transitions (originally from state2) to state1
		mergeList = list()
		for k, s in state2.next_.items():
			next = state1.next(k)
			if next == None:
				state1.nextIs(k, s)
			# if state1 and state2 have conflicting transitions,
			# merge those states
			elif next != s:
				mergeList.append((next, s))

		# add incoming transitions (originally to state2) to state1
		for k, sSet in state2.prev_.items():
			for s in sSet:
				s.nextIs(k, state1)

		# make accept state if either state is accept
		if state2.accept_:
			state1.accept_ = True

		# delete state2
		self.stateDel(state2)

		# merge remaining items
		for a, b in mergeList:
			self.mergeStates(a, b)

	def copyRegex(self):
		copy = Regex(None)

		# add all of the nodes
		for ID, s in self.states_.items():
			newState = State()
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

	def mergeRandom(self):
		# return if only one state remains
		if len(self.states_) == 1:
			return
		stateList = self.states_.keys()[:]
		ID1 = choice(stateList)
		ID2 = choice(list(a for a in stateList if a != ID1))
		
		print "Merging states", ID1, "and", ID2
		self.mergeStates(self.states_[ID1], self.states_[ID2])

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
	re = Regex("testa")
	re.stringIs("tesha")
	re.stringIs("bootcamp")

	re.printGraph("before.png")	
	re.mergeRandom()
	re.printGraph("before.png")	
	# re.printGraph("after.png")
	re2 = re.copyRegex()
	re2.printGraph("after.png")
