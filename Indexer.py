from Postings import Postings
from DocManager import DocManager
from nltk.stem import PorterStemmer
from pathlib import Path
import json
from bs4 import BeautifulSoup
import re


class Indexer:
    def __init__(self):
        self._index = {}                        # {token : Postings()}
        self._doc_manager = DocManager()        # indexer has a document manager

    def create_index(self, directory):
        # create a path object based on the directory given
        path = Path(directory)
        if not path.exists():
            print("Invalid Directory!")

        # recursively iterate through each json file and tokenize it into the index
        token_pattern = r'\b[a-zA-Z0-9]+\b'
        for file in path.rglob('*.json'):
            with open(file, 'r', encoding='utf-8') as curr_json_file:
                # can delete --- just to track progress on the console
                print(curr_json_file.name)

                # load json file and get a document id
                data = json.load(curr_json_file)
                doc_id = self._doc_manager.add_doc(file.name, data)

                # get the html content of the document
                soup = BeautifulSoup(data['content'], 'lxml')

                # read the soup section by section
                for section in soup.stripped_strings:
                    # create a token list for each section
                    token_list = []
                    token_list.extend(re.findall(token_pattern, section))

                    # add token to the index and increment its frequency
                    for token in token_list:
                        token = self._normalize_token(token)
                        self._add_token_to_index(token)
                        self._increment_frequency_postings(token, doc_id)

        self._write_index_frequency_postings_to_file()
        self._write_doc_manager_to_file()

    # add a token as the key, and a Postings Object as its value --> {token : Postings()}
    def _add_token_to_index(self, token):
        if token not in self._index:
            self._index[token] = Postings()

#################################################################### FREQUENCY POSTING METHODS ONLY
    def _increment_frequency_postings(self, token, doc_id):
        postings = self._get_token_postings(token)
        if postings:
            postings.increment_frequency_posting(doc_id)

    def _write_index_frequency_postings_to_file(self):
        with open(f'Indexer{self._partial_index_number}.txt', 'w', encoding='utf-8') as output:
            output.write(f"total tokens = {len(self._index)}\n")
            for token, postings in self._index.items():
                output.write(f"token = {token}\n")
                postings.write_frequency_posting_to_file(output)
#################################################################### FREQUENCY POSTING METHODS ONLY

    def _write_doc_manager_to_file(self):
        self._doc_manager.write_doc_manager_to_file()

    def _get_token_postings(self, token):
        return self._index[token]

    def _normalize_token(self, token):
        return PorterStemmer().stem(token.lower())
