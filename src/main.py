import curses
import datetime
import os
import string
from enum import Enum

import songsdatabase
from audio_backend import AudioBackend
from file_browser import FileBrowser
from playlist import PlaylistManager


SONGS_DIRECTORY = '/home/alok/Musik/Rock Blues/Led Zeppelin/'
PLAYLIST_CHARACTERS = string.digits + string.ascii_letters
PLAYLIST_SPACE = 40
MAX_FILE_WIDTH = 120


def format_duration(duration):
    minutes = duration // 60
    hour = minutes // 60
    if hour > 0:
        return datetime.time(second=duration % 60, minute=minutes % 60, hour=hour % 24).strftime('%H:%M:%S')
    else:
        return datetime.time(second=duration % 60, minute=minutes).strftime('%M:%S')


class RenderMode(Enum):
    NORMAL = 0
    FILE_BROWSER = 1


def limit_str(s, size):
    if len(s) > size:
        return s[:size-3] + '...'
    return s


def pad_spaces(s, size):
    if len(s) < size:
        return s + ' '*(size - len(s))
    return s


def get_render_width(d, maxi=None):
    width = 0
    if not d.IS_FILE:
        width = d.get_longest_sub_len() + 5
    return width if maxi is None else min(width, maxi)


def render_file_browser(scr, cwd, offset):
    scr.clear()
    render_width = sum(map(lambda d: get_render_width(d, MAX_FILE_WIDTH), cwd))
    left_shift = max(render_width - (curses.COLS - PLAYLIST_SPACE), 0)
    for dir_index, directory in enumerate(cwd):
        if not directory.IS_FILE:
            up_shift = max(directory.cursor + 4 - curses.LINES, 0)
            x_pos = offset - left_shift
            longest_sub_len = min(directory.get_longest_sub_len(), MAX_FILE_WIDTH)
            for index, sub in enumerate(directory.get_subs()):
                y_pos = index - up_shift
                if y_pos < 0:
                    continue
                if y_pos >= curses.LINES:
                    break
                if directory.cursor == index and dir_index != len(cwd)-1:
                    if dir_index == len(cwd) - 2:
                        # cursor color
                        color_pair = curses.color_pair(2)
                    else:
                        color_pair = curses.color_pair(3)
                else:
                    if sub.IS_FILE:
                        color_pair = curses.color_pair(1)
                    else:
                        color_pair = curses.color_pair(5)
                render_string = pad_spaces(limit_str(sub.name, MAX_FILE_WIDTH), longest_sub_len)
                if x_pos + longest_sub_len >= PLAYLIST_SPACE:
                    overlap = PLAYLIST_SPACE - x_pos
                    if overlap > 0:
                        render_string = render_string[overlap:]
                        x_pos += overlap
                    scr.addstr(
                        y_pos,
                        max(x_pos, 0),
                        render_string,
                        color_pair
                    )
            offset += get_render_width(directory, MAX_FILE_WIDTH)


