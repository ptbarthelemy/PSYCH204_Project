from regex import Regex

HSIZE = 10
class Inference:
	def __init__(self, numH, strings):
		self.hSpace_ = list()
		self.strings_ = strings
		self.baseH_ = Regex(strings)
		self.numH_ = numH
		prob = self.likelihood(self.baseH_)
		for i in range(self.numH_):
			self.hSpace_.append((self.baseH_.copy(), prob))

	def cullHypotheses(self):
		for a in range(len(self.hSpace_) - self.numH_):
			del self.hSpace_[-1]

	def sortHypotheses(self):
		# sort by descending probability
		self.hSpace_ = sorted(self.hSpace_, key=lambda array: -array[1])

	def likelihood(self, re):
		result = re.logPrior()
		for string in self.strings_:
			accept, LL = re.string(string)
			if not accept:
				print "Error, regex does not accept string", string
				re.printGraph("output/inference/error.png")
				assert False
			result += LL
		return result

	def duplicateHypotheses(self, permute=False):
		for re, prob in self.hSpace_[:]:
			re2 = re.copy()
			if permute:
				re2.permuteRegex()
			self.hSpace_.append((re2, self.likelihood(re2)))

if __name__ == '__main__':
	inf = Inference(HSIZE, ['757-123', '757-134', '757-445', '757-915'])
	inf.baseH_.printGraph("output/inference/h1.png")
	for i in range(10): 
		print "Iteration", i
		inf.duplicateHypotheses(True)
		inf.sortHypotheses()
		print "  best cost", inf.hSpace_[0][1]
		print "  worst cost", inf.hSpace_[-1][1]
		inf.hSpace_[0][0].printGraph("output/inference/trial-%d-best.png" % i)
		inf.hSpace_[-1][0].printGraph("output/inference/trial-%d-worst.png" % i)
		inf.cullHypotheses()
