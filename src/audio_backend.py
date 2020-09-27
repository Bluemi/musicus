import pydub
import simpleaudio


SONG1 = '/home/alok/Musik/Rock Blues/Led Zeppelin/Houses of the Holy/' \
        'Led Zeppelin Houses of the Holy 01 The Song Remains the Same.wav'
SONG2 = '/home/alok/Musik/Rock Blues/Eric Clapton/Complete Clapton/' \
        '1-07 After Midnight (Alternate Mix from _Crossroads_).mp3'


class AudioBackend:
    def __init__(self):
        self.current_player: simpleaudio.PlayObject or None = None

    def stop(self):
        if self.current_player is not None:
            self.current_player.stop()
        self.current_player = None

    def play(self, filename):
        self.stop()
        song = read_file(filename)
        self.current_player = song.play()

    def is_playing(self):
        if self.current_player is not None:
            return self.current_player.is_playing()
        return False


def read_file(filename):
    song = pydub.AudioSegment.from_file_using_temporary_files(filename)
    return simpleaudio.WaveObject(song.raw_data, song.channels, song.sample_width, song.frame_rate)


def play_song(filename):
    song = read_file(filename)
    song.play()
