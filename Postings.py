# contains contextual information about a token
class Postings:
    def __init__(self):
        self._doc_id = None
        self._frequency_postings = {}                             # {doc_id : frequency}
        self._importance_postings = {}                            # {doc_id : (tag, frequency)}
        # ...                                                     # add other postings as desired
        # self._other2_posting = {}                               # ...

#################################################################### FREQUENCY POSTING METHODS ONLY
    # increment the frequency count (of a token) for a specific document
    def increment_frequency_posting(self, doc_id):
        if doc_id in self._frequency_postings:
            self._frequency_postings[doc_id] += 1
        else:
            self._frequency_postings[doc_id] = 1

    # Converts the posting data to a dictionary
    def frequency_to_dict(self):
        return self._frequency_postings
            # Add other posting dictionaries here if needed in the future
#################################################################### FREQUENCY POSTING METHODS ONLY

#################################################################### IMPORTANCE POSTING METHODS ONLY
    # increment the frequency count (of a token) for a specific document
    def increment_importance_postings(self, doc_id, tag):
        found = False
        if doc_id in self._importance_postings:
            for key in self._importance_postings[doc_id]:
                if tag == key:
                    found = True
                    self._importance_postings[doc_id][key] += 1
            if not found:
                self._importance_postings[doc_id][tag] = 1
        else:
            self._importance_postings[doc_id] = {}
            self._importance_postings[doc_id][tag] = 1

    # Converts the posting data to a dictionary
    def importance_to_dict(self):
        return self._importance_postings
            # Add other posting dictionaries here if needed in the future

    # check if an importance posting exists:
    def has_importance_posting(self):
        return bool(self._importance_postings)
#################################################################### IMPORTANCE POSTING METHODS ONLY