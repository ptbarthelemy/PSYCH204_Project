from regex import Regex
import copy

def toStr2(s):
	result = ""
	for a in sorted(s):
		result += ("%d"%a) + "-"
	return result[:-1]

def toStr1(s):
	stringList = list()
	for a in s: 
		stringList.append(toStr2(a))

	result = ''
	for a in sorted(stringList):
		result += a + "|"
	return result[:-1]

def totalSet(s):
	result = [[[s[0]]]]
	for a in s[1:]:
		newResult = list()
		for b in result:
			newB = [[a]]
			newB.extend(b)
			newResult.append(newB)
			for i in range(len(b)):
				newB = copy.deepcopy(b)
				newB[i].append(a)
				newResult.append(newB)
		result = copy.deepcopy(newResult)
	return result

HSIZE = 100
class Inference:
	def __init__(self, numH, strings):
		self.hSpace_ = list()
		self.strings_ = strings
		self.baseH_ = Regex(strings)
		self.baseHProb_ = self.likelihood(self.baseH_)
		self.numH_ = numH
		# for i in range(self.numH_):
		# 	self.hSpace_.append((self.baseH_.copy(), self.baseHProb_))

	def generateAll(self):
		print "Generating hypothesis for", len(self.baseH_.states_), "states."
		allRegexes = totalSet(list((s.ID_) for s in self.baseH_.states_.values()))
		print "Total number of regexes", len(allRegexes)
		for regexStates in allRegexes:
			newRegex = self.baseH_.copy()
			for a in regexStates:
				if len(a) == 1:
					continue
				for b in a[1:]:
					newRegex.mergeRandom(a[0], b)
			self.hSpace_.append((newRegex, self.likelihood(newRegex)))

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
		newH = list()
		for i in range(self.numH_ ):
			newH.append((self.baseH_.copy(), self.baseHProb_))
		for re, prob in self.hSpace_[:]:
			re2 = re.copy()
			if permute:
				re2.permuteRegex()
			newH.append((re2, self.likelihood(re2)))
		self.hSpace_.extend(newH)

if __name__ == '__main__':
	# generate all hypotheses
	strings = ['abc', 'dbc', 'ebc', 'abc', 'dbc']
	inf = Inference(HSIZE, strings)
	inf.generateAll()
	# for a, index in zip(inf.hSpace_, range(len(inf.hSpace_))):
	# 	regex, prob = a
	# 	regex.printGraph("output/hypothesis%d.png"%index)
	inf.sortHypotheses()
	for i in range(10):
		print "Place", i, "probability", inf.hSpace_[i][1]
		inf.hSpace_[i][0].printGraph("output/hypothesis-top%d.png"%i)

	print "Worst probability", inf.hSpace_[-1][1]
	inf.hSpace_[-1][0].printGraph("output/hypothesis-bottom.png")

	# Test1: should recognize pattern in first 4 characters
	# parameters: alpha = 2, permute_prob = 0.5
	#strings = ['757-123', '757-134', '757-445', '757-915']
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

	# wildcard threshold: increasing variance means higher likelihood of wildcard
	# workds with (0, 5)
	# strings = ['abc', 'dbc'] # should not use a wildcard
	# strings = ['abc', 'dbc', 'ebc'] # should use a wildcard
	# strings = ['abc', 'dbc', 'ebc', 'fbc'] # should use a wildcard
	# strings = ['abcdefg', 'dbcdefg', 'ebcdefg', 'fbcdefg'] # should use wildcard

	# wildcard threshold: increasing the number of examples should decrease the likelihood of a wildcard
	# works with (0, 5)
	# strings = ['abc', 'dbc', 'ebc'] # should use a wildcard
	# strings = ['abc', 'dbc', 'ebc', 'abc', 'dbc', 'ebc'] # should not use a wildcard
	strings = ['abc', 'dbc', 'ebc', 'abc', 'dbc'] # should not use a wildcard

	# kleene threshold: increasing the variance means higher likelihood of kleene
	# works with (0, 2)
	# strings = ['acb', 'acbb'] # should not use kleene
	# strings = ['ab', 'abb', 'abbb'] # should use kleene
	# strings = ['abc', 'abbc', 'abc', 'abbc', 'abc', 'abbc', 'abc', 'abbc'] # should not use kleene

	# kleene threshold: increasing the number of examples should decrease the likelihood of kleene
	# works with (0, 2)
	# strings = ['ab', 'abb', 'abbb'] # should use kleene
	# strings = ['ab', 'abb', 'abbb', 'ab', 'abb', 'abbb', 'ab', 'abb', 'abbb', 'ab', 'abb', 'abbb'] # should not use kleene

	# strings = ['abcd', 'abce', 'bbce', 'bbcd']
	# strings = ['abc', 'abbc', 'abc']
	# strings = ['abc', 'adc', 'adce']
	# strings = ['abcd', 'bbcd', 'dbcd']
	# strings = ['abcd', 'bbcd', 'efgh'] # < we definitely won't be able to learn this
	# strings = ['oee', 'oee', 'oe']
	# strings = ['oeeeeeeeee', 'oeeeeeeeee', 'oeeeeeeeee', 'oeeeeeeeee', 'oeeeeeeeee', 'oeeeeeeeee', 'oeeeeeeeee', 'oeeeeeeeee', 'oeeeeeeeee'] # it takes way too long to NOT generalize
	# strings = ['oeee', 'oeee', 'oe', 'oe', 'oe', 'oe', 'oeee'] # generalizes
	# strings = ['oee', 'oee', 'oe', 'oe', 'oe', 'oe', 'oee'] # doesn't generalize
	# strings = ['oeee', 'oeee', 'oe', 'oe', 'oe', 'oe', 'oeee', 'oeee', 'oeee', 'oe', 'oe', 'oe', 'oe', 'oeee']
	inf = Inference(HSIZE, strings)
	print "Base hypothesis probability", inf.baseHProb_
	inf.baseH_.printGraph("output/inference/hbase.png")


	for i in range(10): 
		print "Iteration", i
		inf.duplicateHypotheses(True)
		inf.sortHypotheses()
		print "  best cost", inf.hSpace_[0][1]
		print "  worst cost", inf.hSpace_[-1][1]
		inf.hSpace_[0][0].printGraph("output/inference/trial-%d-best.png" % i)
		# inf.hSpace_[1][0].printGraph("output/inference/trial-%d-best2.png" % i)
		# inf.hSpace_[2][0].printGraph("output/inference/trial-%d-best3.png" % i)
		# inf.hSpace_[3][0].printGraph("output/inference/trial-%d-best4.png" % i)
		# inf.hSpace_[4][0].printGraph("output/inference/trial-%d-best5.png" % i)
		# inf.hSpace_[5][0].printGraph("output/inference/trial-%d-best6.png" % i)
		inf.hSpace_[-1][0].printGraph("output/inference/trial-%d-worst.png" % i)
		inf.cullHypotheses()
