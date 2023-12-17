import sys
from . import strip_preprocess, parse_string

if len(sys.argv) >= 2:
	lines = [line for line in open(sys.argv[1])]
	lines = strip_preprocess(lines)
	s = "\n".join(lines)
	parse_string(s)
else:
	s = "int (*(*p(int))(int a, int b))(int (*a)(int x, int y), int b) {}"
	parse_string(s)
