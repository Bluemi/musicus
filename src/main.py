import curses
import songsdatabase
import config
from audio_backend import AudioBackend


# SONGS_DIRECTORY = '/home/alok/Musik/Rock Blues/Led Zeppelin/Houses of the Holy/'
SONGS_DIRECTORY = '/home/alok/Musik/Rock Blues/Led Zeppelin/'


class Musicus:
    def __init__(self):
        self.song_index = 0
        self.cursor_index = 0
        self.songs = songsdatabase.SongsDatabase.from_dir(SONGS_DIRECTORY)
        self.playing = False

    def render(self, scr):
        scr.clear()
        for index, song in enumerate(self.songs.song_list):
            if index >= curses.LINES:
                break
            if index == self.song_index:
                color_pair = 2
            elif index == self.cursor_index:
                color_pair = 3
            else:
                color_pair = 1
            scr.addstr(index, 0, song, curses.color_pair(color_pair))
        scr.refresh()

    def inc_cursor_index(self):
        if self.cursor_index < len(self.songs.song_list):
            self.cursor_index += 1
            return True
        return False

    def dec_cursor_index(self):
        if self.cursor_index > 0:
            self.cursor_index -= 1
            return True
        return False

    def inc_song_index(self):
        if self.song_index < len(self.songs.song_list):
            self.song_index += 1
            return True
        return False

    def dec_song_index(self):
        if self.song_index > 0:
            self.song_index -= 1
            return True
        return False

    def get_current_song(self):
        return self.songs.song_list[self.song_index]


def main(stdscr: curses.window, logs):
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_BLUE)
    stdscr.nodelay(True)

    config.init()

    musicus = Musicus()
    audio_backend = AudioBackend()
    ch = 1
    while True:
        if ch != 0:
            musicus.render(stdscr)

        try:
            ch = stdscr.getkey()
            if ch == 'q':
                break
            elif ch == 'j':
                musicus.inc_cursor_index()
            elif ch == 'k':
                musicus.dec_cursor_index()
            elif ch == 'c':
                if musicus.playing:
                    musicus.playing = False
                    audio_backend.stop()
                else:
                    musicus.playing = True
                    audio_backend.play(musicus.get_current_song())
            else:
                logs.append(ch)
        except curses.error:
            ch = 0

        # logs.append('playing: {}  is_playing: {}'.format(musicus.playing, audio_backend.is_playing()))
        if musicus.playing and not audio_backend.is_playing():
            if musicus.inc_song_index():
                audio_backend.play(musicus.get_current_song())


if __name__ == '__main__':
    main_logs = []
    curses.wrapper(main, main_logs)
    for log in main_logs:
        print(log)
