import os
from Indexer import Indexer

# creates an index for a specified directory containing html content in json files
if __name__ == '__main__':

    # create an indexer
    index = Indexer()

    # get current working directory
    cwd = os.getcwd()

    # specify folder in which to locate all json files
    directory = 'DEV'
    print(f"searching : {os.path.join(cwd, directory)}")

    # create the index based on the directory given
    index.create_index(os.path.join(cwd, directory))
