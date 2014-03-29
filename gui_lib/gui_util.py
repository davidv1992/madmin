def intersect(a, b):
	(aminx, aminy, amaxx, amaxy) = a
	(bminx, bminy, bmaxx, bmaxy) = b
	
	# no overlap case
	if aminx >= bmaxx or bminx >= amaxx or aminy >= bmaxy or bminy >= amaxy:
		return []
	
	# have overlap case
	return ((max(aminx, bminx), max(aminy, bminy),
	        min(amaxx, bmaxx), min(amaxy, bmaxy)),)


# Process text to produce a representation suitable for
#  output to screen
# Whitespace characters will never appear at the start of a line
#  except on the first
# Lines will have only whitespace in the characters that they are
#  longer than width
# Lines will be broken only on whitespace, and forced on a \n
# Tabs are not supported


# TOKEN FORMAT: [(tok_type, value)]

_TOK_WORD = 0
_TOK_NEWLINE = 1
_TOK_WHITESPACE = 2
_TOK_NONE = 3
def _text_tokenize(text):
	curTokenType = _TOK_NONE
	curTokenValue = None
	tokens = []
	for index in range(0,len(text)):
		if curTokenType == _TOK_NONE:
			if text[index] == '\n':
				tokens.append((_TOK_NEWLINE,None))
			elif text[index].isspace():
				curTokenType = _TOK_WHITESPACE
				curTokenValue = 1
			else:
				curTokenType = _TOK_WORD
				curTokenValue = text[index]
		elif curTokenType == _TOK_WHITESPACE:
			if text[index] == '\n':
				tokens.append((curTokenType, curTokenValue))
				tokens.append((_TOK_NEWLINE, None))
				curTokenType = _TOK_NONE
			elif text[index].isspace():
				curTokenValue = curTokenValue + 1
			else:
				tokens.append((curTokenType, curTokenValue))
				curTokenType = _TOK_WORD
				curTokenValue = text[index]
		elif curTokenType == _TOK_WORD:
			if text[index] == '\n':
				tokens.append((curTokenType, curTokenValue))
				tokens.append((_TOK_NEWLINE, None))
				curTokenType = _TOK_NONE
			elif text[index].isspace():
				tokens.append((curTokenType, curTokenValue))
				curTokenType = _TOK_WHITESPACE
				curTokenValue = 1
			else:
				curTokenValue = curTokenValue + text[index]
	
	if curTokenType != _TOK_NONE:
		tokens.append((curTokenType, curTokenValue))
	
	return tokens


_TAS_STARTLINE = 0
_TAS_INLINE = 1
_TAS_DOENDLINE = 2
def text_arrange(text, width, height):
	tokens = _text_tokenize(text)
	lines = []
	index = 0
	state = _TAS_STARTLINE
	curline = ""
	while index < len(tokens):
		if state == _TAS_STARTLINE:
			if tokens[index][0] == _TOK_WORD:
				if len(tokens[index][1]) > width:
					lines.append(tokens[index][1][0:width])
				else:
					curline = tokens[index][1]
					state = _TAS_INLINE
				index = index + 1
			elif tokens[index][0] == _TOK_NEWLINE:
				lines.append("")
				index = index + 1
			elif tokens[index][0] == _TOK_WHITESPACE:
				curline = ""
				for i in range(0, min(width, tokens[index][1])):
					curline = curline + " "
				state =  _TAS_INLINE
				index = index + 1
		elif state == _TAS_INLINE:
			if tokens[index][0] == _TOK_WHITESPACE:
				for i in range(0, min(width-len(curline), tokens[index][1])):
					curline = curline + " "
				index = index + 1
			if tokens[index][0] == _TOK_NEWLINE:
				state = _TAS_DOENDLINE
				index = index + 1
			if tokens[index][0] == _TOK_WORD:
				if len(tokens[index][1]) + len(curline) > width:
					state = _TAS_DOENDLINE
				else:
					curline = curline + tokens[index][1]
					index = index + 1
		elif state == _TAS_DOENDLINE:
			lines.append(curline)
			curline = ""
			state = _TAS_STARTLINE
	
	if state == _TAS_DOENDLINE or state == _TAS_INLINE:
		lines.append(curline)
	
	if height != -1 and len(lines) > height:
		lines = lines[:height]
		# remove trailing whitespace from last line
		while len(lines[-1]) > 0 and lines[-1][-1].isspace():
			lines[-1] = lines[-1][:-1]
		# if neccessary, remove letters from last word to make space for
		#  3 dots
		while len(lines[-1]) > width-3:
			lines[-1] = lines[-1][:-1]
		lines[-1] += '...'
	
	return lines
