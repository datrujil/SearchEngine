import os
from collections import defaultdict
from nltk.stem import PorterStemmer
from itertools import islice

# DT: Separate calculation function for separation of concerns
def calculate_tfidf_weight(tf, idf):
    """
    Calculate the tf-idf weight defined by "the product of its tf weight and its idf weight"
    """
    return tf * idf


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
            return {}, 0 # DT: Return postings and idf 0 if the file doesn't exist

        postings = {}
        idf = 0
        with open(file_path, 'r', encoding='utf-8') as file:
            current_token = None
            for line in file:
                if line.startswith('token ='):
                    current_token = line.strip().split(' = ')[1]
                elif current_token == token and line.startswith('idf ='):   # DT: Retrieve the idf value
                    idf = float(line.strip().split('=')[1])
                elif current_token == token and line.startswith('('):
                    doc_id, tf = map(float, line.strip("()\n").split(','))  # DT: Retrieve each document and their respective tf
                    postings[int(doc_id)] = tf
        return postings, idf

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

        scores = defaultdict(float) # DT: Doc ID --> Relevance Score

        for token in tokens:
            postings, idf = self._load_postings_for_token(token)    # DT: Retrieves idf now in addition to just postings
            if not postings:
                continue # Skip token with no postings

            for doc_id, tf in postings.items():
                scores[doc_id] += calculate_tfidf_weight(tf, idf)   # DT: Calculate the relevance score of each document given tf and idf

        ranked_docs = sorted(scores.items(), key = lambda x: x[1], reverse=True)    # DT: Sort the docs in decreasing order by their relevance scores
    
        doc_manager_path = "DocumentManager.txt"
        results = []
        # DT: Return the top 5 most relevant documents
        for doc_id, score in ranked_docs[:5]:
            url = self.get_url_from_docmanager(doc_manager_path, doc_id)
            if url:
                results.append((url, score))
        return results