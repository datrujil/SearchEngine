import json


# contains contextual information about a token
class Postings:
    def __init__(self):
        self._doc_id = None
        self._frequency_postings = {}                             # {doc_id : frequency}
        # self._other_posting = {}                                # add other postings as desired
        # ...                                                     # ...
        # self._other2_posting = {}                               # ...

#################################################################### FREQUENCY POSTING METHODS ONLY
    # increment the frequency count (of a token) for a specific document
    def increment_frequency_posting(self, doc_id):
        if doc_id in self._frequency_postings:
            self._frequency_postings[doc_id] += 1
        else:
            self._frequency_postings[doc_id] = 1

    # Converts the posting data to a dictionary format for JSON export
    def to_dict(self):
        return self._frequency_postings
            # Add other posting dictionaries here if needed in the future
#################################################################### FREQUENCY POSTING METHODS ONLY
