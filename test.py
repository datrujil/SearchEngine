import os
from docmanager import DocManager
from bs4 import BeautifulSoup
import json
from pathlib import Path
from indexer import Indexer
import re
from nltk.stem import PorterStemmer


# run full directory
directory = './Information_Analyst_Data/www_cs_uci_edu'

# run specific directory only for quicker testing
# directory = 'cert_ics_uci_edu'    # can be any directory you choose

# DT - Partitioning variables
FILES_READ = 0
INDEX_FILE = 0
CURR_FILE = "index" + str(INDEX_FILE) + ".txt"

# DT - Determines how many files are read per partition before creating a new text file
FILES_THRESHOLD = 200

# create a document manager
my_doc_manager = DocManager()

# create an indexer
my_index = Indexer()

# get current working directory
cwd = os.getcwd()

# token pattern
token_pattern = r'\b[a-zA-Z0-9]+\b'

# DT - Token stemming function using Porter stemming
ps = PorterStemmer()

# crawl through each directory recursively and read all .json files
for file in Path(os.path.join(cwd, directory)).rglob('*.json'):
    # DT - Reset variables and increment indexer by 1 for memory efficiency and partitioning
    if FILES_READ > FILES_THRESHOLD:
        FILES_READ = 0
        INDEX_FILE += 1
        my_index = Indexer()
        CURR_FILE = "index" + str(INDEX_FILE) + ".txt"

    # open a json file
    with open(file, 'r', encoding='utf-8') as f:
        # print to console just to see progress
        print(file)
        # load the json file
        data = json.load(f)
        # extract url from json and add it to the document manager
        my_doc_manager.add_doc(file.name, data["url"])
        # obtain the document id that the document manager assigned it
        doc_id = my_doc_manager.get_doc_id(data["url"])

        # get contents of the json file
        soup = BeautifulSoup(data['content'], 'lxml')
        # read the content in sections
        for section in soup.stripped_strings:
            # create the token list for each section
            token_list = []
            token_list.extend(re.findall(token_pattern, section))
            for token in token_list:
                # DT - Stem the token
                token = ps.stem(token)
                # add token to the index and increment its frequency
                my_index.add_token_to_index(token)
                my_index.increment_frequency_posting(token, doc_id)

    # Write the current file's indexed postings to the current index file.
    my_index.write_postings_to_file(file_name=CURR_FILE)

    FILES_READ += 1

# print entire index
# my_index.print_index_frequency_posting(file_name="index.txt")

#my_index.print_index_frequency_posting2(file_name="index2.txt")
# print entire document manager for reference
my_doc_manager.print_manager(valid_file_name="valid.txt", invalid_file_name="invalid.txt")
