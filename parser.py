import plex
"""
EXPRESSIONS
<Program> -> Stmt_List #
Stmt_List -> Stmt Stmt_List | e
Stmt -> id = Expr | print Expr
Expr -> Term Term_Tail
Term_Tail -> OP1 Term Term_Tail | e
Term -> Factor Factor_Tail 
Factor_Tail -> OP2 Factor Factor_Tail | e
Factor -> (Expr) | id | tf | e
OP1 -> and | or
OP2 -> not

"""

class ParseError(Exception):
	pass
	
	
class MyParser:
	def __init__(self):
		self.st = {}
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
		print("Match Attemt")
		if self.la == token:
			self.la, self.val = self.next_token()
		else:
			raise ParseError("To self.la dn tautistike me to current token")
	def next_token(self):
		return self.scanner.read()
	def stmtList(self):
		if self.la == 'ID' or self.la == 'print':
			self.stmt()
			self.stmtList()
		elif self.la is None:
			return
	def stmt(self):
		if self.la == 'ID':
			self.match('ID')
			self.match('=')
			self.expr()
		elif self.la == 'print':
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
			self.match('(')
			self.expr()
			self.match(')')
		elif self.la == 'ID':
			self.match('ID')
		elif self.la == 'TRUE':
			self.match('TRUE')
		elif self.la == 'FALSE':
			self.match('FALSE')
		elif self.la in ('not','and','or',None,')','print'):
			return
		else:
			raise ParseError('Expected (,id or tf')
	def OP1(self):
		if self.la == 'and':
			self.match('and')
		elif self.la == 'or':
			self.match('or')
		else:
			raise ParseError('Expected \'and\' or \'or\'')
	def OP2(self):
		if self.la == 'not':
			self.match('not')
		else:
			raise ParseError('Expected not')
	

parser = MyParser()
with open('commands.txt') as fp:
	try:
		parser.parse(fp)
	except ParseError as perr:
		print(perr)