class State:
	def __init__(self):
		self.prev_ = list()
		self.next_ = dict()
		self.accept_ = False
		self.name_ = None
		pass

	def nextNew(self, letter):
		if self.next_.get(letter, None) is None:
			self.next_[letter] = State()
			self.next_[letter].prev_.append(self)
		return self.next_[letter]

	def next(self, a):
		return self.next_.get(a, None)


class Regex:
	def __init__(self, str=None):
		self.states_ = dict()
		self.lastStateName_ = -1
		self.start_ = State()
		self.stateIs(self.start_)
		if str:
			self.stringIs(str)

	def stateIs(self, state):
		self.lastStateName_ = self.lastStateName_ + 1
		self.states_[self.lastStateName_] = state
		state.name_ = self.lastStateName_

	def stringIs(self, str):
		lastState = self.start_
		for a in str:
			lastState = lastState.nextNew(a)
			if lastState.name_ is None:
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

	#def mergeState(self):

	def display(self):
		for state in self.states_.values():
			print state.name_, "accept:", state.accept_
			for k, s in zip(state.next_.keys(), state.next_.values()):
				print "  ", k, ":", s.name_


if __name__ == '__main__':
	re = Regex("test")
	re.stringIs("tesh")
	re.stringIs("allaroundtheworld")
	re.display()
	print re.string("tehhh")