import json
from pprint import pprint
import nltk

import math
import string
from nltk.corpus import stopwords
from nltk.stem.porter import *
import csv
import pickle
from sklearn import svm
from sklearn import preprocessing
import operator
from collections import OrderedDict
from recipe import *


with open("index_in_json", "rb") as fp1:
        load_index_in_json = pickle.load(fp1)

with open("documents", "rb") as fp2:
        load_documents = pickle.load(fp2)

with open("inverted_index", "rb") as fp3:
        load_inverted_index = pickle.load(fp3)

with open("doc_length", "rb") as fp4:
        load_doc_length = pickle.load(fp4)


def find_recipe(json_filename, query, top_n, without_food, load_index_in_json, load_documents, load_inverted_index, load_doc_length):
    


    doc_rank = doc_ranking(query, load_index_in_json, load_documents, load_inverted_index, load_doc_length)
    sorted_doc_rank = sorted(doc_rank.items(), key=operator.itemgetter(1), reverse=True)
    data = json.load(open(json_filename))
    for i in range(0, 5):
        index = load_index_in_json[sorted_doc_rank[i][0]]
    
    filtered_doc_index = delete_food(sorted_doc_rank, load_documents, without_food)
    
    data = get_data(json_filename, top_n, filtered_doc_index, load_documents)

    return data