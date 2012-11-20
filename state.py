from random import random

WILDCARD_NUM = "N"
SET_NUM = "0123456789"
WILDCARD_ALPHA = "A"
SET_ALPHA = "abcdefghijklmnopqrstuvwxyz"
WILDCARD_ALL = "S"
SET_ALL = "0123456789abcdefghijklmnopqrstuvwxyz -"

def getFromLetterDict(letterDict, letter):
	result = None
	if letter in SET_NUM:
		result = letterDict.get(WILDCARD_NUM, None)
	if result is None and letter in SET_ALPHA:
		result = letterDict.get(WILDCARD_ALPHA, None)
	if result is None:
		result = letterDict.get(WILDCARD_ALL, None)
	if result is None:
		result = letterDict.get(letter, None)
	return result	

def overlap(letter1, letter2):
	if letter1 == letter2:
		return letter1
	if WILDCARD_ALL in (letter1, letter2):
		return WILDCARD_ALL
	if WILDCARD_ALPHA == letter1 and letter2 in SET_ALPHA or\
		WILDCARD_ALPHA == letter2 and letter1 in SET_ALPHA:
		return WILDCARD_ALPHA
	if WILDCARD_NUM == letter1 and letter2 in SET_NUM or\
		WILDCARD_NUM == letter2 and letter1 in SET_NUM:
		return WILDCARD_NUM
	return None


class State:
	def __init__(self, regex, start=False):
		self.prev_ = dict() # maps letter to all predecessors
		self.next_ = dict() # maps letter to single successor
		self.accept_ = False
		self.ID_ = None
		self.start_ = start
		self.regex_ = regex
		regex.stateIs(self)
		pass

	def next(self, letter):
		return getFromLetterDict(self.next_, letter)

	def prev(self, letter):
		return getFromLetterDict(self.prev_, letter)

	def nextRemove(self, letter):
		print "Removing transition", self.ID_, ":",letter,":", self.next_[letter].ID_
		nextState = self.next_[letter]
		del self.next_[letter]
		nextState.prev_[letter].remove(self)
		if len(nextState.prev_[letter]) == 0:
			del nextState.prev_[letter]

	def nextIs(self, letter, state):
		print "Transition", self.ID_, ":", letter, ":", state.ID_

		# merge items as necessary
		mergeList = list()
		for k, s in self.next_.items():
			newLetter = overlap(k, letter)
			if newLetter is not None:
				print "  >Transition", self.ID_, ":", k, ":", s.ID_, "requires merging"
				letter = newLetter
				mergeList.append(s)
				self.nextRemove(k)

		# insert state
		self.regex_.printText()
		self.next_[letter] = state
		if state.prev_.get(letter, None) is None:
			state.prev_[letter] = [self]
		else:
			state.prev_[letter].append(self)

		# merge remaining states
		for s in mergeList:
			print "Merging", s.ID_
			state.merge(s)

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
		print "Changing incoming transitions"
		for k, sSet in state.prev_.items():
			for s in sSet[:]: # set is not constant--need copy
				s.nextRemove(k)
				s.nextIs(k, self)

		# add outgoing transitions (originally from state) to state1
		# mergeList = list()
		print "Changing outgoing transitions"
		for k, s in state.next_.items():
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
		for k, s2 in self.next_.items():
			for wildcard in [WILDCARD_NUM, WILDCARD_ALPHA, WILDCARD_ALL]:
				if self.wildcardizeTransition(k, wildcard):
					break

