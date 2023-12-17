from importer import importer
importer("../../pyctok/pyctok", __file__)
importer("../../pylrparser/pylrparser", __file__)

def strip_preprocess(lines):
	lines2 = []
	for line in lines:
		line = line.rstrip("\n")
		if line and line[0] == "#":
			continue
		lines2.append(line)
	return lines2
