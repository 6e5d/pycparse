import sys
from pathlib import Path

from pyctok import Tokenizer
import pylrparser
from pylrparser.parser import cached_parser
from . import preprocess

primitives = ["size_t",
	"uint8_t", "uint32_t", "uint64_t",
	"int8_t", "int32_t", "int64_t",
	"int", "long", "float", "double", "char", "bool"
]
consts = ["NULL"]
keywords = ["typedef", "if", "else", "for", "while",
	"void", "return", "sizeof", "continue", "break", "static"]
sue = ["struct", "union", "enum"]

def proc_tok(tok):
	if tok[1] in [
		",", ";",
		"(", ")",
		"[", "]",
		"{", "}",
		"||", "&&",
	] + keywords:
		return (tok[1], tok[1])
	if tok[0] == 32:
		if tok[1] == "=":
			return ("=", tok[1])
		elif tok[1] in ["/", "%"]:
			return ("divmod", tok[1])
		elif tok[1] in ["+", "-"]:
			return ("add", tok[1])
		elif tok[1] in ["<", "<=", ">", ">="]:
			return ("relation", tok[1])
		elif tok[1] in ["==", "!="]:
			return ("eqneq", tok[1])
		elif tok[1][-1] == "=":
			return ("opassign", tok[1])
	match tok:
		case (33, "*"):
			return ("*", "*")
		case (31, "&"):
			return ("prefix", "&p")
		case (31, "-"):
			return ("prefix", "-n")
		case (31, "+"):
			return ("prefix", "+n")
		case (31, x):
			return ("prefix", x)
		case (32, "->"):
			return ("member", "->")
		case (32, "."):
			return ("member", ".")
		case (21, x):
			if "_" in x or x in consts:
				return ("var", x)
			else:
				return ("type", x)
		case (22, x):
			if x in primitives:
				return ("type", x)
			elif x in sue:
				return ("sue", x)
			else:
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
		case "braceinit":
			return ["braceinit", t(j[2])]
		case "return":
			return ["return", t(j[2])]
		case "sizeof":
			return ["sizeof", t(j[3])]
		case "returnvoid":
			return ["return"]
		case "continue":
			return ["continue"]
		case "break":
			return ["break"]
		case "!":
			return []
		case "blocks":
			return t(j[1]) + [t(j[2])]
		case "member":
			return [s(j[2]), t(j[1]), s(j[3])]
		case "cast":
			return ["cast", t(j[4]), t(j[2])]
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
		case "else":
			return ["else", t(j[2])]
		case "for":
			return ["for", [
				t(j[3]), t(j[5]), t(j[7])
			], t(j[9])]
		case "while":
			return ["while", t(j[3]), t(j[5])]
		case "stmtexpr":
			return ["stmtexpr", t(j[1])]
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
		case "sval":
			return t(j[2])
		case "sinits":
			return t(j[1]) + [t(j[3])]
		case "sinits.":
			return [t(j[1])]
		case "sinit":
			return [s(j[2]), t(j[4])]
		case "sval0":
			return "0"
		case "decinit":
			return ["decinit", t(j[1]), t(j[3])]
		case "sdbodys":
			return t(j[1]) + [t(j[3])]
		case "sdbodys.":
			return [t(j[1])]
		case "array":
			return ["@", t(j[1]), t(j[3])]
		case "prefix":
			return [j[1], t(j[2])]
		case "*p":
			return ["*p", t(j[2])]
		case "arg":
			return ["arg", t(j[1]), t(j[3])]
		case "dparams":
			return t(j[1]) + [t(j[3])]
		case "dparams.":
			return [t(j[1])]
		case "simple":
			return [t(j[1]), t(j[2])]
		case "ptr":
			return ["ptr", t(j[2])]
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
			return t[j[1]] + [t(j[3])]
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
		case x:
			raise Exception(j[0])

def parse_string(s):
	lines = [line for line in s.split("\n")]
	lines, includes, defines = preprocess(lines)
	s = "\n".join(lines)

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
	return (t(j), includes, defines)
