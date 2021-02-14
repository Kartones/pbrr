import sys

import colorama

from pbrr.pbrr import PBRR

if __name__ == "__main__":
    colorama.init()

    if len(sys.argv) < 3:
        print("Please specify data path folder and opml filename as arguments")
        print("e.g.: python3 run.py feeds subscriptions.xml")
        exit(1)

    reader = PBRR(data_path=sys.argv[1], opml_filename=sys.argv[2])
    reader.run()
