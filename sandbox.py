import shutil
import re
import os


class Sandbox(object):
    def __init__(self, sandbox_path):
        self.abspath = os.path.abspath(os.path.join(os.getcwd(), sandbox_path))
        self.relpath = sandbox_path

    def _init(self):
        pass
        # if path.exists(self.abspath):
        #     if not path.isdir(self.abspath):
        #         raise ValueError("{} exists and is not a directory".format(self.abspath))
            # shutil.rmtree(self.abspath)
        # makedirs(self.abspath)

    def __enter__(self):
        self._init()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # shutil.rmtree(self.abspath)
        return False

    def get_filepaths(self, pattern=''):
        relpaths = [os.path.join(self.relpath, f) for f in os.listdir(self.abspath) if re.match(pattern, f)]
        filepaths = [os.path.abspath(f) for f in relpaths]
        filepaths.sort()
        return filepaths

    def get_filepath(self, pattern=''):
        relpath = [os.path.join(self.relpath, f) for f in os.listdir(self.abspath) if re.match(pattern, f)]
        if relpath:
            return os.path.abspath(relpath[0])
        return None
