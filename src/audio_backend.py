import time

import pydub
import simpleaudio


SONG1 = '/home/alok/Musik/Rock Blues/Led Zeppelin/Houses of the Holy/' \
        'Led Zeppelin Houses of the Holy 01 The Song Remains the Same.wav'
SONG2 = '/home/alok/Musik/Rock Blues/Eric Clapton/Complete Clapton/' \
        '1-07 After Midnight (Alternate Mix from _Crossroads_).mp3'


class AudioBackend:
    def __init__(self):
        self.current_player: Player or None = None

    def stop(self):
        if self.current_player is not None:
            self.current_player.stop()

    def play(self, filename):
        if self.is_playing():
            self.stop()
        song = read_file(filename)
        self.current_player = Player(song)
        self.current_player.play()

    def seek(self, duration):
        if self.current_player is not None:
            self.current_player.seek(duration)

    def resume(self):
        if self.current_player is not None:
            if not self.is_playing():
                self.current_player.resume()

    def is_playing(self):
        if self.current_player is not None:
            return self.current_player.is_playing()
        return False


class Player:
    def __init__(self, audio_segment: pydub.AudioSegment):
        self.audio_segment = audio_segment
        self.last_start_time = None
        self.played_duration = 0  # this is not updated during playing, use get_played_duration()
        self.playing = False
        self.play_object = None

    def stop(self):
        if self.playing:
            self.play_object.stop()
            self.play_object = None
            self.playing = False
            self.played_duration += (time.time() - self.last_start_time)
            self.last_start_time = None

    def is_playing(self):
        if self.playing:
            return self.play_object.is_playing()
        return False

    def resume(self):
        if not self.playing:
            self.playing = True
            wave_object = simpleaudio.WaveObject(
                self.audio_segment[int(self.played_duration*1000):].raw_data,
                self.audio_segment.channels,
                self.audio_segment.sample_width,
                self.audio_segment.frame_rate
            )
            self.play_object = wave_object.play()
            self.last_start_time = time.time()

    def play(self):
        self.playing = True
        wave_object = simpleaudio.WaveObject(
            self.audio_segment.raw_data,
            self.audio_segment.channels,
            self.audio_segment.sample_width,
            self.audio_segment.frame_rate
        )
        self.last_start_time = time.time()
        self.play_object = wave_object.play()
        self.played_duration = 0

    def seek(self, duration):
        if self.playing:
            self.stop()
            self.played_duration = min(max(self.played_duration + duration, 0), len(self.audio_segment))
            self.resume()
        else:
            self.played_duration = min(max(self.played_duration + duration, 0), len(self.audio_segment))

    def get_played_duration(self):
        if self.playing:
            return self.played_duration + (time.time() - self.last_start_time)
        else:
            return self.played_duration


def read_file(filename):
    return pydub.AudioSegment.from_file(filename)
