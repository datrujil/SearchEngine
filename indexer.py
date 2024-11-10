from postings import Postings


class Indexer:
    def __init__(self):
        self._index = {}    # (token, postings)

    # FREQUENCY POSTING
    # access frequency posting and increment it
    def increment_frequency_posting(self, token, doc_id):
        postings = self._get_token_postings(token)
        if postings:
            postings.increment_frequency_posting(doc_id)

    # add token to index
    def add_token_to_index(self, token):
        if token not in self._index:
            self._index[token] = Postings()

    # get token's postings
    def _get_token_postings(self, token):
        return self._index[token]

    def print_index_frequency_posting(self, *, file_name=None):
        if file_name is not None:
            with open(file_name, 'w', encoding='utf-8') as f:
                for token, postings in self._index.items():
                    f.write(f"token = {token}\n")
                    postings.print_frequency_posting(file=f)
