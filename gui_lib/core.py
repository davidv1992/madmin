import widget
import curses

_stop = False
_WindowWidget = None
_cursorPos = (0,0)
_cursorEnabled = False

def setCursor(x,y):
	global _cursorEnabled, _cursorPos
	_cursorEnabled = True
	_cursorPos = (x,y)
	curses.curs_set(1)

def unsetCursor():
	global _cursorEnabled, _cursorPos
	_cursorEnabled = False
	_cursorPos = (0,0)
	curses.curs_set(0)
	
def stepFocus():
	if not _WindowWidget.changeFocus():
		_WindowWidget.onFocus()

def end():
	global _stop
	_stop = True

def _redraw(stdscr):
	global _WindowWidget
	global _cursorPos, _cursorEnabled
	(height, width) = stdscr.getmaxyx()
	_WindowWidget.draw(stdscr, 0, 0, 0, 0, width, height-1)
	_WindowWidget.draw(stdscr, 0, 0, 0, height-1, width-1, height)
	if _cursorEnabled:
		stdscr.move(_cursorPos[1], _cursorPos[0])
	stdscr.refresh()
	
def _mainloop(stdscr):
	global _stop
	global _WindowWidget
	_stop = False
	(height, width) = stdscr.getmaxyx()
	curses.cbreak()
	curses.curs_set(0)
	_WindowWidget.resize(width, height)
	_WindowWidget.onFocus()
	while not _stop:
		stdscr.clear()
		_redraw(stdscr)
		key = stdscr.getch()
		if key == curses.KEY_RESIZE:
			(height, width) = stdscr.getmaxyx()
			_WindowWidget.resize(width, height)
		elif not _WindowWidget.keyEvent(key):
			if key == ord('\t'):
				stepFocus()
			if key == curses.KEY_END:
				end()
					
	

def mainloop(WindowWidget):
	global _WindowWidget
	_WindowWidget = WindowWidget
	curses.wrapper(_mainloop)
