from importer import importer
importer("../../pyctok/pyctok", __file__)
from pyctok import Tokenizer

from .parse import parse

def strip_preprocess(lines):
	lines2 = []
	for line in lines:
		line = line.rstrip("\n")
		if line and line[0] == "#":
			continue
		lines2.append(line)
	return lines2

def parse_string(s):
	tok = Tokenizer()
	tok.tokenize(s)
	j = parse(tok.toks)
	return j
