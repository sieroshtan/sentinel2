import shutil
from os import path, listdir, makedirs, getcwd


class Sandbox(object):
    def __init__(self, sandbox_path):
        self.abspath = path.abspath(path.join(getcwd(), sandbox_path))
        self.relpath = sandbox_path

    def _init(self):
        if path.exists(self.abspath):
            if not path.isdir(self.abspath):
                raise ValueError("{} exists and is not a directory".format(self.abspath))
            shutil.rmtree(self.abspath)
        makedirs(self.abspath)

    def __enter__(self):
        self._init()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # shutil.rmtree(self.abspath)
        return False

    def get_filepaths(self, startswith=''):
        relpaths = [path.join(self.relpath, f) for f in listdir(self.abspath)]
        filepaths = [path.abspath(f) for f in relpaths if startswith in f]
        filepaths.sort()
        return filepaths
