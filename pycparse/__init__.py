from importer import importer
importer("../../pyctok/pyctok", __file__)
importer("../../pylrparser/pylrparser", __file__)

def preprocess(lines):
	lines2 = []
	includes = []
	defines = dict()
	for line in lines:
		line = line.rstrip("\n")
		if not line:
			continue
		line1 = line.lstrip("\t")
		if line1.startswith("//"):
			continue
		if line1.startswith("#include"):
			file = line1.removeprefix("#include").strip()
			includes.append(file)
			continue
		if line1.startswith("#define"):
			# support 2 types of define: num, simple typedef
			define = line1.removeprefix("#define").strip()
			sp = define.split(" ", 1)
			if len(sp) != 2:
				print("skip define", sp)
				continue
			symbol, string = sp
			defines[symbol] = string
			continue
		if line1.startswith("#"):
			continue
		lines2.append(line)
	return lines2, includes, defines
