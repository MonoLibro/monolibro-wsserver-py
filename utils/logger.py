import os
import datetime
from ColorStr import parse

class Logger:
    def __init__(self, write_to_file = True):
        self.filename = datetime.datetime.now().strftime(r"log_%d-%m-%Y_%H-%M-%S.txt")
        self.write_to_file = write_to_file
        if write_to_file:
            if not os.path.isdir("./logs"):
                os.mkdir("./logs")
            self.file = open(f"./logs/{self.filename}", "w")
    
    def flush(self):
        if self.write_to_file:
            self.file.flush()

    def info(self, *info):
        time = datetime.datetime.now().strftime(r"%d-%m-%Y %H:%M:%S")
        print(parse(f"[{time}][§bINFO§0] {' '.join(info)}"))
        if self.write_to_file:
            self.file.write(f"[{time}][INFO] {' '.join(info)}\n")
            self.flush()
    
    def warn(self, *info):
        time = datetime.datetime.now().strftime(r"%d-%m-%Y %H:%M:%S")
        print(parse(f"[{time}][§yWARN§0] {' '.join(info)}"))
        if self.write_to_file:
            self.file.write(f"[{time}][WARN] {' '.join(info)}\n")
            self.flush()
    
    def err(self, *info):
        time = datetime.datetime.now().strftime(r"%d-%m-%Y %H:%M:%S")
        print(parse(f"[{time}][§rERR§0] {' '.join(info)}"))
        if self.write_to_file:
            self.file.write(f"[{time}][ERR] {' '.join(info)}\n")
            self.flush()

    def close(self):
        if self.write_to_file:
            self.file.close()