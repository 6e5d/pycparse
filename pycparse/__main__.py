import sys
from .parse import parse_string

s = sys.stdin.read()
print(parse_string(s))
