import os
from collections import defaultdict
from nltk.stem import PorterStemmer
from itertools import islice
from pathlib import Path
import math

# list of stop words
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


# calculates the tf-idf weight for a token
# a weight is applied for importance tags (h1,h2,h3,i,em,b,title,strong)
def calculate_tfidf_weight(tf, idf, *, weight=1.0, log=False):
    # use this if the tf being passed in is the raw tf (log is not applied)
    if log and weight != 0:
        return math.log10(tf*weight) * idf
    # assumed the tf has log applied to it already
    return tf * idf * weight


# conducts searching of queries and returns top results
class SearchEngine:
    def __init__(self):
        self.stemmer = PorterStemmer()  # for stemming queries

        self._doc_manager_handle = None # file handle for the document manager

        self._freq_file_handles = {}    # file handles for all frequency indexes

        self._bold_handles = {}         # file handles for all bold indexes
        self._emphasis_handles = {}     # file handles for all emphasis indexes
        self._h1_handles = {}           # file handles for all h1 indexes
        self._h2_handles = {}           # file handles for all h2 indexes
        self._h3_handles = {}           # file handles for all h3 indexes
        self._italics_handles = {}      # file handles for all italics indexes
        self._strong_handles = {}       # file handles for all strong indexes
        self._title_handles = {}        # file handles for all titles indexes

        # aggregate the above file handles for important tags
        # frequency file handle not included
        self._important_file_handles = [self._bold_handles, self._emphasis_handles, self._h1_handles, self._h2_handles]
        self._important_file_handles.extend([self._h3_handles, self._italics_handles, self._strong_handles, self._title_handles])

        # parallel arrays for indexing the above file handles and applying weights
        self._important_handles_index = {'b': 0, 'em': 1, 'h1': 2, 'h2': 3, 'h3': 4, 'i': 5, 'strong': 6, 'title': 7}
        self._importance_weights = [('b',25), ('em',0), ('h1',100), ('h2',50), ('h3',25), ('i',0), ('strong',25), ('title',100)]

        # open all indexes available for searching
        self._open_all_indexes()

    def _open_all_indexes(self):
        # get cwd
        cwd = os.getcwd()

        # get frequency directory containing indexes and recursively open each one
        path = Path(os.path.join(cwd, 'Frequency_Index'))
        if not path.exists():
            print("Frequency Index directory does not exist!")
        else:
            for file in path.rglob('*.txt'):
                self._freq_file_handles[file.name[0]] = open(file, 'r', encoding='utf-8')

        # get importance directory containing indexes and recursively open each one
        for directory, index in self._important_handles_index.items():
            path = Path(os.path.join(cwd, 'Importance_Index', directory))
            if not path.exists():
                print("Importance Index directory does not exist!")
            else:
                for file in path.rglob('*.txt'):
                    self._important_file_handles[index][file.name[0]] = open(file, 'r', encoding='utf-8')

        # open the document manager
        path = Path(os.path.join(cwd, 'DocumentManager.txt'))
        if not path.exists():
            print("Document Manager directory does not exist!")
        else:
            self._doc_manager_handle = open("DocumentManager.txt", 'r', encoding='utf-8')

    # close all opened file handles
    def _close_all_indexes(self):
        for handle in self._freq_file_handles.values():
            handle.close()
        for handle in self._important_file_handles:
            for file in handle.values():
                file.close()
        self._doc_manager_handle.close()

    # retrieve postings for a token from the frequency and important indexes
    def _load_postings_for_token(self, token, *, postings_type, tag_index=None):
        if postings_type.lower() == 'frequency':
            return self._helper_load_postings_for_token(token, self._freq_file_handles[token[0]])
        if postings_type.lower() == 'importance':
            return self._helper_load_postings_for_token(token, self._important_file_handles[tag_index][token[0]])

    # retrieve postings for a token from the frequency and important indexes
    def _helper_load_postings_for_token(self, token, file_handle):
        # if file doesnt exist, return nothing
        if not file_handle:
            return {}, 0

        # reset file marker before searching
        file_handle.seek(0)

        # retrieved postings and idf
        postings = {}
        idf = None

        # go through each line in the file
        for line in file_handle:
            # find token
            if line.strip() == f'token = {token}':
                # move file marker to next line
                line = file_handle.readline()
                # read postings and idf, stop if end of file, or a new token is seen
                while file_handle and 'token' not in line and line != '\n':
                    # get idf
                    if idf is None:
                        idf = float(line.strip().split(' = ')[1])
                    # get postings (doc_id, tf)
                    else:
                        data = line.strip("()\n").split(',')
                        doc_id = int(data[0])
                        tf = float(data[1])
                        postings[doc_id] = tf

                    # move file marker to next line
                    line = file_handle.readline()

                # all postings read
                break

        return postings, idf

    # search document manager for top n results
    # top 5 --> index_start = 0, index_end = 5
    # next 5 --> index_start = 5, index_end = 10
    def get_range_urls_from_docmanager(self, ranked_docs, index_start, index_end):
        urls = []
        scores = []
        for i in range(index_start, index_end):
            url = self.get_url_from_docmanager(ranked_docs[i][0])
            urls.append(url)
            scores.append(ranked_docs[i][1])
        return urls, scores

    # search document manager for a single result
    def get_url_from_docmanager(self, doc_id):
        # use islice to directly seek the desired line to efficiently search DocumentManager.txt
        # a doc_id is always 1 less than the file line. e.g. line 432 contains doc_id 431
        self._doc_manager_handle.seek(0)
        line = next(islice(self._doc_manager_handle, doc_id, doc_id + 1), None)
        if line:
            # extract the url from the line
            parts = line.split("\t")
            url = parts[1].split(" = ")[1].strip("()").split(", ")[1].replace('\'', '').replace(')', '')
            return url
        return None

    # given a query, return the top results based on tf-idf and importance
    def search_query(self, query):
        # get query
        query_tokens = query.lower().split()

        # remove stopwords if query is greater than 3 tokens
        if len(query_tokens) > 3:
            query_tokens = [token for token in query_tokens if token not in STOP_WORDS]

        # normalize query tokens
        query_tokens = [self.stemmer.stem(token) for token in query_tokens]

        # create a score for each relevant document {doc_id:relevance_score}
        scores = defaultdict(float)

        # account for multiple occurrences of the same token
        seen_tokens = set()
        # score each token in the query
        for token in query_tokens:
            # only process tokens once (avoid duplicates from the query)
            if token not in seen_tokens:
                # load the token's frequency postings and idf
                freq_postings, freq_idf = self._load_postings_for_token(token, postings_type='frequency')

                # store the frequency score (tf-idf) for each relevant document
                for doc_id, tf in freq_postings.items():
                    scores[doc_id] += calculate_tfidf_weight(tf, freq_idf)

                # keep track of each tag's postings and idfs [h1,h2,h3,i,em,b,title,strong]
                importance_postings = []
                importance_idfs = []
                # load the token's importance postings and idf for each tag
                for tag, index in self._important_handles_index.items():
                    postings, idf = self._load_postings_for_token(token, postings_type='importance', tag_index=index)
                    importance_postings.append(postings)
                    importance_idfs.append(freq_idf)

                # store the importance score (weighted tf-idf) for each relevant document
                for i, postings in enumerate(importance_postings):
                    for doc_id, tf in postings.items():
                        weight = self._importance_weights[i][1]
                        scores[doc_id] += calculate_tfidf_weight(tf, importance_idfs[i], weight=weight, log=True)
            seen_tokens.add(token)
        # sort the docs by their relevance scores {doc_id:relevance_score}
        ranked_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        return ranked_docs
