import sys
from pathlib import Path

from pyctok import Tokenizer
import pylrparser
from pylrparser.parser import cached_parser
from .preprocessor import Preprocessor
from pycdb import btypes, keywords, consts

sue = ["struct", "union", "enum"]

def proc_tok(tok):
	if tok[1] in btypes:
		return ("type", tok[1])
	if tok[1] in sue:
		return ("sue", tok[1])
	if tok[1] in consts:
		return ("var", tok[1])
	if tok[1] in [
		",", ";",
		"(", ")",
		"[", "]",
		"{", "}",
		"||", "&&",
		"|", "&", "^",
		",", "*", ":"
	] or tok[1] in keywords:
		return (tok[1], tok[1])
	if tok[0] == 32:
		if tok[1] == "=":
			return ("=", tok[1])
		elif tok[1] in ["==", "!="]:
			return ("eqneq", tok[1])
		elif tok[1] in ["<", "<=", ">", ">="]:
			return ("relation", tok[1])
		elif tok[1][-1] == "=": # must after >= <= == !=
			return ("opassign", tok[1])
		elif tok[1] in ["/", "%"]:
			return ("divmod", tok[1])
		elif tok[1] in ["+", "-"]:
			return ("add", tok[1])
		elif tok[1] in ["<<", ">>"]:
			return ("bitshift", tok[1])
	match tok:
		case (31, "&"):
			return ("prefix", "&p")
		case (31, "-"):
			return ("prefix", "-n")
		case (31, "+"):
			return ("prefix", "+n")
		case (31, x):
			return ("prefix", x)
		case (32, "->"):
			return ("field", "->")
		case (32, "."):
			return ("field", ".")
		case (21, x):
			if x[0].islower():
				return ("var", x)
			else:
				# F_x is type
				# FxX is type
				# F_X is var(const)
				idx = x.find("_")
				if idx == -1:
					return ("type", x)
				elif x[idx + 1].isupper():
					return ("var", x)
				return ("type", x)
		case (22, x):
			return ("var", x)
		case (11, x):
			return ("num", x)
		case (12, x):
			return ("str", x)
		case (13, x):
			return ("char", x)
		case x:
			raise Exception(x)

def s(j):
	assert isinstance(j, str)
	return j

