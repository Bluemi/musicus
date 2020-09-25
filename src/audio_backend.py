import pydub
import simpleaudio


SONG1 = '/home/alok/Musik/Rock Blues/Led Zeppelin/Houses of the Holy/' \
        'Led Zeppelin Houses of the Holy 01 The Song Remains the Same.wav'
SONG2 = '/home/alok/Musik/Rock Blues/Eric Clapton/Complete Clapton/' \
        '1-07 After Midnight (Alternate Mix from _Crossroads_).mp3'


class AudioBackend:
    def __init__(self):
        self.playing = []

    def stop(self):
        for player in self.playing:
            player.stop()
        self.playing.clear()

    def play(self, filename):
        self.stop()
        song = read_file(filename)
        player = song.play()
        self.playing.append(player)


def read_file(filename):
    song = pydub.AudioSegment.from_file_using_temporary_files(filename)
    return simpleaudio.WaveObject(song.raw_data, song.channels, song.sample_width, song.frame_rate)


def play_song(filename):
    song = read_file(filename)
    song.play()
