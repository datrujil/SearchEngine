# contains a tokens contextual information (frequency postings, and importance postings)
class Postings:
    def __init__(self):
        self._doc_id = None
        self._frequency_postings = {}       # {doc_id : frequency}
        self._importance_postings = {}      # {doc_id : (tag, frequency)} ; tags can be h1,h2,h3,i,em,b,title,strong

    # FREQUENCY INDEX METHODS
    # -----------------------
    #
    # increments frequency for a given token and doc_id
    def increment_frequency_posting(self, doc_id):
        if doc_id in self._frequency_postings:
            self._frequency_postings[doc_id] += 1
        else:
            self._frequency_postings[doc_id] = 1

    # return frequency posting
    def get_frequency_posting(self):
        return self._frequency_postings

    # IMPORTANCE INDEX METHODS
    # ------------------------
    #
    # increments frequency for a given token, doc_id, and tag
    def increment_importance_postings(self, doc_id, new_tag):
        # increment a token's tag frequency if it exists within a document
        found = False

        # check if token has an importance posting
        if doc_id in self._importance_postings:
            # check if the tag exists in the document
            for existing_tag in self._importance_postings[doc_id]:
                if new_tag == existing_tag:
                    found = True
                    # increment tag frequency if found
                    self._importance_postings[doc_id][existing_tag] += 1
            # tag doesn't exist yet, create one
            if not found:
                self._importance_postings[doc_id][new_tag] = 1

        # create new importance posting and tag for token
        else:
            self._importance_postings[doc_id] = {}
            self._importance_postings[doc_id][new_tag] = 1

    # return importance posting
    def get_importance_posting(self):
        return self._importance_postings
