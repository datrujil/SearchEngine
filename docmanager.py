import hashlib


class DocManager:
    def __init__(self):
        self._valid_manager = {}
        self._invalid_manager = {}
        self._doc_id = 0    # assigned document id
        self._url = 0       # position of url in tuple (url, doc_id)
        self._id = 1        # position of doc_id in tuple (url, doc_id)

    # adds url to doc manager as a [hashed_url]=(url,doc_id) key value pair
    def add_url(self, raw_url):
        # hash url
        hashed_url = self._hash_url(raw_url)
        # if url does not exist, add to manager
        if hashed_url not in self._valid_manager:
            self._valid_manager[hashed_url] = (raw_url, self._doc_id)
            self._increment_doc_id()
        # repeat url, send to invalid manager
        elif hashed_url not in self._invalid_manager:
            self._invalid_manager[hashed_url] = (raw_url, self._doc_id)

    # get the corresponding document id given a url
    def get_url_doc_id(self, raw_url):
        # hashed url
        hashed_url = self._hash_url(raw_url)
        # check manager for url, return document id if valid
        if hashed_url in self._valid_manager:
            return self._valid_manager[hashed_url][self._id]
        # url does not exist in manager
        return -1

    # retrieve url from a document id
    def get_url(self, doc_id):
        for url, id in self._valid_manager.values():
            if doc_id == id:
                return url
        return ''

    # print manager
    def print_manager(self, *, valid_file_name=None, invalid_file_name=None):
        if valid_file_name is not None:
            with open(valid_file_name, 'w', encoding='utf-8') as f:
                for key, value in self._valid_manager.items():
                    f.write(f"hash = {key} info = {value}\n")
            if invalid_file_name is not None:
                with open(invalid_file_name, 'w', encoding='utf-8') as f:
                    for key, value in self._invalid_manager.items():
                        f.write(f"hash = {key} info = {value}\n")

    # hash a url using sha256, return the hexadecimal representation
    def _hash_url(self, url):
        normalized_url = self._normalize_url(url)
        hashed_url = hashlib.sha256()
        hashed_url.update(normalized_url.encode())
        hashed_url = hashed_url.hexdigest()
        return hashed_url

    # increments the document id
    def _increment_doc_id(self):
        self._doc_id += 1

    def _normalize_url(self, url):
        fragment = url.find('#')
        if fragment != -1:
            url = url[0:fragment]
        if url.endswith('/'):
            url = url[:-1]
        return url
