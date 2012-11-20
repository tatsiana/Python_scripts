#!/usr/bin/python
#
__author__ = 'Tatsiana Maskalevich'


""" to run pass two arguments: input log file and where to output
    Accumulate search_term,frequency pairs from AOL search logs. 
    Use predefined local_search_model_keywords as SEARCH_TERMS """

import csv
import collections
import pprint
import re
import sys
from sets import Set


def ngrams(sequence, n, pad_left=False, pad_right=False, pad_symbol=None):
    """
    http://stackoverflow.com/questions/2380394/simple-implementation-of-n-gram-tf-idf-and-cosine-similarity-in-python
    A utility that produces a sequence of ngrams from a sequence of items.
    For example:

    >>> ngrams([1,2,3,4,5], 3)
    [(1, 2, 3), (2, 3, 4), (3, 4, 5)]

    Use ingram for an iterator version of this function.  Set pad_left
    or pad_right to true in order to get additional ngrams:

    >>> ngrams([1,2,3,4,5], 2, pad_right=True)
    [(1, 2), (2, 3), (3, 4), (4, 5), (5, None)]
    """

    if pad_left:
        sequence = chain((pad_symbol,) * (n-1), sequence)
    if pad_right:
        sequence = chain(sequence, (pad_symbol,) * (n-1))
    sequence = list(sequence)

    count = max(0, len(sequence) - n + 1)
    return [tuple(sequence[i:i+n]) for i in range(count)] 


def CSV_writer(dictionary, file_name):

	writer = csv.writer(open(file_name, 'wb'))
	for key, value in dictionary.iteritems():
		writer.writerow([key,value])



if __name__ == "__main__":

    csv_doc = sys.argv[1]
    csv_out = sys.argv[2]

    # in case we need to prettyprint anything
    pp = pprint.PrettyPrinter(indent=4)
    
    ''' initiate dictionary for the final inverted set'''
    inverted_index_set = collections.defaultdict(list)


    ''' read the model values and parse + dedupe them so that we only have key phrases'''
    reader = csv.reader(open('local_suggestions_model.txt', 'rb'), 
                             delimiter = '\t')
    # key,value pairs
    search_words_values = []
    search_words_keys=[]
    for row in reader:
        row[1] = row[1].split('-')[0]
        row[1] = re.sub(r'eateries','',row[1])
        row[1] = row[1].strip().lower()
        word1 = row[1]
        search_words_keys.append(word1)
        if len(word1)== 1 and word1[-1:] == 's':
            search_words_keys.append(word1[-1:])
            search_words_keys.append(word1[-2:])

    # dedupe the model_kewords    
    search_words_keys = list(Set(search_words_keys))
    # hash map with phrase : index
    model_dict = dict(zip(search_words_keys,xrange(len(search_words_keys))))
    # hash map with index : phrase
    model_dict_inverted = dict(zip(xrange(len(search_words_keys)),search_words_keys))
    # hash map word : index (non-unique)
    words_dicts = collections.defaultdict(list)
    for key, value in model_dict.iteritems():
        new_key = key.split()
        for k in new_key:
            words_dicts[k].append(value)

    #print words_dicts

    # write model as enumerated list into a csv file
    CSV_writer(model_dict, 'model_key_value.csv')
    CSV_writer(model_dict_inverted, 'model_key_value_inverted.csv')
    CSV_writer(words_dicts, 'model_words_value.csv')

    #open aol log
    aol_reader = csv.reader(open(csv_doc, 'rb'), delimiter = '\t')
    aol_reader.next()
    print 'Starting Processing!'
    n = 0
    sample4processing = []
    for line in aol_reader:
        n += 1
        term = line[1].strip().lower()
        terms = term.split()
        #sanity!
        if n%1000 == 0:
            print 'Processed', n, 'results'
        set_values = []
        set_keys = []
        temp_dict = collections.defaultdict(list)

        # unigrams check 
        for t in terms:
            match = words_dicts.get(t)

            if match != None:
                set_keys.append(t)
                set_values.append(set(match))
                temp_dict[t].append(set(match))


        # unigrams
        if len(terms) == 1 and set_keys:
            print set_keys[0] in model_dict.keys()
            if set_keys[0] in model_dict.keys():
                inverted_index_set[model_dict[set_keys[0]]].append(1)
        #bigrams
        if len(set_keys) > 1:
            bi_grams = ngrams(set_keys, 2)
            for bi_gram in bi_grams:
                (w1,w2) = bi_gram
                intersection = set.intersection(temp_dict[w1][0],temp_dict[w2][0])
                if list(intersection) and len(bi_gram) == len( model_dict_inverted[list(intersection)[0]].split()):
                    inverted_index_set[list(intersection)[0]].append(1)
        #trigrams
        if len(set_keys) > 2:
            print 'More than 3'
            tri_grams = ngrams(set_keys, 3)
            for tri_gram in tri_grams:
                (w1,w2,w3) = tri_gram
                intersection = set.intersection(temp_dict[w1][0],temp_dict[w2][0],temp_dict[w3][0])
                if list(intersection) and len(tri_gram) == len( model_dict_inverted[list(intersection)[0]].split()):
                    inverted_index_set[list(intersection)[0]].append(1)


    print 'Done processing!'
    #print inverted_index_set
    #ouput into file
    writer = csv.writer(open(csv_out, 'wb'))
    tuples_counts = []
    for index,counts in inverted_index_set.iteritems():
    #    print index,counts
        tuples_counts.append((model_dict_inverted[index], sum(counts)))
        writer.writerow([model_dict_inverted[index],sum(counts)])


    #print tuples_counts


