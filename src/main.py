import curses
import songsdatabase
from audio_backend import AudioBackend


# SONGS_DIRECTORY = '/home/alok/Musik/Rock Blues/Led Zeppelin/Houses of the Holy/'
SONGS_DIRECTORY = '/home/alok/Musik/Rock Blues/Led Zeppelin/'


class Musicus:
    def __init__(self):
        self.song_index = 0
        self.songs = songsdatabase.SongsDatabase.from_dir(SONGS_DIRECTORY)

    def render(self, scr):
        for index, song in enumerate(self.songs.song_list):
            if index >= curses.LINES:
                break
            if index == self.song_index:
                scr.addstr(index, 0, song, curses.color_pair(2))
            else:
                scr.addstr(index, 0, song, curses.color_pair(1))


def main(stdscr: curses.window):
    musicus = Musicus()
    audio_backend = AudioBackend()
    while True:
        stdscr.clear()

        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)

        musicus.render(stdscr)

        stdscr.refresh()
        ch = stdscr.getkey()
        if ch == 'q':
            break
        elif ch == 'j' and musicus.song_index < len(musicus.songs.song_list)-1:
            musicus.song_index += 1
        elif ch == 'k' and musicus.song_index > 0:
            musicus.song_index -= 1
        elif ch == 'c':
            audio_backend.play(musicus.songs.song_list[musicus.song_index])


if __name__ == '__main__':
    curses.wrapper(main)
