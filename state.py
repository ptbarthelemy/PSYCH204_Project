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
	if result is None and letter in SET_ALL:
		result = letterDict.get(letter, None)
	return result	


class State:
	def __init__(self):
		self.prev_ = dict() # maps letter to all predecessors
		self.next_ = dict() # maps letter to single successor
		self.accept_ = False
		self.ID_ = None
		pass

	def next(self, letter):
		return getFromLetterDict(self.next_, letter)

	def prev(self, letter):
		return getFromLetterDict(self.prev_, letter)

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

	def nextRemove(self, letter):
		# remove transition between state and next without deleting next
		print "Replacing transition", letter,"for state",self.ID_
		state2 = self.next_[letter]
		state2.prev_[letter].remove(self)
		if len(state2.prev_[letter]) == 0:
			del state2.prev_[letter]
		del self.next_[letter]

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

		# replace transition only if no other transition from the same
		# set exists
		state2 = self.next(k)
		replace = [k]
		for kOther, state2Other in self.next_.items():
			if kOther == k:
				continue
			if kOther in charSet:
				if state2Other.ID_ != state2.ID_:
					return False
				replace.append(kOther)

		# replace transition
		for letter in replace:
			self.nextRemove(letter)
		self.nextIs(wildcard, state2)
		return True

	def wildcardize(self):
		for k, s2 in self.next_.items():
			for wildcard in [WILDCARD_NUM, WILDCARD_ALPHA, WILDCARD_ALL]:
				if self.wildcardizeTransition(k, wildcard):
					break

