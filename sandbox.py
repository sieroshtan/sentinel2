import shutil
import re
import os


class Sandbox(object):
    """
    Context manager for sandbox folder
    """
    def __init__(self, sandbox_path):
        self.abspath = os.path.abspath(os.path.join(os.getcwd(), sandbox_path))
        self.relpath = sandbox_path

    def _init(self):
        """
        Create sandbox folder
        :return:
        """
        if os.path.exists(self.abspath):
            if not os.path.isdir(self.abspath):
                raise ValueError("{0} exists and is not a directory".format(self.abspath))
            shutil.rmtree(self.abspath)
        os.makedirs(self.abspath)

    def __enter__(self):
        self._init()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit from sandbox "mode", and delete all temporary files
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        shutil.rmtree(self.abspath)
        return False

    def get_filepaths(self, pattern=''):
        """
        Return filepaths from sandbox folder by regexp pattern
        :param pattern:
        :return:
        """
        relpaths = [os.path.join(self.relpath, f) for f in os.listdir(self.abspath) if re.match(pattern, f)]
        filepaths = [os.path.abspath(f) for f in relpaths]
        filepaths.sort()
        return filepaths

    def get_filepath(self, pattern=''):
        """
        Return filepath from sandbox folder by regexp pattern
        :param pattern:
        :return:
        """
        relpath = [os.path.join(self.relpath, f) for f in os.listdir(self.abspath) if re.match(pattern, f)]
        if relpath:
            return os.path.abspath(relpath[0])
        return None
