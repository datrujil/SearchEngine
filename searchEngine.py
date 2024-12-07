import os
from collections import defaultdict
from nltk.stem import PorterStemmer
from itertools import islice
from pathlib import Path
import math

# DT: Stop words
STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as",
    "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot",
    "could","couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few",
    "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll",
    "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
    "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most",
    "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
    "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's",
    "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until",
    "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when",
    "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
}

# DT: Separate calculation function for separation of concerns
def calculate_tfidf_weight(tf, idf, *, weight=1.0, log=False):
    """
    Calculate the tf-idf weight defined by "the product of its tf weight and its idf weight"
    """

    if log and weight != 0:
        return math.log10(tf*weight) * idf

    return tf * idf * weight

class SearchEngine:
    def __init__(self, index_folder):
        self.index_folder = index_folder
        self.stemmer = PorterStemmer()

        self._freq_file_handles = {}

        self._bold_handles = {}
        self._emphasis_handles = {}
        self._h1_handles = {}
        self._h2_handles = {}
        self._h3_handles = {}
        self._italics_handles = {}
        self._strong_handles = {}
        self._title_handles = {}
        self._important_file_handles = [self._bold_handles, self._emphasis_handles, self._h1_handles, self._h2_handles]
        self._important_file_handles.extend([self._h3_handles, self._italics_handles, self._strong_handles, self._title_handles])
        self._important_handles_index = {'b': 0, 'em': 1, 'h1': 2, 'h2': 3, 'h3': 4, 'i': 5, 'strong': 6, 'title': 7}
        self._importance_weights = [('b',25), ('em',0), ('h1',100), ('h2',50), ('h3',25), ('i',0), ('strong',25), ('title',100)]    
        self._open_all_indexes()

    def _open_all_indexes(self):
        cwd = os.getcwd()

        important_directory = 'Importance_Index'
        frequency_directory = 'Frequency_Index'

        path = Path(os.path.join(cwd, frequency_directory))
        for file in path.rglob('*.txt'):
            self._freq_file_handles[file.name[0]] = open(file, 'r', encoding='utf-8')

        for directory, index in self._important_handles_index.items():
            path = Path(os.path.join(cwd, important_directory, directory))
            for file in path.rglob('*.txt'):
                self._important_file_handles[index][file.name[0]] = open(file, 'r', encoding='utf-8')

    def _close_all_indexes(self):
        for handle in self._freq_file_handles.values():
            handle.close()
        for handle in self._important_file_handles:
            for file in handle.values():
                file.close()

    def _load_postings_for_token(self, token, *, postings_type, index=None):
        if postings_type.lower() == 'frequency':
            return self._helper_load_postings_for_token(token, self._freq_file_handles[token[0]])
        if postings_type.lower() == 'importance':
            return self._helper_load_postings_for_token(token, self._important_file_handles[index][token[0]])

    def _helper_load_postings_for_token(self, token, file):
        """
        Load postings for a specific token from its corresponding file.
        """
        if not file:
            return {}, 0  # DT: Return postings and idf 0 if the file doesn't exist

        file.seek(0)    # DT: Reset the file pointer

        postings = {}
        idf = None
        for line in file:
            # find query token
            if line.strip() == f'token = {token}':
                # get line after the token line
                line = file.readline()
                while file and 'token' not in line and line != '\n':
                    # get idf
                    if idf is None:
                        idf = float(line.strip().split(' = ')[1])  # DT: Retrieve the idf value
                    # get postings
                    else:
                        data = line.strip("()\n").split(',')
                        doc_id = int(data[0])
                        tf = float(data[1])  # DT: Retrieve each document and their respective tf
                        postings[doc_id] = tf
                    # get next line
                    line = file.readline()
                break

        return postings, idf

    def get_url_from_docmanager(self, file_path, doc_id):
        """
        Retrieve the URL for a given document ID by directly accessing the corresponding line in docmanager.txt.
        """

        # Use islice to directly seek the desired line to efficinetly search DocumentManager.txt
        file_path.seek(0)
        line = next(islice(file_path, doc_id, doc_id + 1), None)
        if line:
            # Extract the URL from the line
            parts = line.split("\t")
            url = parts[1].split(" = ")[1].strip("()").split(", ")[1].replace('\'', '').replace(')', '')
            return url
        return None

    def search_query(self, query):
        """
        Search for documents that contain all tokens in the query and return the first 5 as URLs.
        """
        # Normalize and stem the tokens
        tokens = query.lower().split()

        # DT: Remove stopwords if query is greater than 3 tokens
        if len(tokens) > 3:
            tokens = [token for token in tokens if token not in STOP_WORDS]

        tokens = [self.stemmer.stem(token) for token in tokens]

        scores = defaultdict(float)  # DT: Doc ID --> Relevance Score

        # DT: Refactored token processing code
        for token in tokens:
            freq_postings, freq_idf = self._load_postings_for_token(token, postings_type='frequency')

            # DT: Process importance postings
            importance_postings = []
            importance_idfs = []
            for tag, index in self._important_handles_index.items():
                postings, idf = self._load_postings_for_token(token, postings_type='importance', index=index)
                importance_postings.append(postings)
                importance_idfs.append(freq_idf)
                
            # DT: Update scores from frequency postings
            for doc_id, tf in freq_postings.items():
                scores[doc_id] += calculate_tfidf_weight(tf, freq_idf)

            # DT: Update scores from importance postings
            for i, postings in enumerate(importance_postings):
                    for doc_id, tf in postings.items():
                        weight = self._importance_weights[i][1]
                        scores[doc_id] += calculate_tfidf_weight(tf, importance_idfs[i], weight=weight, log=True)

        ranked_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)    # DT: Sort the docs in decreasing order by their relevance scores
        file_object = open("DocumentManager.txt", 'r', encoding='utf-8')
        results = []
        # DT: Return the top 15 most relevant documents
        for doc_id, score in ranked_docs[:15]:
            url = self.get_url_from_docmanager(file_object, doc_id)
            if url:
                results.append((url, score))
        return results
