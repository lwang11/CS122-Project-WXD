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
                            word not in cur_customized_stopwords)]
                    else:
                        filtered_words = singles
                    filtered_words_2 = []
                    if is_remove_puctuation:
                        for word in filtered_words:
                            if word.isalpha():
                                filtered_words_2.append(word)
                                word_set.add(word)
                    else:
                        filtered_words_2 = filtered_words

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

        for i in range(0, len(documents)):
            index = index_in_json[i]
            document = documents[i]
            if each_word in document:
                inverted_index[each_word][0] = inverted_index[each_word][0] + 1
                inverted_index[each_word].append((i, document.count(each_word)))
    return inverted_index

def get_document_length(index_in_json, documents, inverted_index):
    doc_length = []
    for i in range(0, len(documents)):
        document = documents[i]
        length = 0.0
        for each_word in document:
            tf = math.log(document.count(each_word) + 1.0)
            idf = inverted_index[each_word][0]
            length = length + tf*idf*tf*idf
        doc_length.append(math.sqrt(length))
    return doc_length


def doc_ranking(k1, b, query, index_in_json, documents, inverted_index, doc_length):
    #preprocessing query
    N = len(documents)
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
    average_length = 0.0
    for each_doc in documents:
        average_length = average_length + len(each_doc)
    average_length = float(average_length) / len(documents)
    #doc doc_ranking
    doc_rank = {}
    query_length = 0.0
    for each_word in query_set:
        if each_word in inverted_index:
            for i in range(1, len(inverted_index[each_word])):
                document_index = inverted_index[each_word][i][0]
                document_count = inverted_index[each_word][i][1]
                tf_doc = float(document_count)
                df_doc = inverted_index[each_word][0]
                # doc_word_weight = tf_doc * idf_doc
                part_1 = (N - df_doc + 0.5) / float(df_doc + 0.5)
                part_2 = ((k1 + 1) * tf_doc) / (tf_doc + k1 * (1 - b + b * (len(documents[document_index]) / average_length)))
                # part_3 = ((k3 + 1) * tf_doc) / (k3 + tf_doc)
                if document_index not in doc_rank:
                    doc_rank[document_index] = 0.0
                doc_rank[document_index] = doc_rank[document_index] + math.log(part_1 * part_2)
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
    s=[]
    for i in range(0, top_n):
        a = []
        index = load_index_in_json[doc_index[i]]
        a.append(data[index]['title'][0:-1])
        c = ''
        for i in range(len(data[index]['ingredients'])):
            c += data[index]['ingredients'][i] + ", "

        a.append(c)
        b = ''
        for i in range(len(data[index]['directions'])):
            b += data[index]['directions'][i] + " "
        a.append(b)
        s.append(a)
    return s



def save_func(filename, data):
    with open(filename, "wb") as fp1:
        pickle.dump(data, fp1)

def load_func(filename):
    with open(filename, "rb") as fp1:
        data = pickle.load(fp1)
    return data

stemmer = PorterStemmer()
is_lower_case = True
is_stem = True
is_remove_stopwords = True
is_remove_puctuation = True

name_documents = 'documents_BM25'
name_index_in_json = 'index_in_json_BM25'
name_word_set = 'word_set_BM25'
name_inverted_index = 'inverted_index_BM25'
num_attribute = 11
json_filename = 'full_format_recipes.json'
name_doc_length = 'doc_length_BM25'

k1 = 1.2
b = 0.75
customized_stopwords = {"spoon", "cups", "large",
    "teaspoon", "medium", "small", "Freshly", "sheets", "pound",
    "tablespoon", "ounce", "lb"}


load_documents = load_func(name_documents)
load_index_in_json = load_func(name_index_in_json)
load_word_set = load_func(name_word_set)
load_inverted_index = load_func(name_inverted_index)
load_doc_length = load_func(name_doc_length)

def find_recipe(json_filename, query, top_n, without_food, load_index_in_json, load_documents, load_inverted_index, load_doc_length):
    doc_rank = doc_ranking(k1, b, query, load_index_in_json, load_documents, load_inverted_index, load_doc_length)
    sorted_doc_rank = sorted(doc_rank.items(), key=operator.itemgetter(1), reverse=True)
    data = json.load(open(json_filename))
    for i in range(0, top_n):
        index = load_index_in_json[sorted_doc_rank[i][0]]
    
    filtered_doc_index = delete_food(sorted_doc_rank, load_documents, without_food)
    
    dt = get_data(json_filename, top_n, filtered_doc_index, load_documents)

    return dt
