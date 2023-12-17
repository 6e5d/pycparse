from pathlib import Path

from pyctok import Tokenizer
import pylrparser
from pylrparser.parser import Parser

def proc_tok(tok):
	if tok[1] in ",;()[]{}":
		return (tok[1], tok[1])
	if tok[0] == 32 and tok[1][-1] == "=":
		return ("Assign", tok[1])
	if tok[0] == 32 and tok[1] in "*/%":
		return ("Mul", tok[1])
	if tok[0] == 32 and tok[1] in "+-":
		return ("Add", tok[1])
	match tok:
		case (32, "->"):
			return ("Member", "->")
		case (32, "."):
			return ("Member", ".")
		case (32, "."):
			return ("Member", ".")
		case (31, "*"):
			return ("Deref", "*")
		case (21, x):
			return ("Var", x)
		case (11, x):
			return ("Num", x)
		case (12, x):
			return ("Str", x)
		case (13, x):
			return ("Char", x)
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
		case "add" | "divmod" | "assign" | "member":
			return [s(j[2]), t(j[1]), t(j[3])]
		case "call":
			return [t(j[1]), t(j[3])]
		case "params":
			return [t(j[1])] + t(j[3])
		case "params.":
			return [t(j[1])]
		case "begin":
			return ["begin"] + t(j[2])
		case "stmts":
			return [t(j[1])] + t(j[2])
		case "stmts.":
			return [t(j[1])]
		case "defun":
			return t(j[1]) + [t(j[2])]
		case "declare":
			return [t(j[1]), t(j[2])]
		case "fun":
			return [t(j[1]), t(j[3])]
		case "dparams":
			return t(j[1]) + [t(j[3])]
		case "dparams.":
			return [t(j[1])]
		case "simple":
			return [t(j[1]), t(j[2])]
		case "ptr":
			return ["*", t(j[2])]
		case "paren":
			return t(j[2])
		case "index":
			return ["@", t(j[1]), t(j[3])]
		case "str":
			return f'"{j[1]}"'
		case "char":
			return f"'{j[1]}'"
		case x:
			raise Exception(j[0])

def parse_string(s):
	tok = Tokenizer()
	tok.tokenize(s)
	syms = []
	origs = []
	for tok in tok.toks:
		sym, orig = proc_tok(tok)
		syms.append(sym)
		origs.append(orig)
	rule_string = open(Path(__file__).parent / "rules.txt").read()
	parser = Parser(rule_string)
	j = parser.parse(syms, origs)
	return t(j)
