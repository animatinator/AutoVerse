# Markov stuff
# TODO only use words from a supplied dictionary
# TODO put everything in lowercase then convert to title case. Will be fine as only
# dictionary words will be used - no proper nouns.

import bisect
import re
import string
from collections import defaultdict
import random


# Things to ignore
BAD_FILE_CONTENT = ['\n', '"', '\' ', ' \'', '(', ')']
# Punctuation which we should treat as (zero-syllable) words
KEY_PUNCTUATION = [",", ".", "!", "?", ";", "--"]

# Load the content of a file
def loadFileContent(filename):
	infile = open(filename, "r")
	content = infile.read()
	infile.close()
	return content

# Condense sequences of spaces into single spaces
def condenseSpaces(content):
	content = re.sub(r'( )+', ' ', content)
	return content

# Add spaces around KEY_PUNCTUATION characters so they can be split out as words
def expandKeyPunctuation(content):
	for symbol in KEY_PUNCTUATION:
		content = content.replace(symbol, " %s " % symbol)
	return content

# Remove extra spacing around KEY_PUNCTUATION characters
def contractKeyPunctuation(content):
	for symbol in KEY_PUNCTUATION:
		content = content.replace(" %s" % symbol, symbol)
	return content

# Remove unwanted characters from a string
def filterBadContent(content):
	for thing in BAD_FILE_CONTENT:
		content = content.replace(thing, " ")
	return content

# Sanitise the raw content of a file for processing
# We first filter unwanted characters, then add spacing around punctuation we want to be
# treated as words. With this done, we condense groups of spaces into single spaces, and
# return the result.
def sanitiseFileContent(content):
	# TODO For iambic pentameter, we should avoid full stops but use commas. We should
	# also remove capital letters, probably?
	content = filterBadContent(content)
	content = expandKeyPunctuation(content)
	return condenseSpaces(content)

# Split a string into words (splitting on spaces)
def splitIntoWords(content):
	return content.split(" ")

# Load a file, sanitise it and return the list of words
def loadAndParseFile(filename):
	fileContent = loadFileContent(filename)
	sanitised = sanitiseFileContent(fileContent)
	words = splitIntoWords(sanitised)
	return words

# In a [[string, int]] list (list of words and their frequencies), either add this new
# word with frequency set to 1 or increment its frequency
# TODO shouldn't this just be a string->int map? Need to iterate, though...
def incrementWordCountInList(word, list):
	if list == []:
		return [[word, 1]]
	
	for item in list:
		if item[0] == word:
			item[1] += 1
			return list
	list.append([word, 1])
	return list

# Build a map from (string, string) -> [[string, int]] which indicates the possible next
# choices and their frequencies in the source text
# TODO generalise to n-grams?
def buildMap(words):
	if len(words) < 3:
		return {}
	
	markovMap = defaultdict(list)
	
	for i in xrange(0, len(words) - 3):
		mapEntry = markovMap[(words[i], words[i+1])]
		markovMap[(words[i], words[i+1])] = incrementWordCountInList(words[i+2], mapEntry)

	return markovMap


# Add a full stop to the end of the supplied text if it doesn't already end with one
def maybeAddFullStop(sentence):
	if sentence[-1] != '.':
		return sentence + "."
	return sentence

# Take a raw list of generated words and join them, removing surplus padding around
# punctuation
def formSentence(words):
	joined = " ".join(words)
	contracted = contractKeyPunctuation(joined)
	return maybeAddFullStop(contracted)

# Given a list of probabilities, select an index by the roulette wheel approach
def rouletteWheelSelection(integers):
	cumulativeValues = []
	total = 0
	
	for integer in integers:
		total += integer
		cumulativeValues.append(total)

	rouletteValue = random.randint(0, total)
	rouletteIndex = bisect.bisect_left(cumulativeValues, rouletteValue)
	return rouletteIndex

# Generate the next word based on the last two and the Markov map
def generateNextWord(markovMap, first, second):
	possibilities = markovMap[(first, second)]
	selectedIndex = rouletteWheelSelection([entry[1] for entry in possibilities])
	return possibilities[selectedIndex][0]

# Generate a sequence of words of a specified length from a Markov map
def generateSentence(markovMap, numWords):
	# TODO pick seed words properly - need probabilities of sentence starting with a given
	# bigram
	output = ["It", "was"]
	for i in xrange(2, numWords):
		output.append(generateNextWord(markovMap, output[i-2], output[i-1]))
	return formSentence(output)



# Testing the code. Load and parse a source corpus, build a Markov map from it and use that
# to generate 100 words of high-quality literature.
if __name__ == '__main__':
	words = loadAndParseFile("data/dickens.txt")
	map = buildMap(words)
	print generateSentence(map, 100)
