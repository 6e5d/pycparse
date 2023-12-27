from buildc.depinfo import Depinfo
from buildc.build import nsdef

class Ppfunc:
	def __init__(self, params, body):
		self.params = params
		self.body = body

# limitation: preprocessing are all treated like they are placed to top
# only support plain define + simple function with concat
class Preprocessor:
	def __init__(self, proj):
		self.includes = []
		# ident -> (Ppfunc | str)
		self.immediates = dict()
		self.alias = dict()
		self.content = []
		depinfo = Depinfo()
		depinfo.build(proj)
		name, camel, snake = nsdef(proj)
		self.nsmacro(name, camel, snake)
		for path in depinfo.deps:
			name, camel, snake = nsdef(path)
			self.nsmacro(name, camel, snake)
	def nsmacro(self, name, camel, snake):
		self.directive(f"#define {name}(ident) {snake}_##ident")
		self.directive(f"#define {name.capitalize()}(ident) "
			f"{camel}##ident")
	def directive(self, line):
		if line.startswith("#include"):
			file = line.removeprefix("#include").strip()
			self.includes.append(file)
			return
		if line.startswith("#ifndef "):
			return
		if line.startswith("#endif"):
			return
		if line.startswith("#undef"):
			return
		if line.startswith("#define"):
			define = line.removeprefix("#define").strip()
			if "(" in define:
				name, rule = define.split(")")
				head, body = name.split("(")
				args = [sp.strip()
					for sp in body.split(",")]
				self.immediates[head.strip()] =\
					Ppfunc(args, rule.strip())
				return
			sp = define.split(" ", 1)
			if len(sp) == 1:
				# print("skip include guard define", sp)
				return
			symbol, string = sp
			if string[0].isnumeric():
				self.immediates[symbol] = string
			else:
				self.alias[symbol] = string
			return
		raise Exception(line)
	def proc_line_rule(self, line, sym, rule):
		offset = line.find(sym)
		if offset == -1:
			return False
		# check if substr is a full word
		before = line[:offset]
		if before and before[-1].isalnum():
			return False
		after = line[offset + len(sym):]
		if after and after[0].isalnum():
			return False
		if isinstance(rule, Ppfunc) and (not after or after[0] != "("):
			raise Exception(line)
		# now it is a valid substitute
		if isinstance(rule, str):
			return before + rule + after
		idx = after.find(")")
		params = [arg.strip() for arg in after[1:idx].split(",")]
		after = after[idx + 1:]
		if len(params) != len(rule.params):
			raise Exception(line, rule.params)
		# all asserts here are limitations
		assert len(params) == 1
		sp = rule.body.split("##")
		assert len(sp) == 2
		assert sp[1] == rule.params[0]
		return before + sp[0] + params[0] + after
	def proc_content(self):
		output = []
		for ln, line in enumerate(self.content):
			for sym, rule in self.immediates.items():
				ret = self.proc_line_rule(line, sym, rule)
				if ret != False:
					line = ret
			output.append(line)
		return output
	def preprocess(self, lines):
		includes = []
		ns = [None, None]
		for line in lines:
			line = line.rstrip("\n")
			if not line:
				continue
			line = line.lstrip("\t")
			if line.startswith("//"):
				continue
			if line.startswith("#"):
				self.directive(line)
			else:
				self.content.append(line)
		return self.proc_content()
