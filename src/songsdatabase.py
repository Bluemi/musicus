import os


SOUND_FILE_ENDINGS = ['wav', 'mp3']


class SongsDatabase:
    def __init__(self, song_list):
        self.song_list = song_list

    @staticmethod
    def from_dir(directory):
        """
        Create SongsDatabase from directory

        :param directory:
        :return: A SongsDatabase containing all songs of the given directory
        :rtype: SongsDatabase
        """
        song_list = []
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                for ending in SOUND_FILE_ENDINGS:
                    if filename.endswith(ending):
                        song_list.append(os.path.join(dirpath, filename))

        return SongsDatabase(song_list)

    def __str__(self):
        return str(self.song_list)