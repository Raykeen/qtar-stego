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


def print_progress_bar(iteration, total, time, prefix='', suffix='', decimals=1, length=100, fill='█', **kwargs):
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
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)

    remained = format_time(time * (total - iteration))

    print('\r%s |%s| %s%% | %s/%s | %s remained | %s' %
          (prefix, bar, percent, iteration, total, remained, suffix),
          end='\r', **kwargs)

    # Print New Line on Complete
    if iteration == total:
        print(**kwargs)


def format_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)
