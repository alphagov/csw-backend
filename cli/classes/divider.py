import sys


class Divider:

    def line(self):
        sys.stdout.write("\n" + chr(8213) * 80 + "\n")
        sys.stdout.flush()
