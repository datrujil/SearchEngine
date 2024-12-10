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
        self._current_size = 0                              # Track number of JSON files visited (partial index dump)
        self._threshold = 5000                              # JSON File limit (partial index dump)
        self._num_docs = 0                                  # number of documents indexed

    # create index
    def create_index(self, directory):
        # check if directory exists
        path = Path(directory)
        if not path.exists():
            print("Invalid Directory!")
            return

        # Tokenization regex pattern
        token_pattern = r'\b[a-zA-Z0-9]+\b'

        # Recursively go through each JSON file in the directory
        for file in path.rglob('*.json'):
            with open(file, 'r', encoding='utf-8') as curr_json_file:
                # For tracking progress
                print(curr_json_file.name)

                # Load JSON file and get a document ID
                data = json.load(curr_json_file)
                doc_id = self._doc_manager.add_doc(file.name, data)

                # keep track of largest doc_id assigned (used for idf calculation at the end)
                if self._num_docs < doc_id:
                    self._num_docs = doc_id

                # Parse HTML content
                # lxml parser handles broken html
                soup = BeautifulSoup(data['content'], 'lxml')

                # parse important tags first
                importance = ['title', 'h1', 'h2', 'h3', 'b', 'i', 'strong', 'em']
                for tag in importance:
                    important_words = soup.find_all(tag)
                    for word in important_words:
                        word = word.getText()
                        token_list = re.findall(token_pattern, word)
                        for token in token_list:
                            token = self._normalize_token(token)
                            # add importance posting to token
                            self._add_token_to_index(token, doc_id, posting='importance', tag=tag)

                # Process each section of the html
                # a section is html content between tags as to not load entire html content at once
                for section in soup.stripped_strings:
                    token_list = re.findall(token_pattern, section)

                    # Process each token in the section
                    for token in token_list:
                        token = self._normalize_token(token)
                        # add frequency posting to token
                        self._add_token_to_index(token, doc_id, posting='frequency')

            # check if threshold has been reached - if it has, dump partial index
            self._current_size += 1
            if self._current_size >= self._threshold:
                self._write_frequency_index_to_file()
                self._write_importance_index_to_file()
                self._reset_index()

        # Final write after indexing is complete
        self._write_frequency_index_to_file()
        self._write_importance_index_to_file()
        self._write_doc_manager_to_file()

        # merge indexes
        self._merge_indexes()

    # adds a token to the index
    def _add_token_to_index(self, token, doc_id, *, posting, tag=None):
        # if a token does not exist in the index, create an entry for it with an empty postings
        if token not in self._index:
            self._index[token] = Postings()

        # get the current token's postings
        token_postings = self._get_token_postings(token)

        # update the token's frequency postings
        if posting == 'frequency':
            token_postings.increment_frequency_posting(doc_id)

        # update the token's importance postings
        if posting == 'importance':
            token_postings.increment_importance_postings(doc_id, tag)

    # write the frequency index to file
    def _write_frequency_index_to_file(self, output_folder="Frequency_Index"):
        # locate the frequency index directory
        cwd = os.getcwd()
        path = Path(os.path.join(cwd, output_folder))

        # make the directory if it does not exist
        path.mkdir(parents=False, exist_ok=True)

        # write token and frequency postings to file from the current partial index
        for token, postings in self._index.items():
            # get the first letter of the token and open the corresponding file
            first_letter = token[0]
            file_name = os.path.join(output_folder, f'{first_letter}.txt')
            with open(file_name, 'a', encoding='utf-8') as output:
                # write token, doc_id and frequency to file
                output.write(f'token = {token}\n')
                for docID, frequency in postings.get_frequency_posting().items():
                    frequency = self._calc_tf(frequency)
                    output.write(f'({docID},{frequency})\n')

    # write the importance index to file
    def _write_importance_index_to_file(self, output_folder='Importance_Index'):
        # locate the importance index directory
        cwd = os.getcwd()
        path = Path(os.path.join(cwd, output_folder))

        # make the root directory if it does not exist
        if not path.is_dir():
            path.mkdir()

        # write token and importance postings to file from the current partial index
        for token, postings in self._index.items():
            # get doc_id and tag_info for token [e.g. doc_id = 17, tag_info = (h1, 4)]
            for doc_id, tag_info in postings.get_importance_posting().items():
                # extract tag and frequency from tag_info
                for tag, frequency in tag_info.items():
                    # create subdirectory for the tag if it does not exist
                    path = Path(os.path.join(cwd, output_folder, tag))
                    if not path.is_dir():
                        path.mkdir()

                    # get the first letter of the token and open the file under its corresponding tag
                    first_letter = token[0]
                    file_name = os.path.join(cwd, output_folder, tag, f'{first_letter}.txt')
                    with open(file_name, 'a', encoding='utf-8') as output:
                        # write token, doc_id, and frequency to file
                        output.write(f'token = {token}\n')
                        output.write(f'({doc_id},{frequency})\n')

    # merge indexes for frequency index and importance index
    def _merge_indexes(self, frequency="Frequency_Index", importance="Importance_Index"):
        # Ensure the directories exists
        if not os.path.exists(frequency) or not os.path.exists(importance):
            print(f"Output folder '{frequency} or {importance}' does not exist!")
            return

        # Process each file in each directory
        folders = [frequency, importance]
        for directory in folders:
            # enter directory
            path = Path(os.path.join(os.getcwd(), directory))

            # recursively go through each txt file in directory
            for file_name in path.rglob('*.txt'):
                file_path = os.path.join(directory, file_name)

                # Dictionary to store merged postings for tokens
                merged_postings = defaultdict(dict)

                # Read the file and aggregate postings
                with open(file_path, 'r', encoding='utf-8') as file:
                    current_token = None
                    for line in file:
                        # get token
                        if line.startswith('token ='):
                            current_token = line.strip().split(' = ')[1]
                        # get doc_id and frequency
                        elif current_token and line.startswith('('):  # Posting line
                            posting = line.strip("()\n").split(',')
                            doc_id = int(posting[0])
                            freq = float(posting[1])
                            # aggregate duplicate tokens
                            merged_postings[current_token][doc_id] = (
                                    round(merged_postings[current_token].get(doc_id, 0) + freq, 2)
                            )

                # Rewrite the file with merged postings
                with open(file_path, 'w', encoding='utf-8') as file:
                    # sort tokens based on doc_id
                    for token in sorted(merged_postings.keys()):
                        # write token, idf, doc_id, and frequency
                        file.write(f'token = {token}\n')
                        doc_frequency = len(merged_postings.get(token))
                        idf = round(self._calc_idf(doc_frequency), 2)
                        file.write(f"idf = {idf}\n")
                        for doc_id, freq in sorted(merged_postings[token].items()):  # Sorted postings
                            file.write(f'({doc_id},{freq})\n')
                        file.write('\n')

        print(f"Postings merged!")

    # writes the document manager for this specific index into a text file
    def _write_doc_manager_to_file(self):
        self._doc_manager.write_doc_manager_to_file()

    # resets the index for partial index dumping
    def _reset_index(self):
        self._index = {}
        self._current_size = 0

    # retrieve a token's postings value
    def _get_token_postings(self, token):
        return self._index[token]

    # normalize tokens by using porter stemmer
    def _normalize_token(self, token):
        return PorterStemmer().stem(token.lower())

    # calculates the term frequency for a given token's frequency
    def _calc_tf(self, count):
        return 1 + math.log10(count)

    # calculates the tokens idf based on number of documents it is in, and the total number of documents
    # in the corpus
    def _calc_idf(self, doc_count):
        # add 1 because num docs starts at 0
        return math.log10((self._num_docs + 1) / doc_count)
