import json
from pprint import pprint
import nltk
import matplotlib.pyplot as plt
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

def read_and_preprocessing(json_filename, num_attribute, is_lower_case, is_stem,is_remove_stopwords, is_remove_puctuation, stemmer):
    data = json.load(open(json_filename))
    documents = []
    index_in_json = []
    title_set = set()
    word_set = set()
    cnt = 0
    len_data = str(len(data))

    for i in range(0, len(data)):
        if len(data[i]) == num_attribute and len(data[i]['ingredients']) != 0:
            if data[i]['title'] not in title_set:
                # if i > 5:
                #     break
                print(str(i) + '/' + len_data)
                title_set.add(data[i]['title'])
                index_in_json.append(i)
                ingredients = data[i]['ingredients']

                actual_ingredients = []
                for each_ingredient in ingredients:
                    if is_lower_case:
                        each_ingredient = each_ingredient.lower()

                    tokens = nltk.word_tokenize(each_ingredient)

                    if is_stem:
                        singles = [stemmer.stem(token) for token in tokens]

                    if is_remove_stopwords:
                        filtered_words = [word for word in singles if word not in stopwords.words('english')]
                    else:
                        filtered_words = singles
                    filtered_words_2 = []
                    if is_remove_puctuation:
                        for word in filtered_words:
                            if word.isalpha():
                                filtered_words_2.append(word)
                                word_set.add(word)
                        # filtered_words_2 = [word for word in filtered_words if word.isalpha()]
                    else:
                        filtered_words_2 = filtered_words
                    # print('-----------------------------------')
                    # print(filtered_words_2)
                    actual_ingredients = actual_ingredients + filtered_words_2
                documents.append(actual_ingredients)



    return index_in_json, documents, word_set



def save_func(filename, data):
    # print('start saving ' + filename)
    with open(filename, "wb") as fp1:
        pickle.dump(data, fp1)
    # print('end saving ' + filename)

def load_func(filename):
    # print('start loading ' + filename)
    with open(filename, "rb") as fp1:
        data = pickle.load(fp1)
    # print('end loading ' + filename)
    return data


stemmer = PorterStemmer()
is_lower_case = True
is_stem = True
is_remove_stopwords = True
is_remove_puctuation = True

name_documents = 'documents'
name_index_in_json = 'index_in_json'
name_word_set = 'word_set'
name_inverted_index = 'inverted_index'
num_attribute = 11
json_filename = 'full_format_recipes.json'
name_doc_length = 'doc_length'


# index_in_json, documents, word_set = read_and_preprocessing(json_filename, num_attribute, is_lower_case, is_stem,is_remove_stopwords, is_remove_puctuation, stemmer)
# save_func(name_documents, documents)
# save_func(name_index_in_json, index_in_json)
# save_func(name_word_set, word_set)

load_documents = load_func(name_documents)
load_index_in_json = load_func(name_index_in_json)
load_word_set = load_func(name_word_set)

print(len(load_documents))




