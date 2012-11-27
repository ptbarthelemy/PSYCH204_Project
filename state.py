from random import random
from math import log

WILDCARD_NUM = "N"
SET_NUM = "0123456789"
WILDCARD_ALPHA = "A"
SET_ALPHA = "abcdefghijklmnopqrstuvwxyz"
WILDCARD_ALL = "S"
SET_ALL = "0123456789abcdefghijklmnopqrstuvwxyz -"

DEBUG = False

def keyUnion(key1, key2):
	# return a wildcard if applicable
	if WILDCARD_ALL in key1+key2:
		return WILDCARD_ALL

	result = set(key1 + key2)

	if WILDCARD_ALPHA in result:
		for a in result.copy():
			if a in SET_ALPHA:
				result.remove(a)
	if WILDCARD_NUM in result:
		for a in result.copy():
			if a in SET_NUM:
				result.remove(a)

	# otherwise take the union
	result = list(result)
	result.sort()
	return ''.join(result)

def keysOverlap(key1, key2):
	return len(keyUnion(key1, key2)) < len(key1 + key2)

def isKey(key):
	if key == WILDCARD_ALL:
		return True
	if key == WILDCARD_ALPHA:
		return True
	if key == WILDCARD_NUM:
		return True

def keyIntersect(key1, key2):
	result = set()
	for a in key1:
		for b in key2:
			if keysOverlap(a, b):
				if isKey(a):
					result.add(b)
				else:
					result.add(a)

	result = list(result)
	result.sort()
	return ''.join(result)

def keyLen(key):
	result = len(key)
	if WILDCARD_ALL == key:
		return len(SET_ALL)
	if WILDCARD_ALPHA in key:
		result += len(SET_ALPHA) - 1
	if WILDCARD_NUM in key:
		result += len(SET_NUM) - 1
	return result

def numOverlap(key1, key2):
	return keyLen(keyIntersect(key1, key2))

def keyChangeProb(k, wildcard):
	return numOverlap(k, wildcard) * 1.0 / keyLen(wildcard)

class State:
	def __init__(self, regex=None, start=False, ID=None):
		self.prev_ = list() # maps key to all predecessors
		self.next_ = list() # maps key to single successor
		self.accept_ = False
		self.ID_ = ID
		self.start_ = start
		self.regex_ = regex
		if regex is not None:
			regex.stateIs(self)

	def copy(self, regex=None):
		result = State(regex=regex, start=self.start_, ID=self.ID_)
		result.accept_ = self.accept_
		return result

	def next(self, letter):
		for k, s in self.next_:
			if keysOverlap(k, letter):
				return s
		return None

	def logLikelihood(self):
		options = 0
		for k, s in self.next_:
			options += keyLen(k)
		if self.accept_:
			options += 1
		return - log(options)

	def nextRemove(self, key, state):
		if DEBUG: print "Removing transitions for", self.ID_, ":",key, ":", state.ID_
		# remove forward pointer
		i = 0
		for k, s in self.next_:
			if k == key and s.ID_ == state.ID_:
				del self.next_[i]
			i += 1

		# remove backward pointer
		i = 0
		for k, s in state.prev_:
			if k == key and s.ID_ == self.ID_:
				del state.prev_[i]
				break
			i += 1

	def nextIs(self, key, state):
		if DEBUG: print "Inserting transition", self.ID_, ":", key, ":", state.ID_

		# insert state, merge with existing transition to same state (if exists)
		for k, s in self.next_:
			if s.ID_ == state.ID_:
				key = keyUnion(key, k)
				self.nextRemove(k, s)
				if DEBUG: print "  replacing", k, "and original with", key
		self.next_.append((key, state))
		state.prev_.append((key, self))

		# merge if there are any conflicts
		for k1, s1, k2, s2 in ((k1, s1, k2, s2) for k1, s1 in self.next_
			for k2, s2 in self.next_ if s1.ID_ < s2.ID_):
			if keysOverlap(k1, k2):
				self.regex_.mergeQueue_.append((s1, s2))

		return self.next(key)

	def merge(self, state):
		if DEBUG:
			print "Merging", self.ID_, "with", state.ID_, ". Before merge:"
			self.regex_.printText()
		if self.ID_ == state.ID_:
			if DEBUG: print "States are the same."
			return
		if state.ID_ not in self.regex_.states_.keys() \
			or self.ID_ not in self.regex_.states_.keys() :
			if DEBUG: print "State no longer exists."
			return			
		if state.start_:
			if DEBUG: print "Reordering so start state is first."
			state.merge(self)
			return

		# add incoming transitions (originally to state) to self
		if DEBUG: print "Adding incoming transitions", list((k, s.ID_)
				for k, s in state.prev_)
		for k, s in state.prev_[:]:
			s.nextRemove(k, state)
			s.nextIs(k, self)

		# add outgoing transitions (originally from state) to self
		if DEBUG: print "Adding outgoing transitions", list((k, s.ID_)
					for k, s in state.next_)
		for k, s in state.next_[:]:
			state.nextRemove(k, s)
			self.nextIs(k, s)

		# make accept state if either state is accept
		if state.accept_:
			self.accept_ = True

		# delete state
		self.regex_.stateRemove(state)

		if DEBUG:
			print "After merge:"
			self.regex_.printText()

	def wildcardize(self):
		for k, s2 in self.next_:
			for wildcard in [WILDCARD_ALL, WILDCARD_ALPHA, WILDCARD_NUM]:
				if (random()) < keyChangeProb(k, wildcard):
					self.nextIs(wildcard, self.next(k))
					break


if __name__ == '__main__':
	# test keyunion
	assert keyUnion("abcd", "abc") == "abcd", keyUnion("abcd", "abc")
	assert keyUnion("abc", "abcd") == "abcd", keyUnion("abc", "abcd")
	assert keyUnion("abc", "abd") == "abcd", keyUnion("abc", "abd")
	assert keyUnion("abcN", "123") == "Nabc", keyUnion("abcN", "123")
	assert keyUnion("abcN", "d123") == "Nabcd", keyUnion("abcN", "d123")
	assert keyUnion("S", "asbcdk314") == "S", keyUnion("S", "asbcdk314")
	assert keyUnion("A123", "abcdkN") == "AN", keyUnion("A123", "abcdkN")
	test = keyUnion("-35", "23457")
	assert test == "-23457", test

	# test keyintersect
	test = keyIntersect("abcd", "A")
	assert  test == "abcd", test
	test = keyIntersect("A", "abcd1")
	assert  test == "abcd", test
	test = keyIntersect("AN", "abcd1")
	assert  test == "1abcd", test
	test = keyIntersect("S", "abcd1")
	assert  test == "1abcd", test
	test = keyIntersect("S", "abcdN")
	assert  test == "Nabcd", test
	test = keyIntersect("1234A", "abcN")
	assert  test == "1234abc", test

	# test keyLen
	test = keyLen("abcd")
	assert test == 4, test
	test = keyLen("S")
	assert test == len(SET_ALL), test
	test = keyLen("abcdN")
	assert test == 4 + len(SET_NUM), test
	test = keyLen("A")
	assert test == len(SET_ALPHA), test

	print "All tests pass."

