import re
import json
from Postings import Postings
from DocManager import DocManager
from nltk.stem import PorterStemmer
from pathlib import Path
from bs4 import BeautifulSoup


# creates partial indexes
class Indexer:
    def __init__(self):
        self._index = {}                                    # {token : Postings()}
        self._doc_manager = DocManager()                    # Indexer has a document manager
        self._current_size = 0                              # Track number of JSON files visited
        self._threshold = 5000                              # JSON File limit
        self.file_num = 1                                   # Initialize file number for indexing
        self.current_file = f"index{self.file_num}.json"    # Partial index dump

    def create_index(self, directory):
        # Create a path object based on the directory given
        path = Path(directory)
        if not path.exists():
            print("Invalid Directory!")
            return

        # Tokenization regex pattern
        token_pattern = r'\b[a-zA-Z0-9]+\b'

        # Recursively iterate through each JSON file in the directory
        for file in path.rglob('*.json'):
            with open(file, 'r', encoding='utf-8') as curr_json_file:
                # For tracking progress
                print(curr_json_file.name)

                # Load JSON file and get a document ID
                data = json.load(curr_json_file)
                doc_id = self._doc_manager.add_doc(file.name, data)

                # Parse HTML content
                # lxml parser handles broken html
                soup = BeautifulSoup(data['content'], 'lxml')

                # Process each section of the content; a section is html content between tags as to not load entire
                # html content at once
                for section in soup.stripped_strings:
                    token_list = re.findall(token_pattern, section)

                    # Process each token in the section
                    for token in token_list:
                        token = self._normalize_token(token)
                        self._add_token_to_index(token, doc_id)

            # check if threshold has been reached - if it has, dump partial index
            self._current_size += 1
            if self._current_size >= self._threshold:
                self._write_index_to_file()
                self._reset_index()

        # Final write after indexing is complete
        self._write_index_to_file()
        self._write_doc_manager_to_file()

    def _add_token_to_index(self, token, doc_id):
        if token not in self._index:
            self._index[token] = Postings()

        # Update the posting for the token with the document ID
        self._increment_frequency_postings(token, doc_id)

    # access a token's frequency posting and increment it
    def _increment_frequency_postings(self, token, doc_id):
        postings = self._get_token_postings(token)
        if postings:
            postings.increment_frequency_posting(doc_id)

    # write the index into a json file
    def _write_index_to_file(self):
        index_data = {
            "total_tokens": len(self._index),
            "frequency index": {}
        }

        # Sort tokens alphabetically and add them to the dictionary
        for token in sorted(self._index.keys()):
            postings = self._get_token_postings(token)
            index_data["frequency index"][token] = postings.to_dict()

        with open(self.current_file, 'w', encoding='utf-8') as output:
            json.dump(index_data, output, indent=4)

        print(f"Index written to {self.current_file}")

    # writes the document manager for this specific index into a text file
    def _write_doc_manager_to_file(self):
        self._doc_manager.write_doc_manager_to_file()

    # Resets the index and increments the file name
    def _reset_index(self):
        self._index = {}
        self._current_size = 0                    # Reset index size counter
        self.file_num += 1
        self.current_file = f"index{self.file_num}.json"

    # retrieve a token's postings value
    def _get_token_postings(self, token):
        return self._index[token]

    # stem a token
    def _normalize_token(self, token):
        return PorterStemmer().stem(token.lower())