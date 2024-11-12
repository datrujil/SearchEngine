class Postings:
    def __init__(self):
        self._doc_id = None
        self._frequency_postings = {}                             # {doc_id : frequency}
        # self._other_posting = {}                                # add other postings as desired
        # ...                                                     # ...
        # self._other2_posting = {}                               # ...

#################################################################### FREQUENCY POSTING METHODS ONLY
    def increment_frequency_posting(self, doc_id):
        if doc_id in self._frequency_postings:
            self._frequency_postings[doc_id] += 1
        else:
            self._frequency_postings[doc_id] = 1

    def write_frequency_posting_to_file(self, file):
        for posting in self._frequency_postings.items():
            file.write(f"{posting}\n")
        file.write("-------------------------------------------------------\n\n")
#################################################################### FREQUENCY POSTING METHODS ONLY