class Musicus:
    def __init__(self):
        self.render_mode = RenderMode.NORMAL
        self.song_index = 0
        self.cursor_index = 0
        self.songs = songsdatabase.SongsDatabase.from_dir(SONGS_DIRECTORY)
        self.playing = False
        self.audio_backend = AudioBackend()
        self.playlists = PlaylistManager()
        self.file_browser = FileBrowser()

    def render_line(self, scr, line_index):
        song = self.songs.song_list[line_index]
        if line_index == self.song_index:
            color_pair = 2
        elif line_index == self.cursor_index:
            color_pair = 3
        else:
            color_pair = 1
        scr.addstr(line_index, PLAYLIST_SPACE, song, curses.color_pair(color_pair))

    def render_status(self, scr):
        scr.addstr(curses.LINES - 3, 0, ' '*curses.COLS)
        scr.addstr(curses.LINES - 3, 0, os.path.basename(self.get_current_song()), curses.color_pair(4))

    def render_time(self, scr):
        if self.audio_backend.current_player is not None:
            play_sign = '>' if self.playing else '|'
            played_duration = format_duration(int(self.audio_backend.current_player.get_played_duration()))
            hole_duration = format_duration(int(self.audio_backend.current_player.get_duration()))
            text = ' {} {} / {}'.format(play_sign, played_duration, hole_duration)
            scr.addstr(curses.LINES - 2, 0, text, curses.color_pair(4))
        else:
            scr.addstr(curses.LINES - 2, 0, ' '*curses.COLS, curses.color_pair(4))

    @staticmethod
    def render_playlist_name(scr, next_playlist_name):
        name = 'new playlist: {:<60}'.format(''.join(next_playlist_name))
        scr.addstr(curses.LINES - 3, 0, name, curses.color_pair(4))

    def render_songs(self, scr):
        for index, song in enumerate(self.songs.song_list):
            if index >= curses.LINES - 2:
                break
            self.render_line(scr, index)

    def render_playlists(self, scr):
        for index, playlist in enumerate(self.playlists.playlists):
            scr.addstr(index, 0, playlist.name, curses.color_pair(1))

    def render_file_browser(self, scr):
        scr.addstr(
            0,
            PLAYLIST_SPACE,
            '{:<80}'.format('/'.join(map(lambda d: os.path.basename(d.path), self.file_browser.cwd)))
        )
        render_file_browser(scr, self.file_browser.cwd, PLAYLIST_SPACE)

    def render(self, scr, render_update):
        """
        :type render_update: RenderUpdate
        """
        if render_update.update_type == UpdateType.NORMAL:
            scr.clear()
            self.render_mode = RenderMode.NORMAL
            self.render_songs(scr)
            self.render_time(scr)
            self.render_playlists(scr)
            scr.refresh()
        elif render_update.update_type == UpdateType.CURSOR_MOVE:
            self.render_line(scr, render_update.old_cursor_pos)
            self.render_line(scr, render_update.new_cursor_pos)
        elif render_update.update_type == UpdateType.STATUS_LINE:
            self.render_status(scr)
        elif render_update.update_type == UpdateType.TIME:
            self.render_time(scr)
        elif render_update.update_type == UpdateType.NEW_PLAYLIST:
            Musicus.render_playlist_name(scr, render_update.playlist_name)
        elif render_update.update_type == UpdateType.PLAYLISTS:
            self.render_playlists(scr)
        elif render_update.update_type == UpdateType.FILE_BROWSER:
            self.render_mode = RenderMode.FILE_BROWSER
            self.render_file_browser(scr)

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


class UpdateType(Enum):
    NORMAL = 0
    CURSOR_MOVE = 1
    STATUS_LINE = 2
    TIME = 3
    PLAYLISTS = 4
    NEW_PLAYLIST = 5
    FILE_BROWSER = 6


class RenderUpdate:
    @staticmethod
    def normal():
        return RenderUpdate(
            UpdateType.NORMAL
        )

    @staticmethod
    def cursor_move(old_cursor_pos, new_cursor_pos):
        return RenderUpdate(
            UpdateType.CURSOR_MOVE,
            old_cursor_pos=old_cursor_pos,
            new_cursor_pos=new_cursor_pos
        )

    @staticmethod
    def status_line():
        return RenderUpdate(
            UpdateType.STATUS_LINE
        )

    @staticmethod
    def time():
        return RenderUpdate(
            UpdateType.TIME
        )

    @staticmethod
    def new_playlist(name):
        return RenderUpdate(
            UpdateType.NEW_PLAYLIST,
            playlist_name=name
        )

    @staticmethod
    def playlists():
        return RenderUpdate(
            UpdateType.PLAYLISTS
        )

    @staticmethod
    def file_browser():
        return RenderUpdate(
            UpdateType.FILE_BROWSER
        )

    def __init__(self, update_type, old_cursor_pos=None, new_cursor_pos=None, playlist_name=None):
        self.update_type = update_type
        self.old_cursor_pos = old_cursor_pos
        self.new_cursor_pos = new_cursor_pos
        self.playlist_name = playlist_name


