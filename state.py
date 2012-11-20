from random import random

WILDCARD_NUM = "N"
SET_NUM = "0123456789"
WILDCARD_ALPHA = "A"
SET_ALPHA = "abcdefghijklmnopqrstuvwxyz"
WILDCARD_ALL = "S"
SET_ALL = "0123456789abcdefghijklmnopqrstuvwxyz -"


def keyUnion(key1, key2):
	# return a wildcard if applicable
	if WILDCARD_ALL in key1+key2:
		return WILDCARD_ALL
	if WILDCARD_ALPHA in key1 and sum(1 for a in key2 if a in SET_ALPHA) == len(key2) or\
		WILDCARD_ALPHA in key2 and sum(1 for a in key1 if a in SET_ALPHA) == len(key1):
		return WILDCARD_ALPHA
	if WILDCARD_NUM == key1 and (1 for a in key2 if a in SET_NUM) == len(key2) or\
		WILDCARD_NUM == key2 and sum(1 for a in key1 if a in SET_NUM) == len(key1):
		return WILDCARD_NUM

	# otherwise take the union
	return ''.join(set(key1 + key2))

def keysOverlap(key1, key2):
	return len(keyUnion(key1, key2)) < len(key1 + key2)

class State:
	def __init__(self, regex, start=False):
		self.prev_ = list() # maps key to all predecessors
		self.next_ = list() # maps key to single successor
		self.accept_ = False
		self.ID_ = None
		self.start_ = start
		self.regex_ = regex
		regex.stateIs(self)
		pass

	def next(self, letter):
		for k, s in self.next_:
			if keysOverlap(k, letter):
				return s
		return None

	# def prev(self, letter):
	# 	return getFromLetterDict(self.prev_, letter)

	def nextRemove(self, key, state=None):
		print "Removing transitions for", self.ID_, ":",key, ":"
		# remove forward pointer
		index = 0
		nextStates = list()
		indices = list()
		for k, s in self.next_:
			if keysOverlap(k, key):
				remove = False
				if state is None:
					remove = True
				elif s.ID_ == state.ID_:
					remove = True
				if remove:
					print " ...", s.ID_
					nextStates.append(s)
					indices.append(index)
			index += 1
		for i in reversed(indices):
			del self.next_[i]

		# remove backward pointer
		for nextState in nextStates:
			index = 0
			indices = list()
			for k, s in nextState.prev_:
				if keysOverlap(k, key) and s.ID_ == self.ID_:
					indices.append(index)
				index += 1

			for i in reversed(indices):
				del nextState.prev_[i]

	def nextIs(self, key, state):
		print "Transition", self.ID_, ":", key, ":", state.ID_

		# insert state, merge with existing transition to same state (if exists)
		for k, s in self.next_:
			if s.ID_ == state.ID_:
				self.nextRemove(k)
				key = keyUnion(key, k)
		self.next_.append((key, state))
		state.prev_.append((key, self))

		# merge if there are any conflicts
		for k1, s1, k2, s2 in ((k1, s1, k2, s2) for k1, s1 in self.next_ for k2, s2 in self.next_):
			if keysOverlap(k1, k2) and s1.ID_ is not s2.ID_:
				self.regex_.mergeQueue_.append((s1, s2))

		return self.next(key)

	def merge(self, state):
		print "Merging", self.ID_, "with", state.ID_
		if self.ID_ == state.ID_:
			print "States are the same."
			return
		if state.ID_ not in self.regex_.states_.keys() \
			or self.ID_ not in self.regex_.states_.keys() :
			print "State no longer exists."
			return			
		if state.start_:
			print "Reordering so start state is first."
			state.merge(self)
			return

		# add incoming transitions (originally to state) to self
		print "Changing incoming transitions", list((k, s.ID_)
				for k, s in state.prev_)
		for k, s in state.prev_[:]:
			s.nextRemove(k, state)
			s.nextIs(k, self)

		# add outgoing transitions (originally from state) to state1
		print "Changing outgoing transitions", list((k, s.ID_)
					for k, s in state.next_)
		for k, s in state.next_[:]:
			state.nextRemove(k, s)
			self.nextIs(k, s)

		# make accept state if either state is accept
		if state.accept_:
			self.accept_ = True

		# delete state
		self.regex_.stateRemove(state)

	def wildcardizeTransition(self, k, wildcard):
		# set up charSet
		count = 1.
		if wildcard == WILDCARD_ALL:
			charSet = SET_ALL
			if k == WILDCARD_NUM:
				count = len(SET_NUM)
			elif k == WILDCARD_ALPHA:
				count = len(SET_ALPHA)
		elif wildcard == WILDCARD_ALPHA:
			charSet = SET_ALPHA
			if k not in charSet:
				return False
		elif wildcard == WILDCARD_NUM:
			charSet = SET_NUM
			if k not in charSet:
				return False
		else:
			print "Wildcard not recognized"

		# do so probabilisitcally
		if (random()) > count / len(charSet):
			return False

		self.nextIs(wildcard, state2)
		return True

	def wildcardize(self):
		for k, s2 in self.next_:
			for wildcard in [WILDCARD_NUM, WILDCARD_ALPHA, WILDCARD_ALL]:
				if self.wildcardizeTransition(k, wildcard):
					break

