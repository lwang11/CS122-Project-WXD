
import json
import traceback
import sys
import csv
import os

from functools import reduce
from operator import and_

from django.shortcuts import render
from django import forms

from recipe import *

NOPREF_STR = 'No preference'
RES_DIR = os.path.join(os.path.dirname(__file__), '..', 'res')


class SearchForm(forms.Form):
    query = forms.CharField(
        label='Ingredients',
        help_text='e.g. eggs',
        required=True)
    
    without_food = forms.CharField(label='Unwanted Food', 
                                   help_text='e.g. onion', 
                                   required=False)
    

def home(request):
    result=None
    food_query = None
    if request.method == 'GET':
        form = SearchForm(request.GET)
        if form.is_valid():
            food_query = form.cleaned_data['query']
            without = form.cleaned_data['without_food']
            result = find_recipe('full_format_recipes.json', food_query, 5, without,
                                 load_index_in_json, load_documents, load_inverted_index, load_doc_length)

           
    else:
        form = SearchForm()
    return render(request, 'search/index.html', {'form': form,"result": result, "food_query": food_query})





