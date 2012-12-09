from regex import Regex
from math import exp
from state import keysOverlap, keyMinus
import csv
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
BEAM_SIZE = 100
class Inference:
	def __init__(self, numH, strings):
		self.hSpace_ = list()
		self.strings_ = strings
		self.baseH_ = Regex(strings)
		self.baseHProb_ = self.likelihood(self.baseH_)
		self.numH_ = numH
		self.addRegexes([(self.baseH_.copy(), self.baseHProb_)])

	def addRegexes(self, reSet):
		# add set
		for re, prob in reSet:
			load = True
			for h, _ in self.hSpace_:
				if re.equalTo(h):
					load = False
					continue
			if load:
				self.hSpace_.append((re, prob))

		# remove extra hypotheses
		self.sortHypotheses()
		# self.cullHypotheses()

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
			self.addRegexes([(newRegex, self.likelihood(newRegex))])

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
				re.printText()
				re.printGraph("output/inference/error.png")
				assert False
			result += LL
		return result

	def duplicateHypotheses(self, permute=False):
		newH = list()
		for i in range(self.numH_ ):
			newRe = self.baseH_.copy()
			newRe.permuteRegex()
			newH.append((newRe, self.likelihood(newRe)))
		while len(self.hSpace_) < 2 * self.numH_:
			for re, prob in self.hSpace_[:]:
				re2 = re.copy()
				if permute:
					re2.permuteRegex()
				newH.append((re2, self.likelihood(re2)))
			self.addRegexes(newH)

	def testString(self, testString):
		totalProb = 0
		acceptProb = 0
		for h, prob in self.hSpace_:
			totalProb += exp(prob)
			accept, _ = h.string(testString)
			if accept:
				acceptProb += exp(prob)

		return acceptProb / totalProb

	def beamStep(self, re):
		newRegexes = list()
		# generate merged steps
		for stateID1 in list((s.ID_) for s in re.states_.values()):
			for stateID2 in list((s.ID_) for s in re.states_.values()):
				if stateID1 == stateID2:
					continue
				newRe = re.copy()
				newRe.mergeRandom(stateID1, stateID2)
				newRegexes.append((newRe, self.likelihood(newRe)))

		# generate wildcard steps
		for stateID1 in list((s.ID_) for s in re.states_.values()):
			for wildcard in ['S', 'N', 'A']:
				for k, s in re.states_[stateID1].next_:
					if keysOverlap(k, wildcard) and keyMinus(wildcard, k) != '':
						newRe = re.copy()
						newRe.wildcardize(stateID1, wildcard)
						newRegexes.append((newRe, self.likelihood(newRe)))

						# only replace one of the transitions for a wildcard
						break

		return newRegexes

	def beamSearch(self):
		beam = [(self.baseH_, self.baseHProb_)]
		newBeam = list()
		i = 0
		while len(beam) > 0:
			print "beam iteration:", i, "hypotheses:", len(beam)
			i += 1

			# take step forward
			while len(beam) > 0:
				h, prob = beam.pop(0)
				newBeam.extend(self.beamStep(h))

			# exit if there is no more step
			if len(newBeam) == 0:
				return

			# copy best hypotheses to old beam
			newBeam = sorted(newBeam, key=lambda array: -array[1])
			while len(beam) < BEAM_SIZE and len(newBeam) > 0:
				re1, prob1 = newBeam.pop(0)
				# add = True
				# for re2, prob2 in beam:
				# 	if re1.equalTo(re2):
				# 		add = False
				# 		break
				# if add:
				if True:
					beam.append((re1, prob1))

			#beam[0][0].printGraph("output/beam-iter-%d-1.png"%i)
			#beam[1][0].printGraph("output/beam-iter-%d-2.png"%i)
			#beam[2][0].printGraph("output/beam-iter-%d-3.png"%i)
			#beam[3][0].printGraph("output/beam-iter-%d-4.png"%i)
			#beam[4][0].printGraph("output/beam-iter-%d-5.png"%i)

			# add hypotheses in beam to hset, clear newbeam
			self.addRegexes(beam)
			self.addRegexes(newBeam)
			newBeam = list()

