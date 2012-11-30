from regex import Regex

HSIZE = 10
class Inference:
	def __init__(self, numH, strings):
		self.hSpace_ = list()
		self.strings_ = strings
		self.baseH_ = Regex(strings)
		self.baseHProb_ = self.likelihood(self.baseH_)
		self.numH_ = numH
		for i in range(self.numH_):
			self.hSpace_.append((self.baseH_.copy(), self.baseHProb_))

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
		for i in range(self.numH_):
			self.hSpace_.append((self.baseH_.copy(), self.baseHProb_))
		for re, prob in self.hSpace_[:]:
			re2 = re.copy()
			if permute:
				re2.permuteRegex()
			self.hSpace_.append((re2, self.likelihood(re2)))

if __name__ == '__main__':

	# Test1: should recognize pattern in first 4 characters
	# parameters: alpha = 2, permute_prob = 0.5
	# strings = ['757-123', '757-134', '757-445', '757-915']
	# strings = \
	# ['757-123-2398'
	# ,'757-134-1111'
	# ,'757-445-2231'
	# ,'757-915-5547'
	# ,'(650) 853-9800'
	# ,'(650) 325-8500'
	# ,'(650) 326-0983'
	# ,'(650) 493-9188'
	# ,'(650) 853-3888'
	# ,'(650) 328-8899'
	# ,'(650) 323-7723']

	strings = ['abbb', 'acbb']
	inf = Inference(HSIZE, strings)
	inf.baseH_.printGraph("output/inference/h1.png")
	for i in range(1): 
		print "Iteration", i
		inf.duplicateHypotheses(True)
		inf.sortHypotheses()
		print "  best cost", inf.hSpace_[0][1]
		print "  worst cost", inf.hSpace_[-1][1]
		inf.hSpace_[0][0].printGraph("output/inference/trial-%d-best1.png" % i)
		inf.hSpace_[1][0].printGraph("output/inference/trial-%d-best2.png" % i)
		inf.hSpace_[2][0].printGraph("output/inference/trial-%d-best3.png" % i)
		inf.hSpace_[3][0].printGraph("output/inference/trial-%d-best4.png" % i)
		inf.hSpace_[4][0].printGraph("output/inference/trial-%d-best5.png" % i)
		inf.hSpace_[5][0].printGraph("output/inference/trial-%d-best6.png" % i)
		inf.hSpace_[-1][0].printGraph("output/inference/trial-%d-worst.png" % i)
		inf.cullHypotheses()
