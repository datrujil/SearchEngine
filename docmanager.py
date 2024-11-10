import hashlib


class DocManager:
    def __init__(self):
        self._valid_manager = {}    # {hashed_raw_url : (doc_name, raw_url, doc_id)}
        self._invalid_manager = {}  # {hashed_raw_url : (doc_name, raw_url, doc_id)}
        self._doc_id = 0            # assigned document id to document passed into DocManager
        self._doc_name = 0          # position of doc_name in value tuple (doc_name, raw_url, doc_id)
        self._url = 1               # position of raw_url in value tuple (doc_name, raw_url, doc_id)
        self._id = 2                # position of doc_id in value tuple (doc_name, raw_url, doc_id)

    # adds a raw url to the document manager
    # doc_name is the actual file name, e.g. 0f247aaa92746c0a1f63b0.json
    # raw_url is the url stored in the json file, e.g. json['url']
    def add_doc(self, doc_name, raw_url):
        # hash the raw url
        hashed_url = self._hash_url(raw_url)
        # if hashed url does not exist, add to manager, and store all other relevant info
        if hashed_url not in self._valid_manager:
            self._valid_manager[hashed_url] = (doc_name, raw_url, self._doc_id)
            self._increment_doc_id()
        # url has been added before, add it to the invalid manager
        elif hashed_url not in self._invalid_manager:
            self._invalid_manager[hashed_url] = (doc_name, raw_url, self._doc_id)

    # get the corresponding document id given a raw url
    def get_doc_id(self, raw_url):
        # hash the raw url
        hashed_url = self._hash_url(raw_url)
        # check valid manager for hashed raw url, return the document id
        if hashed_url in self._valid_manager:
            return self._valid_manager[hashed_url][self._id]
        # hashed raw url does not exist in the valid manager
        return -1

    # print the contents of the invalid and valid manager
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

    # defragments a url, e.g. www.something.com/path/example#546 --> www.something.com/path/example
    # removes the last /, e.g. www.something.com/ --> www.something.com
    def _normalize_url(self, url):
        fragment = url.find('#')
        if fragment != -1:
            url = url[0:fragment]
        if url.endswith('/'):
            url = url[:-1]
        return url
