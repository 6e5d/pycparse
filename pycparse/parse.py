from pathlib import Path

class Parser():
	def __init__(self):
		self.stack = []
	def block(self, toks):
		return toks[1:]
	def blocks(self, toks):
		while toks:
			toks = self.block(toks)

def parse(toks):
	parser = Parser()
	parser.blocks(toks)
	print(parser.stack)
