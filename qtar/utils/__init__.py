from collections import OrderedDict
from timeit import default_timer as timer
import ntpath


class benchmark(object):

    def __init__(self, msg, fmt="%0.3g"):
        self.msg = msg
        self.fmt = fmt

    def __enter__(self):
        self.start = timer()
        return self

    def __exit__(self, *args):
        t = timer() - self.start
        print(("%s : " + self.fmt + " seconds") % (self.msg, t))
        self.time = t


def extract_filename(path):
    return ntpath.basename(path).split(".")[0]


def print_progress_bar(iteration, total, time, prefix='', suffix='', decimals=1, **kwargs):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))

    remained = format_time(time * (total - iteration))

    if suffix is None:
        suffix = ''

    print('\r%s | %s%% | %s/%s | %s remained | %s' %
          (prefix, percent, iteration, total, remained, suffix),
          end='\r', **kwargs)

    # Print New Line on Complete
    if iteration == total:
        print(**kwargs)


def format_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)


class ClassPropertyDescriptor(object):

    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()

    def __set__(self, obj, value):
        if not self.fset:
            raise AttributeError("can't set attribute")
        type_ = type(obj)
        return self.fset.__get__(obj, type_)(value)

    def setter(self, func):
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)
        self.fset = func
        return self


def classproperty(func):
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)

    return ClassPropertyDescriptor(func)


def pick(dict_, keys):
    return OrderedDict((key, dict_[key]) for key in keys if key in dict_)


def pick_values(dict_, keys):
    return list(pick(dict_, keys).values())


def flatten(lst):
    flat_list = []
    for item in lst:
        if isinstance(item, (tuple, list)):
            flat_list.extend(item)
        else:
            flat_list.append(item)
    return flat_list