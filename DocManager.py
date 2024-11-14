# maintains document id and url associations
class DocManager:
    def __init__(self):
        self._assign_doc_id = 0                         # assign a document an id
        self._doc_id_manager = {}                       # {doc_id : (file_name, url)}
        self._urls = set()                              # set of all url's
        self._duplicate_urls = set()                    # set of all duplicate url's

    # adds a document/url to the document manager
    def add_doc(self, json_file_name, json_handle):
        url = self._normalize_url(json_handle['url'])
        if self._add_url_to_set(url) is True:
            self._doc_id_manager[self._assign_doc_id] = (json_file_name, url)
            self._increment_doc_id()
        return self.get_doc_id(json_handle['url'])

    # given a document id, return its associated contents (file_name, url)
    def get_doc_info(self, doc_id):
        return self._doc_id_manager[doc_id]

    # given a raw_url, return its document id if found
    def get_doc_id(self, raw_url=None):
        if raw_url is not None:
            url = self._normalize_url(raw_url)
            for doc_id, info in self._doc_id_manager.items():
                if url == info[1]:
                    return doc_id

    # write the document manager to a text file
    def write_doc_manager_to_file(self):
        if self._doc_id_manager:
            with open('DocumentManager.txt', 'w', encoding='utf-8') as output:
                for doc_id, info in self._doc_id_manager.items():
                    output.write(f"Doc_ID = {doc_id}\tInfo = {info}\n")
            with open('Duplicates.txt', 'w', encoding='utf-8') as output:
                for url in self._duplicate_urls:
                    output.write(f"{url}\n")

    # add a url to the set if it has not been seen before - else add it to the duplicates set
    def _add_url_to_set(self, url):
        if url not in self._urls:
            self._urls.add(url)
            return True
        else:
            self._duplicate_urls.add(url)
        return False

    # increments the id for the next document
    def _increment_doc_id(self):
        self._assign_doc_id += 1

    # defragments a url, e.g. www.something.com/path/example#546 --> www.something.com/path/example
    # removes the last /, e.g. www.something.com/ --> www.something.com
    def _normalize_url(self, url):
        fragment = url.find('#')
        if fragment != -1:
            url = url[0:fragment]
        if url.endswith('/'):
            url = url[:-1]
        return url
