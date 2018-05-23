import plex

class ParseError(Exception):
	pass
class RunError(Exception):
	pass
	
class MyRunner:
	def __init__(self):
		self.st = {}
		self.command = None
		self.whatisit = None
		self.args= [False]*2
		self.negative = False
		self.tempVar = None
		self.iterations = 0
	def create_scanner(self,fp):
		letter = plex.Range('azAZ')
		digit = plex.Range('09')
		ID = letter + plex.Rep(letter|digit)
		keyword = plex.Str('print')
		OP1 = plex.Str('and','or')
		OP2 = plex.Str('not')
		equals = plex.Str('=')
		parenthesis = plex.Any('()')
		space = plex.Rep1(plex.Any(' \n\t'))
		tfFalse = plex.NoCase(plex.Str('false','f','0'))
		tfTrue = plex.NoCase(plex.Str('true','t','1'))
		
		lexicon = plex.Lexicon([
			(keyword,plex.TEXT),
			(OP1,plex.TEXT),
			(OP2,plex.TEXT),
			(tfTrue,'TRUE'),
			(tfFalse,'FALSE'),
			(ID,'ID'),
			(space,plex.IGNORE),
			(parenthesis,plex.TEXT),
			(equals,plex.TEXT)
			])
			
		self.scanner = plex.Scanner(lexicon,fp)
		self.la, self.val = self.next_token() #look ahead
	def parse(self,fp):
		self.create_scanner(fp)
		self.stmtList()
	def match(self,token):
		if self.la == token:
			self.la, self.val = self.next_token()
		else:
			raise ParseError("To self.la dn tautistike me to current token")
	def next_token(self):
		return self.scanner.read()
	def stmtList(self):
		if self.la == 'ID' or self.la == 'print':
			self.stmt()
			self.main_run()
			self.iterations = 0
			self.stmtList()
		elif self.la is None:
			return
	def stmt(self):
		if self.la == 'ID':
			if self.val not in self.st: self.st[self.val]=None
			self.tempVar = self.val
			self.command = 'store'
			self.match('ID')
			self.match('=')
			self.expr()
		elif self.la == 'print':
			self.command = 'print'
			self.match('print')
			self.expr()
		else:
			raise ParseError('Expected id or print')
	def expr(self):
		if self.la == '(' or self.la == 'ID' or self.la == 'TRUE' or self.la == 'FALSE':
			self.term()
			self.termTail()
		else:
			ParseError('Expected (,id or tf')
	def termTail(self):
		if self.la == 'and' or self.la == 'or':
			self.OP1()
			self.term()
			self.termTail()
		elif self.la in ('ID','print',None,')'):
			return
		else:
			raise ParseError('Expected \'and\' or \'or\'')
	def term(self):
		if self.la == '(' or self.la == 'ID' or self.la == 'TRUE' or self.la == 'FALSE' or self.la == 'not':
			if self.la == 'not':
				self.negative = True
			self.factor()
			self.factorTail()
		else:
			raise ParseError('Expected (,id or tf')
	def factorTail(self):
		if self.la == 'not':
			self.OP2()
			self.factor()
			self.factorTail()
		elif self.la in ('and','or','ID','print',None,')'):
			return
		else:
			raise ParseError('Expected not')
	def factor(self):
		if self.la == '(':
			if self.negative:
				self.negative = False
			self.match('(')
			self.expr()
			self.match(')')
		elif self.la == 'ID':
			if self.val in self.st:
				self.args[self.iterations] = self.st[self.val]
			else:
				raise RunError('Unknown Identifier')
			self.match('ID')
		elif self.la == 'TRUE':
			self.args[self.iterations] = True
			self.match('TRUE')
		elif self.la == 'FALSE':
			self.args[self.iterations] = False
			self.match('FALSE')
		elif self.la in ('not','and','or',None,')','print'):
			return
		else:
			raise ParseError('Expected (,id or tf')
		if self.negative:
			self.args[self.iterations] = not self.args[self.iterations]
			self.negative = False
		self.iterations+=1
	def OP1(self):
		if self.la == 'and':
			self.whatisit = 'and'
			self.match('and')
		elif self.la == 'or':
			self.whatisit = 'or'
			self.match('or')
		else:
			raise ParseError('Expected \'and\' or \'or\'')
	def OP2(self):
		if self.la == 'not':
			self.match('not')
		else:
			raise ParseError('Expected not')
	def main_run(self):
		if self.iterations == 1:
			temp = self.args[0]
		else:
			if self.whatisit == 'and':
				temp = self.args[0] and self.args[1]
			else:
				temp = self.args[0] or self.args[1]
		if self.command == 'print':
			print(temp)
		else:
			self.st[self.tempVar] = temp
			print("{} stored!".format(self.tempVar))
	

runner = MyRunner()

with open('commands.txt') as fp:
	try:
		runner.parse(fp)
	except ParseError as perr:
		print(perr)