def t(j):
	if isinstance(j, str):
		raise Exception(j)
	match j[0]:
		case "+":
			return t(j[1])
		case ".":
			return s(j[1])
		case "binop" | "assign":
			return [s(j[2]), t(j[1]), t(j[3])]
		case "return":
			return ["return", t(j[2])]
		case "sizeof":
			return ["sizeof", t(j[3])]
		case "returnvoid":
			return ["returnvoid"]
		case "continue":
			return ["continue"]
		case "break":
			return ["break"]
		case "!":
			return []
		case "blocks":
			return t(j[1]) + [t(j[2])]
		case "field":
			return [s(j[2]), t(j[1]), s(j[3])]
		case "cast" | "casts":
			return ["cast", t(j[2]), t(j[4])]
		case "call":
			return ["apply", t(j[1]), t(j[3])]
		case "callvoid":
			return ["apply", t(j[1]), []]
		case "params":
			return t(j[1]) + [t(j[3])]
		case "params.":
			return [t(j[1])]
		case "begin":
			return ["begin"] + t(j[2])
		case "if":
			return ["if", t(j[3]), t(j[5]), t(j[6])]
		case "elif":
			return ["elif", t(j[2])]
		case "switch":
			return ["case", t(j[3])] + t(j[6])
		case "cases":
			return t(j[1]) + [t(j[2])]
		case "cases.":
			return [t(j[1])]
		case "case":
			return [t(j[2]), t(j[4])]
		case "default":
			return ["default", t(j[3])]
		case "else":
			return ["else", t(j[2])]
		case "for":
			return ["for", [
				t(j[3]), t(j[5]), t(j[7])
			], t(j[9])]
		case "while":
			return ["while", t(j[3]), t(j[5])]
		case "stmtexpr":
			return ["expr", t(j[1])]
		case "stmtdec":
			return ["stmtdec", t(j[1]), t(j[2])]
		case "stmts":
			return t(j[1]) + [t(j[2])]
		case "type":
			return ["type", t(j[1]), t(j[2])]
		case "stmtdec_bodys":
			return t(j[1]) + [t(j[3])]
		case "stmtdec_bodys.":
			return [t(j[1])]
		case "decfun":
			return ["decfun"] + t(j[1])
		case "defun":
			return ["defun"] + t(j[1]) + [t(j[2])]
		case "defun_static":
			return ["static"] + t(j[2]) + [t(j[3])]
		case "declare":
			return ["declare", t(j[1]), t(j[2])]
		case "brace_a":
			return ["aval"] + t(j[2])
		case "brace_s":
			return ["sval"] + t(j[2])
		case "member_s.":
			return [t(j[1])]
		case "member_s":
			return t(j[1]) + [t(j[3])]
		case "member_a.":
			return [t(j[1])]
		case "member_a":
			return t(j[1]) + [t(j[3])]
		case "designated":
			return [s(j[2]), t(j[4])]
		case "sval":
			assert len(j) == 5
			return ["casts", t(j[2]), t(j[4][2])]
		case "var":
			return ["var", t(j[1])]
		case "set":
			return ["set", t(j[1]), t(j[3])]
		case "sets":
			return ["sets", t(j[1]), t(j[3])]
		case "array":
			return ["Array", t(j[1]), s(j[3])]
		case "prefix":
			return [j[1], t(j[2])]
		case "&p":
			return ["&p", t(j[2])]
		case "*p":
			return ["*p", t(j[2])]
		case "dvoid":
			assert j[1] == "void"
			return []
		case "dparams":
			return t(j[1]) + [t(j[3])]
		case "dparams.":
			return [t(j[1])]
		case "simple":
			return [t(j[1]), t(j[2])]
		case "ptr":
			return ["Ptr", t(j[2])]
		case "arg":
			return ["Arg", t(j[1]), t(j[3])]
		case "sue":
			return [s(j[1]).capitalize(), s(j[2])]
		case "paren":
			return t(j[2])
		case "typedef_su":
			return ["typedef_su", s(j[2]), t(j[4]), s(j[6])]
		case "typedef_camelize":
			return ["typedef_camelize", s(j[2]), s(j[3])]
		case "typedef_camelize_su":
			return ["typedef_camelize_su", s(j[2]), s(j[3]), s(j[4])]
		case "declares.":
			return [t(j[1])]
		case "declares":
			return [t(j[1])] + t(j[3])
		case "index":
			return ["@", t(j[1]), t(j[3])]
		case "numeric":
			lit = s(j[1])
			if "." in lit:
				if lit.endswith("f"):
					return ["lit", "float", lit]
				else:
					return ["lit", "double", lit]
			return ["lit", "int", lit]
		case "strlit":
			return ["lit", "str", t(j[1])]
		case "strcat.":
			return s(j[1])
		case "strcat":
			return t(j[1]) + s(j[2])
		case "char":
			return ["lit", "char", s(j[1])]
		case "comma":
			return [",", t(j[1]), t(j[3])]
		case x:
			raise Exception(j[0])

def alias_recurse(j, table):
	if isinstance(j, str):
		if j in table:
			return table[j]
		return j
	for idx, jj in enumerate(j):
		j[idx] = alias_recurse(jj, table)
	return j

def parse_string(s):
	tok = Tokenizer()
	tok.tokenize(s)
	syms = []
	origs = []
	for tok in tok.toks:
		sym, orig = proc_tok(tok)
		syms.append(sym)
		origs.append(orig)
	src = Path(__file__).parent / "rules.txt"
	cached = Path(__file__).parent /  "rules.json"
	parser = cached_parser(src, cached)
	j = parser.parse(syms, origs)
	j = t(j)
	return j

# the alias is prepend to the preprocessor
# this is for first parsing the header
# then use type aliases defined in header in source file
def parse_project_file(file, proj, alias = dict()):
	lines = [line for line in open(file)]
	pp = Preprocessor(proj, file, alias)
	lines = pp.preprocess(lines)
	s = "\n".join(lines)
	j = parse_string(s)
	j = alias_recurse(j, pp.alias)
	return (j, pp.includes, pp.alias)
