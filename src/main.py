import curses
from enum import Enum

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

    def render_line(self, scr, line_index):
        song = self.songs.song_list[line_index]
        if line_index == self.song_index:
            color_pair = 2
        elif line_index == self.cursor_index:
            color_pair = 3
        else:
            color_pair = 1
        scr.addstr(line_index, 0, song, curses.color_pair(color_pair))

    def render(self, scr, render_update):
        """
        :type render_update: RenderUpdate
        """
        if render_update.update_type == RenderUpdate.UpdateType.INIT:
            scr.clear()
            for index, song in enumerate(self.songs.song_list):
                if index >= curses.LINES:
                    break
                self.render_line(scr, index)
            scr.refresh()
        else:
            if render_update.update_type == RenderUpdate.UpdateType.CURSOR_MOVE:
                self.render_line(scr, render_update.old_cursor_pos)
                self.render_line(scr, render_update.new_cursor_pos)

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


class RenderUpdate:
    class UpdateType(Enum):
        INIT = 0
        CURSOR_MOVE = 1

    @staticmethod
    def init():
        return RenderUpdate(
            RenderUpdate.UpdateType.INIT
        )

    @staticmethod
    def cursor_move(old_cursor_pos, new_cursor_pos):
        return RenderUpdate(
            RenderUpdate.UpdateType.CURSOR_MOVE,
            old_cursor_pos=old_cursor_pos,
            new_cursor_pos=new_cursor_pos
        )

    def __init__(self, update_type, old_cursor_pos=None, new_cursor_pos=None):
        self.update_type = update_type
        self.old_cursor_pos = old_cursor_pos
        self.new_cursor_pos = new_cursor_pos


def main(stdscr: curses.window, logs):
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_BLUE)
    stdscr.nodelay(True)

    config.init()

    musicus = Musicus()
    audio_backend = AudioBackend()
    render_update: RenderUpdate or None = RenderUpdate.init()
    while True:
        if render_update is not None:
            musicus.render(stdscr, render_update)
            render_update = None

        try:
            ch = stdscr.getkey()
            if ch == 'q':
                break
            elif ch == 'j':
                old_cursor_pos = musicus.cursor_index
                if musicus.inc_cursor_index():
                    render_update = RenderUpdate.cursor_move(old_cursor_pos, musicus.cursor_index)
            elif ch == 'k':
                old_cursor_pos = musicus.cursor_index
                if musicus.dec_cursor_index():
                    render_update = RenderUpdate.cursor_move(old_cursor_pos, musicus.cursor_index)
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
            pass

        # logs.append('playing: {}  is_playing: {}'.format(musicus.playing, audio_backend.is_playing()))
        if musicus.playing and not audio_backend.is_playing():
            if musicus.inc_song_index():
                audio_backend.play(musicus.get_current_song())


if __name__ == '__main__':
    main_logs = []
    curses.wrapper(main, main_logs)
    for log in main_logs:
        print(log)
