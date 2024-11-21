import os
from collections import defaultdict
from functools import reduce
from nltk.stem import PorterStemmer

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

    def search_and(self, query):
        """
        Search for documents that contain all tokens in the query and rank them by combined frequency.
        """
        # Normalize and stem the tokens
        tokens = query.lower().split()
        tokens = [self.stemmer.stem(token) for token in tokens]

        # Load postings for each token and compute document frequency scores
        doc_frequency = defaultdict(int)
        for token in tokens:
            postings = self._load_postings_for_token(token)
            for doc_id, freq in postings.items():
                doc_frequency[doc_id] += freq

        # Sort documents by frequency in descending order
        ranked_docs = sorted(doc_frequency.items(), key=lambda x: x[1], reverse=True)
        return [doc_id for doc_id, _ in ranked_docs[:5]]