if __name__ == '__main__':
	# print "%e"%numRegexes(25)
	# strings = ['abc', 'ad']
	# inf = Inference(HSIZE, strings)
	# inf.beamSearch()

	###########################################################################
	# wild card training

	# 70% chance to accept ilts.
	# if alpha is zero, beta needs to be >= 5 to accept test string
	# if alpha is one, beta needs to be >= 5 to accept the test string
	# strings = ["glts", "elts", "glts", "flts"] 

	# 45% chance to accept ffg.
	# if alpha is zero, beta needs to be < 3 to reject test string
	# if alpha is one, beta needs to be < 3 to reject string
	# strings = ['efg', 'hfg', 'ifg']

	# 30% chance to accept bho
	# if alpha is zero, beta needs to be < 14 to reject test string
	# if alpha is one, beta needs to be < 14 to reject
	# strings = ['bhi', 'bhw', 'bhi', 'bhw', 'bhw']

	###########################################################################
	# kleene star training
	# 90% chance of accepting abbb
	# if alpha is zero, beta must be greater than 2
	# strings = ['ab', 'abb']

	# 80% chance of accepting aoooo
	# if alpha is zero, beta must be greater than 1.5
	#strings = ['jojojojo', 'jojojojo', 'jojojojo']	
	###########################################################################
	input_strings = []

	input_strings.append(['yyyt', 'yt', 'yyyt', 'yyyt', 'yt'])
	input_strings.append(['a'])
	input_strings.append(['ab'])
	input_strings.append(['jojojojo', 'jojojojo', 'jojojojo'])
	input_strings.append(['kl', 'al'])
	input_strings.append(['twtwtw', 'twtwtw', 'twtwtw'])
	input_strings.append(['mat', 'mat', 'mat', 'mat', 'mat', 'tat','mat'])
	input_strings.append(['aaaa','aaaa','aaa'])
	input_strings.append(['www', 'wwww', 'wwww', 'www,' 'wwww'])
	input_strings.append(['qtro','qtrs','ctrs','ctro'])
	input_strings.append(['lcyy','acyy','zcyy','zcyy'])
	input_strings.append(['sfef', 'sfef','sfef', 'sfef'])
	input_strings.append(['bhi', 'bhw', 'bhi', 'bhw', 'bhw'])
	input_strings.append(['adc', 'abc', 'adce'])
	input_strings.append(['ab','abb'])
	input_strings.append(['efg', 'hfg' ,'ifg'])
	input_strings.append(['aoo','ao','aooo'])
	input_strings.append(['zze','zzq','zze','zze'])
	input_strings.append(['glts', 'elts', 'glts', 'flts'])
	input_strings.append(['htuu','ntuu','htuu','xtuu','ztuu','xtuu','ztuu'])
	input_strings.append(['yyyt', 'yt', 'yyyt', 'yyyt', 'yt'])
	input_strings.append(['lp','lllp','llp','llllp','llp','lllp'])
	input_strings.append(['zill','ddill','ddill','zdill','ddill','zdill'])
	test_strings = ['yyyyyt','b','abb','jojo','cl','tw','cat','aaaaaa','wwwwww','ibcd', 'wxcy','lfjk','bho','abce','abbb','ffg','aoooo','zzo','lfts','jtuu','yyt','lllllp','gdill']
	
	test_results = []
	survey_results = [.8, .5, .85,.75,.75,.68,.65,.95,1,.05,.05,0,.35,1,.9,.45,.8,.35,.7,.6,.5,.85,.15]
	
	for j in range(len(input_strings)):
		strings = input_strings[j]
		inf = Inference(HSIZE, strings)
		inf.beamSearch()
		test_results.append(inf.testString(test_strings[j]))
		print strings + ',' + test_strings[i] + ',' + survey_results[i]
	print test_results

	with open('new-model-results.csv', 	'wb') as csvfile:
		thewriter = csv.writer(csvfile)
		for i, string in enumerate(input_strings):
			thewriter.writerow([string] + [test_strings[i]] + [survey_results[i]])


	###########################################################################
	# test, random search
	# inf = Inference(HSIZE, strings)
	# for i in range(5): 
	# 	print "Iteration:", i, "hypotheses:", len(inf.hSpace_)
	# 	inf.duplicateHypotheses(True)
	# 	inf.sortHypotheses()
	# 	print "  best cost", inf.hSpace_[0][1]
	# 	print "  worst cost", inf.hSpace_[-1][1]
	# 	inf.hSpace_[0][0].printGraph("output/inference/trial-%d-best.png" % i)
	# 	inf.hSpace_[-1][0].printGraph("output/inference/trial-%d-worst.png" % i)
	# 	inf.cullHypotheses()

