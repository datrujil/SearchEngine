import os.path
import re
import json
from Postings import Postings
from DocManager import DocManager
from nltk.stem import PorterStemmer
from pathlib import Path
from bs4 import BeautifulSoup
from collections import defaultdict
import math


# creates partial indexes
class Indexer:
    def __init__(self):
        self._index = {}                                    # {token : Postings()}
        self._doc_manager = DocManager()                    # Indexer has a document manager
        self._current_size = 0                              # Track number of JSON files visited
        self._threshold = 5000                              # JSON File limit
        self._num_docs = 0                                  # number of documents indexed

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

                # keep track of largest doc_id assigned
                if self._num_docs < doc_id:
                    self._num_docs = doc_id

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
        self._merge_postings()

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
    def _write_index_to_file(self, output_folder="Indexes"):
        for token, postings in self._index.items():
            first_letter = token[0]
            file_name = os.path.join(output_folder, f'{first_letter}.txt')
            with open(file_name, 'a', encoding='utf-8') as output:
                output.write(f'token = {token}\n')
                for docID, frequency in postings.to_dict().items():
                    frequency = self._convert_tf(frequency)
                    output.write(f'({docID},{frequency})\n')

    def _merge_postings(self, output_folder="Indexes"):
        # Ensure the folder exists
        if not os.path.exists(output_folder):
            print(f"Output folder '{output_folder}' does not exist!")
            return

        # Process each file in the folder
        for file_name in os.listdir(output_folder):
            file_path = os.path.join(output_folder, file_name)

            # Dictionary to store merged postings for tokens
            token_postings = defaultdict(dict)

            # Read the file and aggregate postings
            with open(file_path, 'r', encoding='utf-8') as file:
                current_token = None
                for line in file:
                    if line.startswith('token ='):
                        current_token = line.strip().split(' = ')[1]
                    elif current_token and line.startswith('('):  # Posting line
                        posting = line.strip("()\n").split(',')
                        doc_id = int(posting[0])
                        freq = float(posting[1])
                        token_postings[current_token][doc_id] = (
                                round(token_postings[current_token].get(doc_id, 0) + freq, 2)
                        )

            # Rewrite the file with merged postings
            with open(file_path, 'w', encoding='utf-8') as file:
                for token in sorted(token_postings.keys()):  # Sorted tokens
                    file.write(f'token = {token}\n')
                    doc_frequency = len(token_postings.get(token))
                    idf = round(self._calc_idf(doc_frequency), 2)
                    file.write(f"idf = {idf}\n")
                    for doc_id, freq in sorted(token_postings[token].items()):  # Sorted postings
                        file.write(f'({doc_id},{freq})\n')
                    file.write('\n')

        print(self._num_docs)
        print(f"Postings merged in folder: {output_folder}")

    # writes the document manager for this specific index into a text file
    def _write_doc_manager_to_file(self):
        self._doc_manager.write_doc_manager_to_file()

    # Resets the index and increments the file name
    def _reset_index(self):
        self._index = {}
        self._current_size = 0                    # Reset index size counter

    # retrieve a token's postings value
    def _get_token_postings(self, token):
        return self._index[token]

    # stem a token
    def _normalize_token(self, token):
        return PorterStemmer().stem(token.lower())

    def _convert_tf(self, count):
        return 1 + math.log10(count)

    def _calc_idf(self, doc_count):
        # add 1 because num docs starts at 0
        return math.log10( (self._num_docs + 1) / doc_count )
