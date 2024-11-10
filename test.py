import os
from docmanager import DocManager
from bs4 import BeautifulSoup
import lxml
import json
from pathlib import Path
from indexer import Indexer
import re


directory = 'DEV'
my_doc_manager = DocManager()
my_index = Indexer()

cwd = os.getcwd()
for file in Path(os.path.join(cwd, "cert_ics_uci_edu")).rglob('*.json'):
    token_pattern = r'\b[a-zA-Z0-9]+\b'
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        my_doc_manager.add_url(data["url"])
        doc_id = my_doc_manager.get_url_doc_id(data["url"])
        if doc_id == 26: print(file)
        soup = BeautifulSoup(data['content'], 'lxml')
        for section in soup.stripped_strings:
            token_list = [token.lower() for token in section.split() if re.match(token_pattern, token)]

            for token in token_list:
                my_index.add_token_to_index(token)
                my_index.increment_frequency_posting(token, doc_id)

my_index.print_index_frequency_posting(file_name="index.txt")
