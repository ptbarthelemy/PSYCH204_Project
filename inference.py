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

def f(mat, ns, nf):
	if mat[ns][nf] is not None:
		return mat[ns][nf]
	elif nf == ns or nf == 0:
		result = 1
	else:
		result = nf * f(mat, ns-1, nf) + f(mat, ns-1, nf-1)
	mat[ns][nf] = result
	return result


def numRegexes(n):
	mat = [[None for i in range(n)] for j in range(n)]
	return sum(f(mat, n-1, i) for i in range(n))

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
	print "%e"%numRegexes(25)

	###########################################################################
	# wild card fitting

	# 70% chance to accept ilts.
	# if alpha is zero, beta needs to be >= 5 to accept test string
	# strings = ["glts", "elts", "glts", "flts"] 

	# 40% chance to accept ffg.
	# if alpha is zero, beta needs to be < 3 to reject test string
	# strings = ['efg', 'hfg', 'ifg']

	# 30% chance to accept bho
	# if alpha is zero, beta needs to be < 14 to reject test string
	# strings = ['bhi', 'bhw', 'bhi', 'bhw', 'bhw'] 

	###########################################################################
	# kleene star fitting
	# 90% chance of accepting abbb
	# if alpha is zero, beta must be greater than 2
	# strings = ['ab', 'abb']

	# 80% chance of accepting aoooo
	# if alpha is zero, beta must be greater than 1.5
	# strings = ['ao', 'aoo', 'aooo']

	inf = Inference(HSIZE, strings)
	for i in range(10): 
		print "Iteration", i
		inf.duplicateHypotheses(True)
		inf.sortHypotheses()
		print "  best cost", inf.hSpace_[0][1]
		print "  worst cost", inf.hSpace_[-1][1]
		inf.hSpace_[0][0].printGraph("output/inference/trial-%d-best.png" % i)
		inf.hSpace_[-1][0].printGraph("output/inference/trial-%d-worst.png" % i)
		inf.cullHypotheses()


