import os
from collections import defaultdict
from functools import reduce
from nltk.stem import PorterStemmer
from itertools import islice

class SearchEngine:
    def __init__(self, index_folder):
        self.index_folder = index_folder
        self.stemmer = PorterStemmer()

    def _get_file_for_token(self, token):
        """
        Determine the file where the token is stored based on its first letter.
        """
        first_letter = token[0]
        return os.path.join(self.index_folder, f"{first_letter}.txt")

    def _load_postings_for_token(self, token):
        """
        Load postings for a specific token from its corresponding file.
        """
        file_path = self._get_file_for_token(token)
        if not os.path.exists(file_path):
            return {}

        postings = {}
        with open(file_path, 'r', encoding='utf-8') as file:
            current_token = None
            for line in file:
                if line.startswith('token ='):
                    current_token = line.strip().split(' = ')[1]
                elif current_token == token and line.startswith('('):
                    doc_id, freq = map(int, line.strip("()\n").split(','))
                    postings[doc_id] = freq
        return postings

    def get_url_from_docmanager(self, file_path, doc_id):
        """
        Retrieve the URL for a given document ID by directly accessing the corresponding line in docmanager.txt.
        """

        with open(file_path, 'r', encoding='utf-8') as file:

            # Use islice to directly seek the desired line to efficinetly search DocumentManager.txt
            line = next(islice(file, doc_id, doc_id + 1), None)
            if line:

                # Extract the URL from the line
                parts = line.split("\t")
                url = parts[1].split(" = ")[1].strip("()").split(", ")[1].replace('\'', '').replace(')', '')
                return url
            return None

    def search_and(self, query):
        """
        Search for documents that contain all tokens in the query and return the first 5 as URLs.
        """
        # Normalize and stem the tokens
        tokens = query.lower().split()
        tokens = [self.stemmer.stem(token) for token in tokens]

        doc_sets = []

        for token in tokens:
            postings = self._load_postings_for_token(token)
            if postings:
                doc_sets.append(set(postings.keys()))
            else:
                return []

        # Perform AND operation by intersecting all document sets
        if doc_sets:
            common_docs = set.intersection(*doc_sets)
        else:
            return []
    
        doc_manager_path = "DocumentManager.txt"
        urls = []
        for doc_id in list(common_docs)[:5]:
            url = self.get_url_from_docmanager(doc_manager_path, doc_id)
            if url:
                urls.append(url)
        return urls