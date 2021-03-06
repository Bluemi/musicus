import os.path
from functools import reduce


def file_or_dir_from_path(path):
    if os.path.isfile(path):
        return File.from_path(path)
    elif os.path.isdir(path):
        return Directory.from_path(path)
    raise Exception('path "{}" is neither file nor directory'.format(path))


class File:
    def __init__(self, path):
        self.path = path
        self.IS_FILE = True

    @staticmethod
    def from_path(path):
        return File(path)

    # noinspection PyMethodMayBeStatic
    def get_longest_sub_len(self):
        return 0


class Directory:
    class SubDirectory:
        def __init__(self, name):
            self.name = name
            self.IS_FILE = False

    class SubFile:
        def __init__(self, name):
            self.name = name
            self.IS_FILE = True

    def __init__(self, path, sub_dirs, sub_files, cursor):
        self.path = path
        self.sub_dirs = sub_dirs
        self.sub_files = sub_files
        self.cursor = cursor
        self.IS_FILE = False

    @staticmethod
    def from_path(path):
        try:
            files_dirs = os.listdir(path)
        except PermissionError:
            files_dirs = []
        return Directory(
            path,
            list(map(
                lambda d: Directory.SubDirectory(d),
                filter(lambda d: os.path.isdir(os.path.join(path, d)) and not d.startswith('.'), files_dirs)
            )),
            list(map(
                lambda f: Directory.SubFile(f),
                filter(lambda f: os.path.isfile(os.path.join(path, f)) and not f.startswith('.'), files_dirs)
            )),
            0
        )

    def get_subs(self):
        return self.sub_dirs + self.sub_files

    def get_longest_sub(self):
        if not self.get_subs():
            return ''
        return reduce(lambda sub1, sub2: sub1 if len(sub1.name) > len(sub2.name) else sub2, self.get_subs())

    def get_longest_sub_len(self):
        return len(self.get_longest_sub().name)

    def get_cursor_path(self):
        return os.path.join(self.path, self.get_subs()[self.cursor].name)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.path + '  dirs: ' + ','.join(self.sub_dirs) + '  cursor: ' + str(self.cursor)


def split_all(path):
    folders = []
    while 1:
        path, folder = os.path.split(path)

        if folder != "":
            folders.append(file_or_dir_from_path(os.path.join(path, folder)))
        else:
            if path != "":
                folders.append(file_or_dir_from_path(path))
            break

    folders.reverse()
    for index in range(len(folders)-1):
        folder = folders[index]
        for sub_index, sub in enumerate(folders[index].get_subs()):
            if os.path.join(folder.path, sub.name) == folders[index+1].path:
                folder.cursor = sub_index
                break

    return folders


class FileBrowser:
    def __init__(self):
        self.cwd = split_all(os.path.expanduser('~'))

    def go_left(self):
        if self.cwd:
            self.cwd.pop()
            return True
        return False

    def go_right(self):
        if not self.cwd[-1].IS_FILE:
            new_dir = self.cwd[-1].get_cursor_path()
            self.cwd.append(file_or_dir_from_path(new_dir))

    def go_up(self):
        self.go_left()
        self.cwd[-1].cursor = min(self.cwd[-1].cursor + 1, len(self.cwd[-1].get_subs())-1)
        self.go_right()

    def go_down(self):
        self.go_left()
        self.cwd[-1].cursor = max(self.cwd[-1].cursor - 1, 0)
        self.go_right()
