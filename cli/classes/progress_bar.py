import sys

class ProgressBar:

  progress = 0

  def start(self, title):
    sys.stdout.write(title + ": |" + "-" * 40 + "|" + chr(8) * 41)
    sys.stdout.flush()
    self.progress = 0

  def update(self, x):
    global progress_x
    x = int(x * 40 / 100)
    sys.stdout.write(chr(9612) * (x - self.progress))
    sys.stdout.flush()
    self.progress = x

  def end(self):
    sys.stdout.write(chr(9612) * (40 - self.progress) + "|\n")
    sys.stdout.flush()