import os
import sys

from Indexer import Indexer

if __name__ == '__main__':

    index = Indexer()
    cwd = os.getcwd()
    directory = 'DEV'
    print(f"searching : {os.path.join(cwd, directory)}")

    index.create_index(os.path.join(cwd, directory))
