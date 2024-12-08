import os
from Indexer import Indexer
from gui import create_gui

# creates a frequency and importance index
# if the index is already constructed, run the gui
if __name__ == '__main__':

    # get directories
    cwd = os.getcwd()
    frequency_directory = os.path.join(cwd, 'Frequency_Index')
    importance_index = os.path.join(cwd, 'Importance_Index')

    # create indexes if the indexes do not exist
    if not (os.path.exists(frequency_directory) and os.path.exists(importance_index)):
        # directory in which json files are located
        directory = 'DEV'
        # create index
        print(f"creating indexes from : {os.path.join(cwd, directory)}")
        index = Indexer()
        index.create_index(os.path.join(cwd, directory))

    # create gui for searching
    create_gui()
