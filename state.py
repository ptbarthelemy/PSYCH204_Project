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