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

def read_and_preprocessing(json_filename, num_attribute, is_lower_case,
    is_stem,is_remove_stopwords, is_remove_puctuation, stemmer, customized_stopwords):
    data = json.load(open(json_filename))
    documents = []
    index_in_json = []
    title_set = set()
    word_set = set()
    cnt = 0
    len_data = str(len(data))
    cur_customized_stopwords = set()

    for i in range(0, len(data)):
        if len(data[i]) == num_attribute and len(data[i]['ingredients']) != 0:
            if data[i]['title'] not in title_set:
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
                        for ele in customized_stopwords:
                            cur_customized_stopwords.add(stemmer.stem(ele))

                    if is_remove_stopwords:
                        filtered_words = [word for word in singles if (word
                            not in stopwords.words('english') and
                            (word not in cur_customized_stopwords))]

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


def generate_inverted_index(index_in_json, documents, word_set):

    N = len(documents)
    num_word = len(word_set)
    cur_word = 0
    inverted_index = {}
    for each_word in word_set:
        inverted_index[each_word] = [0]
        cur_word = cur_word + 1
        print(cur_word, num_word)

        for i in range(0, len(documents)):
            index = index_in_json[i]
            document = documents[i]
            # print(each_word)
            # print(document)
            if each_word in document:
                inverted_index[each_word][0] = inverted_index[each_word][0] + 1
                # inverted_index[each_word].append((index, document.count(each_word)))
                inverted_index[each_word].append((i, document.count(each_word)))
        inverted_index[each_word][0] = 1.0 + math.log(float(N) / float(inverted_index[each_word][0]))
    return inverted_index


def get_document_length(index_in_json, documents, inverted_index):
    doc_length = []
    for i in range(0, len(documents)):
        document = documents[i]
        length = 0.0
        print(i,len(documents))
        for each_word in document:
            tf = math.log(document.count(each_word) + 1.0)
            idf = inverted_index[each_word][0]
            length = length + tf*idf*tf*idf
        doc_length.append(math.sqrt(length))
    return doc_length


def doc_ranking(query, index_in_json, documents, inverted_index, doc_length):
    #preprocessing query
    query_set = set()
    if is_lower_case:
        query = query.lower()
    tokens = nltk.word_tokenize(query)
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
                query_set.add(word)
    else:
        filtered_words_2 = filtered_words
    print(filtered_words_2)
    #doc doc_ranking
    doc_rank = {}
    query_length = 0.0
    for each_word in query_set:
        if each_word in inverted_index:
            tf_query = math.log(filtered_words_2.count(each_word) + 1.0)
            idf_query = inverted_index[each_word][0]
            query_word_weight = tf_query * idf_query
            query_length = query_length + query_word_weight*query_word_weight
            for i in range(1, len(inverted_index[each_word])):
                document_index = inverted_index[each_word][i][0]
                document_count = inverted_index[each_word][i][1]
                tf_doc = math.log(document_count + 1.0)
                idf_doc = inverted_index[each_word][0]
                doc_word_weight = tf_doc * idf_doc
                if document_index not in doc_rank:
                    doc_rank[document_index] = 0.0
                doc_rank[document_index] = doc_rank[document_index] + doc_word_weight * query_word_weight

    query_length = math.sqrt(query_length)
    for document_index in doc_rank:
        doc_rank[document_index] = float(doc_rank[document_index]) / (query_length * doc_length[document_index])
    return doc_rank

def delete_food(sorted_doc_rank, documents, without_food):
    if len(without_food) == 0:
        filtered_doc_index = []
        for ele in sorted_doc_rank:
            index = ele[0]
            filtered_doc_index.append(index)
    else:
        without_food_set = set()
        if is_lower_case:
            without_food = without_food.lower()
        tokens = nltk.word_tokenize(without_food)
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
                    without_food_set.add(word)
        else:
            filtered_words_2 = filtered_words
        filtered_doc_index = []
        for ele in sorted_doc_rank:
            index = ele[0]
            is_valid = True
            for each_no_word in without_food_set:
                if each_no_word in documents[index]:
                    is_valid = False
                    break
            if is_valid:
                filtered_doc_index.append(index)
    return filtered_doc_index



def get_data(json_filename, top_n, doc_index, documents):
    data = json.load(open(json_filename))
    to_print ={}
    for i in range(0, top_n):
        index = load_index_in_json[doc_index[i]]
        to_print['title'] = data[index]['title']
        to_print['ingredients'] = documents[doc_index[i]]
        # data[index]['ingredients']

        print('title: ' + data[index]['title'] + ' ' + str(len(documents[doc_index[i]])))
        print(documents[doc_index[i]])
        print('------------------------------------------')



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

customized_stopwords = {"spoon", "cups", "large",
    "teaspoon", "medium", "small", "Freshly", "sheets", "pound",
    "tablespoon", "ounce", "lb"}

index_in_json, documents, word_set = read_and_preprocessing(json_filename, num_attribute, is_lower_case, is_stem,is_remove_stopwords, is_remove_puctuation, stemmer, customized_stopwords)

save_func(name_documents, documents)
save_func(name_index_in_json, index_in_json)
save_func(name_word_set, word_set)
#
# load_documents = load_func(name_documents)
# load_index_in_json = load_func(name_index_in_json)
# load_word_set = load_func(name_word_set)
#
#
# # inverted_index = generate_inverted_index(load_index_in_json, load_documents, load_word_set)
# # save_func(name_inverted_index, inverted_index)
# load_inverted_index = load_func(name_inverted_index)
#
# # doc_length = get_document_length(load_index_in_json, load_documents, load_inverted_index)
# # save_func(name_doc_length, doc_length)
# load_doc_length = load_func(name_doc_length)
#
# query = 'potato, beef'
#
# doc_rank = doc_ranking(query, load_index_in_json, load_documents, load_inverted_index, load_doc_length)
# sorted_doc_rank = sorted(doc_rank.items(), key=operator.itemgetter(1), reverse=True)
# # pprint(sorted_doc_rank[0:8])
# # data = json.load(open(json_filename))
# # for i in range(0, 5):
# #     index = load_index_in_json[sorted_doc_rank[i][0]]
# #     pprint(data[index])
#
# # without_food = 'olive oil'
# # without_food = ''
# without_food = 'mushroom'
# filtered_doc_index = delete_food(sorted_doc_rank, load_documents, without_food)
# # print(filtered_doc_index[0:5])
# top_n = 5
# get_data(json_filename, top_n, filtered_doc_index, load_documents)
#
# #
