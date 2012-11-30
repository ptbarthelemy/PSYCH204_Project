from random import choice, seed, random
from math import exp, log
import pydot
from state import State

DEBUG = False
ALPHA = 2
PERMUTE_PROB = 0.7

def floatEqual(f1, f2):
	if abs(f1 - f2) < 0.00005:
		return True
	return False

def probOfSkippingAccept(n, lastAcceptChoice):
	"""
	Parameters:
		- n is the number of accept states skipped.
		- lastAcceptChoice is whether the string could have continued beyond
		  the accept state.

	Let tau be the probability of a string not being generated beyond an accept
	state. Instead of setting tau, we can simply apply a uniform prior and
	integrate over possible values. This gives us the formulas below:

	if the string could have continued beyond the last accept state:
		p(stopping at desired accept) = p(string match) (tau) (1 - tau)^n
		marginalizing -->			  = p(string match) / (n^2 + 3n + 2)

	otherwise:
		p(stopping at desired accept) = p(string match) (1 - tau)^n
		marginalizing -->			  = p(string match) / (n + 1)

	This concept was explained in the Rational Rules paper, p. 6.
	"""
	if lastAcceptChoice:
		return 1./(n**2 + 3*n + 2)
	return 1./(n+1)

class Regex:
	def __init__(self, strings=None):
		self.mergeQueue_ = list()
		self.states_ = dict()
		self.lastStateID_ = -1
		self.start_ = None
		if strings is not None:
			for string in strings:
				self.stringIs(string)

	def stateIs(self, state):
		# assign ID if there isn't one
		if state.ID_ is None:
			self.lastStateID_ = self.lastStateID_ + 1
			state.ID_ = self.lastStateID_

		# add state to map
		self.states_[state.ID_] = state

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
		lastState.accept_ = True

		if DEBUG: print "need to merge", list((s1.ID_, s2.ID_) for s1, s2 in self.mergeQueue_)
		while len(self.mergeQueue_) > 0:
			s1, s2 = self.mergeQueue_.pop(0)
			s1.merge(s2)

	def copy(self):
		copyRegex = Regex(None)

		# add all of the nodes
		for ID, s in self.states_.items():
			s.copy(copyRegex)

		# add all of the edges
		for ID, s1 in self.states_.items():
			for k, s2 in s1.next_:
				copyRegex.states_[ID].nextIs(k, copyRegex.states_[s2.ID_])

		# set the regex-level attributes
		copyRegex.lastStateID_ = self.lastStateID_
		copyRegex.start_ = copyRegex.states_[self.start_.ID_]

		return copyRegex

	def mergeRandom(self, ID1=None, ID2=None):
		# return if only one state remains
		if len(self.states_) == 1:
			return
		if ID1 is None or ID2 is None:
			ID1 = choice(self.states_.keys())
			ID2 = choice(list(a for a in self.states_.keys() if a != ID1))
		if DEBUG: print "Merging states", ID1, "and", ID2
		
		# loop through all states
		self.mergeQueue_.append((self.states_[ID1], self.states_[ID2]))
		while len(self.mergeQueue_) > 0:
			s1, s2 = self.mergeQueue_.pop(0)
			s1.merge(s2)

	def permuteRegex(self):
		while (random()) < PERMUTE_PROB:
			if (random()) < 0.5:
				self.mergeRandom()
			else:
				self.wildcardize()

	def wildcardize(self):
		# for s1 in self.states_.values():
		# 	s1.wildcardize()

		self.states_[choice(self.states_.keys())].wildcardize()
		while len(self.mergeQueue_) > 0:
			s1, s2 = self.mergeQueue_.pop(0)
			s1.merge(s2)

	def printText(self):
		print "#Regex display"
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

	def logPrior(self):
		return - ALPHA * len(self.states_);

	def string(self, str):
		logLikelihood = 0
		numAcceptSkipped = 0
		state = self.start_
		while len(str) != 0:
			newLL, accept = state.logLikelihood()
			logLikelihood += newLL
			numAcceptSkipped += 1 if accept else 0
			state = state.next(str[0])
			str = str[1:]
			if state is None:
				return False, None

		if state.accept_:
			lastAcceptChoice = False
			if len(state.next_) > 0:
				lastAcceptChoice = True
			return True, logLikelihood + log(probOfSkippingAccept(numAcceptSkipped,lastAcceptChoice))

		return False, None


def TestMerge(strings, seedVal=None):
	if seedVal is not None:
		seed(seedVal)
	re = Regex(strings)
	i = 0
	while True:
		# re.printText()
		re.printGraph("output/merge-%d.png" % i)
		for string in strings:
			accept, prob = re.string(string)
			assert accept, "Error: base string was not accepted."
		if len(re.states_) == 1:
			break
		# print "\n*** Loop stage", i
		re.mergeRandom()
		i += 1

def TestWildcardize(strings, seedVal=None):
	if seedVal is not None:
		seed(seedVal)
	re = Regex(strings)
	for i in range(10):
		# re.printText()
		re.printGraph("output/merge-%d.png" % i)
		for string in strings:
			accept, prob = re.string(string)
			assert accept, "Error: base string was not accepted."
		# print "\n*** Loop stage", i
		re.wildcardize()

if __name__ == '__main__':
	strings1 = ['757-123', '757-134', '757-445', '757-915'] 
	strings2 = ["abc", "sS"] 
	strings3 = ["testa", "tesSa", "bootcamp"]

	TestMerge(strings1, 9)
	# TestMerge(strings2)
	# TestMerge(strings3)

	# TestWildcardize(strings1)
	# TestWildcardize(strings2)
	# TestWildcardize(strings3)

	# log prior
	re = Regex(["testa", "Sbesta"])
	test = re.logPrior()
	assert floatEqual(test, - ALPHA * 11), test

	# likelihood
	re = Regex(["testa", "besta"])
	test1, test2 = re.string("testa")
	assert test1
	test2 = exp(test2)
	assert floatEqual(test2, 0.5), test2

	re = Regex(["testa", "testab"])
	test1, test2 = re.string("testa")
	assert test1
	test2 = exp(test2)
	assert floatEqual(test2, 0.5), test2

	re = Regex([""])
	re.stringIs("testa")
	test1, test2 = re.string("testa")
	assert test1
	test2 = exp(test2)
	assert floatEqual(test2, 0.5), test2

	print "Passed all tests."
