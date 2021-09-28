#!/usr/bin/env python3
import time
import pymp
import argparse
import re

# Reads the text of the provided file, and
#   splits it into a list including punctuation.
# Returns: the list of all split items.
def loadAllWords(file_name):
    with open(file_name, 'r') as file:
        words = file.read()
    return re.findall(r"[\w']+|[.,!?;]", words)


# Counts the amount of times the provided word is within
#   the provided list of words. Only exact matches are counted.
#   If you search for 'love', 'self-love' will not be count.
# Returns: the number of times the word is counted.
def wordFrequency(word, words):
    count = 0
    for i in words:
        if word.lower() == i.lower():
            count += 1
    return count


# Counts the given words in the given documents,
#   in parallel by splitting the words among processes.
# Returns: the shared dictionary containing the words and freq.
def countByWordsParallel(fileNames, searchedWords):
    # We need a shared dictionary
    wordDict = pymp.shared.dict()
    
    # Load all of the words
    words = []
    for name in fileNames:
        words += loadAllWords(name)
    
    # Using PYMP for parallel.
    with pymp.Parallel() as p:
        # Iterate though the list of words.
        for word in p.iterate(searchedWords):
            print(f'Thread {p.thread_num} of {p.num_threads} is evaluating word \'{word}\'')
            wordDict[word] = wordFrequency(word, words)
            
    # Return the shared dictionary of words and frequency.
    return wordDict
    
# Counts the given words in the given documents,
#   in serial, by iterating through the words.
# Returns: the dictionary containing the words and freq.
def countByWordsSerial(fileNames, searchedWords):
    # We need a shared dictionary
    wordDict = dict()
    
    # Load all of the words
    words = []
    for name in fileNames:
        words += loadAllWords(name)
    
    for word in searchedWords:
        wordDict[word] = wordFrequency(word, words)
            
    # Return the shared dictionary of words and frequency.
    return wordDict


# Counts the given words in the given documents,
#   in parallel by splitting the documents among processes.
# Returns: the shared dictionary containing the words and freq.
def countByDocumentsParallel(fileNames, searchedWords):
    # We need a shared dictionary
    wordDict = pymp.shared.dict()
    
    # Using PYMP for parallel.
    with pymp.Parallel() as p:
        # Add lock to control access to the list.
        lock = p.lock
        
        # Initialize the shared dictionary with the words.
        for i in p.range(len(searchedWords)):
            wordDict[searchedWords[i]] = 0
        
        # Iterate through the list of documents.
        for name in p.iterate(fileNames):
            print(f'Thread {p.thread_num} of {p.num_threads} is evaluating document {name}')
            words = loadAllWords(name)
            
            # We need a dictionary for each document.
            tempDict = dict()
            
            # Update the dictionary with the word and frequency.
            for word in searchedWords:
                tempDict[word] = wordFrequency(word, words)
                
            # We have to engage the lock, allowing the current process
            # to be able to update the frequency without any other
            # process accessing it at the same time.
            lock.acquire()
            
            for word, freq in tempDict.items():
                wordDict[word] += freq
                
            # Finished updating the frequency, we can now
            # release the lock, so other processes can access it.
            lock.release()
            
    return wordDict

# Counts the given words in the given documents,
#   in serial by iterating through the documents.
# Returns: the dictionary containing the words and freq.
def countByDocumentsSerial(fileNames, searchedWords):
    # We need a shared dictionary
    wordDict = dict()
    
    # Initialize the dictionary with the words.
    for word in searchedWords:
        wordDict[word] = 0
    
    # Iterate through the list of documents.
    for name in fileNames:
        words = loadAllWords(name)
        
        # Update the dictionary with the word and frequency.
        for word in searchedWords:
            wordDict[word] += wordFrequency(word, words)
    
    return wordDict


def main():
    parser = argparse.ArgumentParser(description=
    'Counts the frequency of words within the work of Shakespeare,'
    'using PYMP for running in parallel on multiple processes.'
    'Process the words by either distributing the words'
    'or documents among the available amount of processes.')
    parser.add_argument('-e', '--expected', action='store_true',
    help = 'Print out the expected frequency results.')
    parser.add_argument('-w', '--word', action='store_true',
    help = 'Count frequency by iterating through words.')
    parser.add_argument('-d', '--document', action='store_true',
    help = 'Count frequency by iterating through documents.')
    parser.add_argument('-p', '--parallel', action='store_true',
    help = 'Indicates running in parallel, word or document per process.')

    args = parser.parse_args()
    
    # Starting time of the program
    startTimeMaster = time.monotonic()
    
    # List of all the file names.
    fileNames = ['shakespeare1.txt', 'shakespeare2.txt', 'shakespeare3.txt', 
                 'shakespeare4.txt', 'shakespeare5.txt', 'shakespeare6.txt', 
                 'shakespeare7.txt', 'shakespeare8.txt']

    # The list of words we will be counting
    wordsList = ['hate', 'love', 'death', 'night', 
                 'sleep', 'time', 'henry', 'hamlet', 
                 'you', 'my', 'blood', 'poison', 
                 'macbeth', 'king', 'heart', 'honest']
    
    # The real amount of times each word is within the documents.
    realWordFreq = {'blood': 719, 'death': 963, 'hamlet': 474, 'hate': 188,
                    'heart': 1124, 'henry': 612, 'honest': 309, 'king': 3033,
                    'love': 2399, 'macbeth': 288, 'my': 13184, 'night': 825,
                    'poison': 98, 'sleep': 272, 'time': 1180, 'you': 14580}
    
    
    result = dict({})
    
    if args.parallel:
        if args.word:
            startTimeWord = time.monotonic()
            result = countByWordsParallel(fileNames, wordsList)
            elapsed = time.monotonic() - startTimeWord
        if args.document:
            startTimeDocument = time.monotonic()
            result = countByDocumentsParallel(fileNames, wordsList)
            elapsed = time.monotonic() - startTimeDocument
    else:
        if args.word:
            startTimeWord = time.monotonic()
            result = countByWordsSerial(fileNames, wordsList)
            elapsed = time.monotonic() - startTimeWord
        if args.document:
            startTimeDocument = time.monotonic()
            result = countByDocumentsSerial(fileNames, wordsList)
            elapsed = time.monotonic() - startTimeDocument
    
    # Test results match from algorithm to algorithm and print
    if args.expected:
        print('Expected words and frequency:')
        for word, freq in realWordFreq.items():
            print(f'\t{word} - {freq}')
    
    if result != {}:
        print('Searched words and frequency:')
        for word, freq in sorted(result.items()):
            print(f'\t{word} - {freq}')
        print('Total search time: %.4f seconds' % elapsed)
        print('Total run time: %.4f seconds' % (time.monotonic() - startTimeMaster))
    
    
if __name__ == '__main__':
    main()
