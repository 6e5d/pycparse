from importer import importer
importer("../../pyctok/pyctok", __file__)
importer("../../pylrparser/pylrparser", __file__)

def preprocess(lines):
	lines2 = []
	includes = []
	defines = dict()
	ns = [None, None]
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
			if symbol.startswith("NS_NAME("):
				sp2 = string.split("##")
				assert len(sp2) == 2
				ns[0] = sp2[0]
				continue
			if symbol.startswith("NS_TYPE("):
				sp2 = string.split("##")
				assert len(sp2) == 2
				ns[1] = sp2[0]
				continue
			defines[symbol] = string
			continue
		if line1.startswith("#"):
			continue
		lines2.append(line)
		assert ns[0] != None
	return lines2, includes, defines, ns
