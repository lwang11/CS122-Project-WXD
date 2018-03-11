# CS122-Project-
CS122 2018 Group Project

Data downloaded from https://www.kaggle.com/hugodarwood/epirecipes/data

Scripts in our project:
1.	Vector_space.py, a python file containing data preprocessing and vector space model construction
2.	BM25.py, a python file containing data preprocessing and probabilistic BM-25 model construction
3.	Scrapeimage.py, a python file scraping image from google

Files in our project:

All results are saved to shorten running time.
1.	For Vector_space.py, doc_length, documents, index_in_json, inverted_index, word_set are saved
2.	For BM25.py, doc_length_BM25, documents_BM25, index_in_json_BM25, inverted_index_BM25, word_set_BM25 are saved

To run the project:
1.	Install pip in your terminal (if have not done so)
2.	Go to “Cookbook” folder, run:
python3 manage.py runserver
3.	Go to 127.0.0.1:8000/search/

Responsibilities:
1.	Data Preprocessing: Wenxi Xiao 
2.	Build models and algorithms: Lerong Wang, Wenxi Xiao, Yangyang Dai
3.	Django user interface: Lerong Wang, Yangyang Dai


