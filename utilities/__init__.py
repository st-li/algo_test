from os import path
import sys


cur_path = path.dirname(path.realpath(__file__))
parent_path = path.dirname(cur_path)

sys.path.append(parent_path)