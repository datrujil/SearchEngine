class Postings:
    def __init__(self):
        self._doc_id = None
        self._frequency_posting = {}   # (doc_id, frequency)

    def increment_frequency_posting(self, doc_id):
        if doc_id in self._frequency_posting:
            self._frequency_posting[doc_id] += 1
        else:
            self._frequency_posting[doc_id] = 1


    def print_frequency_posting(self, *, file=None):
        if file is not None:
            for doc_id, frequency in self._frequency_posting.items():
                file.write(f"doc id = {doc_id}, frequency = {frequency}\n")
            file.write("-------------------------------------------------------\n\n")
