import sys
from .parse import parse_string
from . import strip_preprocess

lines = [line for line in open(sys.argv[1])]
lines = strip_preprocess(lines)
s = "\n".join(lines)
print(parse_string(s))