def main(stdscr: curses.window, logs):
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)

    stdscr.nodelay(True)
    curses.curs_set(False)

    # config.init()

    musicus = Musicus()
    render_updates: RenderUpdate or None = [RenderUpdate.normal()]

    last_duration = None
    next_playlist_name = None
    while True:
        for render_update in render_updates:
            musicus.render(stdscr, render_update)
            render_updates = []

        ch = stdscr.getch()
        if ch != -1:
            if next_playlist_name is not None:
                if ch == 10:
                    musicus.playlists.new(''.join(next_playlist_name))
                    next_playlist_name = None
                    render_updates.append(RenderUpdate.status_line())
                    render_updates.append(RenderUpdate.playlists())
                elif ch == 27:
                    next_playlist_name = None
                    render_updates.append(RenderUpdate.status_line())
                else:
                    c = chr(ch)
                    if c in PLAYLIST_CHARACTERS:
                        next_playlist_name.append(chr(ch))
                        render_updates.append(RenderUpdate.new_playlist(next_playlist_name))
            else:
                if musicus.render_mode == RenderMode.NORMAL:
                    if ch == ord('q'):
                        break
                    elif ch == ord('2'):
                        render_updates.append(RenderUpdate.file_browser())
                    elif ch == ord('j'):
                        old_cursor_pos = musicus.cursor_index
                        if musicus.inc_cursor_index():
                            render_updates.append(RenderUpdate.cursor_move(old_cursor_pos, musicus.cursor_index))
                    elif ch == ord('k'):
                        old_cursor_pos = musicus.cursor_index
                        if musicus.dec_cursor_index():
                            render_updates.append(RenderUpdate.cursor_move(old_cursor_pos, musicus.cursor_index))
                    elif ch == ord('c'):
                        if musicus.playing:
                            musicus.playing = False
                            musicus.audio_backend.stop()
                        else:
                            musicus.playing = True
                            musicus.audio_backend.resume()
                        render_updates.append(RenderUpdate.time())
                    elif ch == ord('h'):
                        musicus.audio_backend.seek(-5)
                    elif ch == ord('l'):
                        musicus.audio_backend.seek(5)
                    elif ch == 10:  # enter
                        if musicus.playing:
                            musicus.audio_backend.stop()
                        old_cursor_pos = musicus.song_index
                        musicus.song_index = musicus.cursor_index
                        render_updates.append(RenderUpdate.cursor_move(old_cursor_pos, musicus.song_index))
                        render_updates.append(RenderUpdate.status_line())
                        render_updates.append(RenderUpdate.time())
                        musicus.playing = True
                        musicus.audio_backend.play(musicus.get_current_song())
                    elif ch == ord('n'):
                        next_playlist_name = []
                        render_updates.append(RenderUpdate.new_playlist(next_playlist_name))
                    else:
                        logs.append(str(ch))
                elif musicus.render_mode == RenderMode.FILE_BROWSER:
                    if ch == ord('q'):
                        break
                    elif ch == ord('l'):
                        musicus.file_browser.go_right()
                        render_updates.append(RenderUpdate.file_browser())
                    elif ch == ord('h'):
                        musicus.file_browser.go_left()
                        render_updates.append(RenderUpdate.file_browser())
                    elif ch == ord('j'):
                        musicus.file_browser.go_up()
                        render_updates.append(RenderUpdate.file_browser())
                    elif ch == ord('k'):
                        musicus.file_browser.go_down()
                        render_updates.append(RenderUpdate.file_browser())
                    elif ch == ord('1'):
                        render_updates.append(RenderUpdate.normal())

        if musicus.playing and not musicus.audio_backend.is_playing():
            old_cursor_pos = musicus.song_index
            if musicus.inc_song_index():
                musicus.audio_backend.play(musicus.get_current_song())
                render_updates.append(RenderUpdate.cursor_move(old_cursor_pos, musicus.song_index))
                render_updates.append(RenderUpdate.status_line())

        if musicus.audio_backend.current_player is not None:
            current_duration = int(musicus.audio_backend.current_player.get_played_duration())
            if current_duration != last_duration:
                render_updates.append(RenderUpdate.time())
                last_duration = current_duration


if __name__ == '__main__':
    main_logs = []
    curses.wrapper(main, main_logs)
    for log in main_logs:
        print(log)
