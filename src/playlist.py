import songsdatabase


class PlaylistManager:
    def __init__(self):
        self.playlists = []

    def new(self, name):
        self.playlists.append(Playlist(name))


class Playlist:
    def __init__(self, name):
        self.name = name
        self.songs = songsdatabase.SongsDatabase.empty()
