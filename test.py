import os
from docmanager import DocManager
from bs4 import BeautifulSoup
import json
from pathlib import Path
from indexer import Indexer
import re


# run full directory
directory = 'DEV'

# run specific directory only for quicker testing
# directory = 'cert_ics_uci_edu'    # can be any directory you choose


# create a document manager
my_doc_manager = DocManager()

# create an indexer
my_index = Indexer()

# get current working directory
cwd = os.getcwd()

# token pattern
token_pattern = r'\b[a-zA-Z0-9]+\b'
# crawl through each directory recursively and read all .json files
for file in Path(os.path.join(cwd, directory)).rglob('*.json'):
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
                # add token to the index and increment its frequency
                my_index.add_token_to_index(token)
                my_index.increment_frequency_posting(token, doc_id)

# print entire index
my_index.print_index_frequency_posting(file_name="index1.txt")
#my_index.print_index_frequency_posting2(file_name="index2.txt")
# print entire document manager for reference
my_doc_manager.print_manager(valid_file_name="valid.txt", invalid_file_name="invalid.txt")
