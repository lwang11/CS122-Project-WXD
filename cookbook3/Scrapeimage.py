
# learned online from https://gist.github.com/genekogan/ebd77196e4bf0705db51f86431099e57

import argparse
import json
import itertools
import logging
import re
import os
import uuid
import sys
from urllib.request import urlopen, Request

from bs4 import BeautifulSoup


def configure_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter('[%(asctime)s %(levelname)s %(module)s]: %(message)s'))
    logger.addHandler(handler)
    return logger

logger = configure_logging()

REQUEST_HEADER = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}


def get_soup(url, header):
    response = urlopen(Request(url, headers=header))
    return BeautifulSoup(response, 'html.parser')

def get_query_url(query):
    return "https://www.google.co.in/search?q=%s&source=lnms&tbm=isch" % query

def extract_images_from_soup(soup):
    image= soup.find_all("div", {"class": "rg_meta"})
    metadata_dict = (json.loads(e.text) for e in image)
    link_type_records = ((d["ou"], d["ity"]) for d in metadata_dict)
    return link_type_records

def extract_images(query, num_images):
    url = get_query_url(query)
    logger.info("Souping")
    soup = get_soup(url, REQUEST_HEADER)
    logger.info("Extracting image urls")
    link_type_records = extract_images_from_soup(soup)
    return itertools.islice(link_type_records, num_images)

def get_raw_image(url):
    request = Request(url, headers=REQUEST_HEADER)
    response = urlopen(request)
    return response.read()

def save_image(raw_image, image_type, save_directory):
    extension = image_type if image_type else 'jpg'
    file_name = uuid.uuid4().hex
    save_path = os.path.join(save_directory, file_name)
    with open(save_path, 'wb') as image_file:
        image_file.write(raw_image)

def download_images_to_dir(images, save_directory, num_images):
    for i, (url, image_type) in enumerate(images):
        try:
            logger.info("Making request (%d/%d): %s", i, num_images, url)
            raw_image = get_raw_image(url)
            save_image(raw_image, image_type, save_directory)
        except Exception as ex:
            logger.exception(ex)            

def run(query, save_directory, num_images=1):
    query = '+'.join(query.split())
    logger.info("Extracting image links")
    images = extract_images(query, num_images)
    logger.info("Downloading images")
    download_images_to_dir(images, save_directory, num_images)
    logger.info("Finished")


def get_title(json_filename):
    data = json.load(open(json_filename))
    title_set = set()
    for i in range(0, len(data)):
        d = data[i]
        if 'title' in d.keys():           
            title_set.add(d['title'])
    return title_set

title_set = get_title("full_format_recipes.json")

for i in title_set:
    run(i,'/Users/yangyangdai/desktop/food pic',1)  

