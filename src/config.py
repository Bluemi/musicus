import os
import songsdatabase


CONFIG_DIR_PATH = os.path.expanduser('~/.config/musicus')
LIB_FILE_PATH = os.path.join(CONFIG_DIR_PATH, 'lib.pl')
CONFIG_FILE_PATH = os.path.join(CONFIG_DIR_PATH, 'config.yaml')


class Config:
    def __init__(self, playlists_dir):
        self.playlists_dir = playlists_dir

    @staticmethod
    def default():
        if os.path.isfile(CONFIG_FILE_PATH):
            pass
        else:
            os.makedirs(CONFIG_DIR_PATH, exist_ok=True)


def init():
    if not os.path.isfile(CONFIG_FILE_PATH):
        os.makedirs(CONFIG_DIR_PATH, exist_ok=True)

    if not os.path.isfile(LIB_FILE_PATH):
        with open(LIB_FILE_PATH, 'a'):
            pass


def read_lib():
    return songsdatabase.SongsDatabase.from_playlist(LIB_FILE_PATH)
