#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Author:	Vasilis.Vlachoudis@cern.ch
# Date:	20-Jun-2019
#from __future__ import print_function

__author__   = "Vasilis Vlachoudis"
__email__    = "Vasilis.Vlachoudis@cern.ch"
__version__  = "0.0"

import os
import sys
import time
import subprocess

inch = 72.0		# in dpi
mm   = 72.0/25.4	# -//-
cm   = 10*mm

#===============================================================================
# Postscript writing class
#===============================================================================
class Postscript:
	VIEWER  = "gv"
	HEADER  = "%!PS-Adobe-2.0"
	CREATOR = "Postscript.py"
	TITLE   = None
	PAGES = {
			"C5 Envelope" : (461, 648),
			"DL Envelope" : (312, 624),
			"Folio"       : (595, 935),
			"Executive"   : (522, 756),
			"Letter"      : (612, 792),
			"Legal"       : (612, 1008),
			"Ledger"      : (1224, 792),
			"Tabloid"     : (792, 1224),
			"A0"          : (2384, 3370),
			"A1"          : (1684, 2384),
			"A2"          : (1191, 1684),
			"A3"          : (842, 1191),
			"A4"          : (595, 842),
			"A5"          : (420, 595),
			"A6"          : (297, 420),
			"A7"          : (210, 297),
			"A8"          : (148, 210),
			"A9"          : (105, 148),
			"B0"          : (2920, 4127),
			"B1"          : (2064, 2920),
			"B2"          : (1460, 2064),
			"B3"          : (1032, 1460),
			"B4"          : (729, 1032),
			"B5"          : (516, 729),
			"B6"          : (363, 516),
			"B7"          : (258, 363),
			"B8"          : (181, 258),
			"B9"          : (127, 181),
			"B10"         : (91, 127),
		}
	DEFAULT_PAGE = "A4"

	DEFAULT_FONTS = set([	# Postscript level-1
				"Courier",
				"Helvetica",
				"Helvetica-Monospace",
				"Helvetica-Bold",
				"Helvetica-Ital",
				"Helvetica-Bold-Italic",
				"Times",
				"Symbol"

				# Postscript level 2
				"ITC-Avant-Garde-Gothic",
				"ITC-Bookman",
				"New-Century-Schoolbook",
				"Palatino",
				"ITC-Zapf-Chancery",
				"ITC-Zapf-Dingbats",

				# Postscript level 3
				"Albertus",
				"Antique-Olive",
				"Apple-Chancery",
				"Arial",
				"Bodoni",
				"Carta",
				"Chicago",
				"Clarendon",
				"Cooper-Black",
				"Cooper-Black-Italic",
				"Copperplate-Gothic",
				"Coronet",
				"Eurostile",
				"Geneva",
				"Gill-Sans",
				"Goudy",
				"Hoefler-Text",
				"Joanna",
				"Letter-Gothic",
				"ITC-Lubalin-Graph",
				"ITC-Mona-Lisa-Recut",
				"Marigold",
				"Monaco",
				"New-York",
				"Optima",
				"Oxford",
				"Stempel-Garamond",
				"Tekton",
				"Times-New-Roman",
				"Univers",
				"Wingdings",
			])

	# Map of fonts to default ones
	FONT_TABLE = {
		"DejaVu-Sans"      : "Sans",
		"DejaVu-Sans-bold" : "Sans-Bold",
		"DejaVu-Sans-Mono" : "Arial-Monospace",
		"Liberation-Sans"  : "Helvetica-Monospace",
		}

	PROLOG = """
%--------- Procedures ----------------
% Optimize without dict variables later, if at all
/centershow {
   /s exch def
   /y exch def
   /rm exch def
   /lm exch def
   rm lm sub
   s stringwidth pop sub
   2 div
   lm add y moveto
    s show
} def

/xmoveto {
   currentpoint
   exch
   pop
   moveto
} def

/ymoveto {
   currentpoint
   pop
   exch
   moveto
} def

/rightshow {
   /s exch def
   s stringwidth
   neg exch neg exch
   rmoveto
   s show
} def

/rectpath {
    /h exch def
    /w exch def
    /t exch def
    /l exch def
    newpath
    l t moveto
    w 0 rlineto
    0 h neg rlineto
    w neg 0 rlineto
    0 h rlineto
} def

/bgrect {
   /s exch def
   currentpoint
   s false charpath pathbbox
   /ury exch def
   /urx exch def
   /lly exch def
   /llx exch def
   newpath
   llx lly moveto
   urx lly lineto
   urx ury lineto
   llx ury lineto
   llx lly moveto
   fill
} def
%---------- PS Card --------------------
"""

#/textheight {
#    gsave                                  % save graphic context
#    {
#        100 100 moveto                     % move to some point
#        (HÍpg) true charpath pathbbox      % gets text path bounding box (LLx LLy URx URy)
#        exch pop 3 -1 roll pop             % keeps LLy and URy
#        exch sub                           % URy - LLy
#    }
#    stopped                                % did the last block fail?
#    {
#        pop pop                            % get rid of "stopped" junk
#        currentfont /FontMatrix get 3 get  % gets alternative text height
#    }
#    if
#    grestore                               % restore graphic context
#} bind def
#
#/jumpTextLine {
#    textheight 1.25 mul                    % gets textheight and adds 1/4
#    0 exch neg rmoveto                     % move down only in Y axis
#} bind def

	#-----------------------------------------------------------------------
	def __init__(self, filename=None, paper=DEFAULT_PAGE, landscape=False):
		"""Open a postscript file for writing"""
		self.f = None
		self._f_opened = False

		# initialize variables
		self.cursor_x           =  0
		self.cursor_y           =  0
		self.current_font_size  = 12
		self.current_line_size  =  0	# height
		self.margin_top         =  0
		self.margin_bottom      =  0
		self.margin_left        =  0
		self.margin_right       =  0
		self.header             = "Postscript Header"
		self.headerfont         = "Times-Bold"
		self.headersize         = 12
		self.headergray         = 0.8
		self.footer             = "- %d -"
		self.footerfont         = "Times-Roman"
		self.footersize         = 12
		self.footergray         = 0.8

		self._tobuffer = False
		self._buffer   = []	# buffer commands to find line height before drawing
		self._page_marker = None
		self._page_count  = 1

		self.setPaperSize(paper, landscape)
		self.setMargin(cm, cm, cm, cm)
		if filename:
			self.open(filename)

	#-----------------------------------------------------------------------
	def setPaperSize(self, paper, landscape=False):
		self.paper = paper
		self.landscape = landscape
		try:
			self.page_width, self.page_height = Postscript.PAGES[paper]
		except KeyError:
			self.page_width, self.page_height = Postscript.PAGES[Postscript.DEFAULT_PAGE]
		if self.landscape:
			# invert width <-> height
			self.page_width, self.page_height = self.page_height, self.page_width

	#-----------------------------------------------------------------------
	def setMargin(self, left, right, top, bottom):
		self.margin_left   = left
		self.margin_right  = self.page_width - right
		self.margin_top    = self.page_height - top
		self.margin_bottom = bottom

	#-----------------------------------------------------------------------
	def open(self, filename):
		"""Open a postscript file for writing"""
		if isinstance(filename,str):
			self.f = open(filename,"w")
			self._f_opened = True
		else:
			self.f = filename
		self(Postscript.HEADER)
		self.resetCursor()

	#-----------------------------------------------------------------------
	def close(self):
		self.flush()
		self("showpage")
		if self._page_marker is not None:
			# correct pages
			self.f.seek(self._page_marker)
			self.write("%d"%(self._page_count))
		if self._f_opened:
			self.f.close()

	#-----------------------------------------------------------------------
	# Write directly to file
	#-----------------------------------------------------------------------
	def write(self, s):
		"""Write string s to file"""
#		print(s,end='')
		self.f.write(s)

	#-----------------------------------------------------------------------
	# Write or buffer depending the status of buffer
	#-----------------------------------------------------------------------
	def __call__(self, *args):
		"""Write current arguments to a new line"""
		if self._tobuffer:
			self._buffer.append(" ".join(args))
#			print("Buffering...", self._buffer[-1])
		else:
			self.write(" ".join(args))
			self.write("\n")

	#-----------------------------------------------------------------------
	def flush(self):
		self._tobuffer = False
		for line in self._buffer:
			self(line)
		del self._buffer[:]

	#-----------------------------------------------------------------------
	def enableBuffer(self, enable=True):
		self._tobuffer = enable

	#-----------------------------------------------------------------------
	# Override comment in case you want to change the default ones
	#-----------------------------------------------------------------------
	def comment(self):
		self("%%Creator:", Postscript.CREATOR)
		if Postscript.TITLE:
			self("%%Title:", Postscript.TITLE)
		self("%%CreationDate:",time.ctime())
		self("%%DocumentPaperSizes:",self.paper)
		self("%%Orientation:", "Landscape" if self.landscape else "Portrait")
		self("%%Pages:       ")
		try:
			self._page_marker = self.f.tell()-7
		except AttributeError:
			pass
		self("%%EndComments")
#		PrologTarget = "%%BeginProlog\n"

	#-----------------------------------------------------------------------
	# Override prolog in case you want to change the default ones
	#-----------------------------------------------------------------------
	def prolog(self):
		self("/EncapDict 200 dict def EncapDict begin")
		self("/showpage {} def /erasepage {} def /copypage {} def end")
		self("/BeginInclude {0 setgray 0 setlinecap 1 setlinewidth")
		self("0 setlinejoin 10 setmiterlimit [] 0 setdash")
		self("/languagelevel where {")
		self("  pop")
		self("  languagelevel 2 ge {")
		self("    false setoverprint")
		self("    false setstrokeadjust")
		self("  } if")
		self("} if")
		self("newpath")
		self("save EncapDict begin} def")
		self("/EndInclude {restore end} def")
		self(Postscript.PROLOG)
		self("%%EndProlog")
		self.newpageSetup()

	#-----------------------------------------------------------------------
	# Reset cursor position to top left corner
	#-----------------------------------------------------------------------
	def resetCursor(self):
		self.cursor_x = self.margin_left
		self.cursor_y = self.margin_top

	#-----------------------------------------------------------------------
	def define(self, variable, code):
		self("/%s %s def"%(variable, code))

	#-----------------------------------------------------------------------
	# Move commands
	#-----------------------------------------------------------------------
	def newpage(self):
		"""end of current page"""
		self("showpage")
		self._page_count += 1
		self.newpageSetup()

	#-----------------------------------------------------------------------
	def newpageSetup(self):
#		self("BeginInclude")
		self("%%%%Page: %d %d"%(self._page_count, self._page_count))
		if self.landscape:
			self.translate(self.page_height, 0)
			self.rotate(90)
		self.gsave()
		# Draw page header & footer
		if self.header:
			# Header
			self.setFont(self.headerfont, self.headersize)
			self.setGray(self.headergray)
			if self._page_count % 2:
				self.moveto(self.margin_right, self.margin_top)
				self.showRight(self.header)
			else:
				self.moveto(self.margin_left, self.margin_top)
				self.show(self.header)
			self.newpath()
			self.lineWidth(0.1)
			self.moveto(self.margin_left,  self.margin_top-1*mm)
			self.lineto(self.margin_right, self.margin_top-1*mm)
			self.stroke()

		if self.footer:
			self.setFont(self.footerfont, self.footersize)
			self.setGray(self.footergray)

			# Page number
			self.showCenter(self.margin_left, self.margin_right, self.margin_bottom-2*mm,
					self.footer%(self._page_count))
			self.newpath()
			self.lineWidth(0.1)
			self.moveto(self.margin_left,  self.margin_bottom+2*mm)
			self.lineto(self.margin_right, self.margin_bottom+2*mm)
			self.stroke()
		self.grestore()
#		self("EndInclude")

	#-----------------------------------------------------------------------
	def newline(self):
		if self._tobuffer:
			self._tobuffer = False
#			print("   XY:", self.cursor_x, self.cursor_y)
#			print("   TL:", self.margin_left, self.margin_top)
#			print("   LH:", self.current_line_size)
			self.cursor_x  = self.margin_left
			self.cursor_y -= self.current_line_size
			if self.cursor_y < self.margin_bottom:
				self.newpage()
				self.cursor_y = self.margin_top - self.current_line_size
#			print("   XY:", self.cursor_x, self.cursor_y)
			self.current_line_size = 0
			self.moveto()
			self.flush()
			self.enableBuffer()
		else:
			# If not buffered line height is from previous line
			self.cursor_x  = self.margin_left
			self.cursor_y -= self.current_line_size
			if self.cursor_y < self.margin_bottom:
				self.newpage()
				self.cursor_y = self.margin_top
			self.current_line_size = 0
			self.moveto()
#		print("------------------------------------------------")
#		print()

	#-----------------------------------------------------------------------
	# Move current position to location (x,y) if specified else to
	# class cursor position
	#-----------------------------------------------------------------------
	def moveto(self, x=None, y=None):
		if x is None:
			self("%.3f %.3f moveto" % (self.cursor_x, self.cursor_y))
		else:
			self("%.3f %.3f moveto" % (x, y))

	#-----------------------------------------------------------------------
	# Move only x/y at absolute position
	#-----------------------------------------------------------------------
	def xmoveto(self, x):
		self("%.3f xmoveto"%(x))

	#-----------------------------------------------------------------------
	def ymoveto(self, y):
		self("%.3f xmoveto"%(y))

	#-----------------------------------------------------------------------
	def rmoveto(self, x, y):
		self("%.3f %.3f rmoveto" % (x, y))

	#-----------------------------------------------------------------------
	def translate(self, x, y):
		self("%.3f %.3f translate" % (x, y))

	#-----------------------------------------------------------------------
	def rotate(self, a):
		self("%.3f rotate" % (a))

	#-----------------------------------------------------------------------
	def gsave(self):
		self("gsave")

	#-----------------------------------------------------------------------
	def grestore(self):
		self("grestore")

	#-----------------------------------------------------------------------
	# Color commands
	#-----------------------------------------------------------------------
	def setGray(self, percent):
		self(" %.3f setgray" % percent)

	#-----------------------------------------------------------------------
	def setColor(self, r, g, b):
		self("%.3f %.3f %.3f setrgbcolor"%(r,g,b))

	#-----------------------------------------------------------------------
	# Text commands
	#-----------------------------------------------------------------------
	@staticmethod
	def findFont(name):
		"""return closest match of font based on name"""
		name = name.replace(" ","-")
		if name in Postscript.DEFAULT_FONTS:
			return name
		try:
			return Postscript.FONT_TABLE[name]
		except KeyError:
			pass

		# FIXME try to find a closest match
		return name

	#-----------------------------------------------------------------------
	def setFont(self, fontname, fontsize):
		"""Select current font and font size"""
		name = Postscript.findFont(fontname)
#		print("FONT:", fontname, "->", name)
		self("/%s findfont %.3f scalefont setfont" % (name, fontsize))
		self.current_font_size = fontsize
		self.current_line_size = max(self.current_line_size, fontsize)

	#-----------------------------------------------------------------------
	@staticmethod
	def escape(s):
		sout = ""
		for ch in s:
			if ch in " ." or ch.isalnum():
				sout += ch
			else:
				sout += "\\%o"%(ord(ch))
		return sout

	#-----------------------------------------------------------------------
	# Show string with background color (as tuple r,g,b) if specified
	#-----------------------------------------------------------------------
	def show(self, s, bg=None):
		if not s: return

		if bg:	# Draw background
			self.gsave()
			self.setColor(*bg)
			self.bgrect(s)
			self.grestore()

		self.current_line_size = max(self.current_line_size, self.current_font_size)
		self("(%s) show"%(s))

	#-----------------------------------------------------------------------
	def showRight(self, s):
		self("(%s) rightshow" % (s))

	#-----------------------------------------------------------------------
	def showCenter(self, left, right, y, s):
		self("%.3f %.3f %.3f (%s) centershow" % (left, right, y, s))

	#-----------------------------------------------------------------------
	# Drawing commands
	#-----------------------------------------------------------------------
	def newpath(self):
		self("newpath")

	#-----------------------------------------------------------------------
	def stroke(self):
		self("stroke")

	#-----------------------------------------------------------------------
	def fill(self):
		self("fill")

	#-----------------------------------------------------------------------
	def lineWidth(self, lw):
		self("%.3f setlinewidth" % lw)

	#-----------------------------------------------------------------------
	def lineto(self, x, y):
		self("%.3f %.3f lineto" % (x, y))

	#-----------------------------------------------------------------------
	def rlineto(self, x, y):
		self("%.3f %.3f rlineto" % (x, y))

	#-----------------------------------------------------------------------
	def translate(self, x, y):
		self("%.3f %.3f translate" % (x, y))

	#-----------------------------------------------------------------------
	def bgrect(self, s):
		self("(%s) bgrect"%(s))

	#-----------------------------------------------------------------------
	def rect(self, left, top, width, height):
		self("%.3f %.3f %.3f %.3f rectpath" % (left, top, width, height))
		self.stroke()

	#-----------------------------------------------------------------------
	def view(self):
		return subprocess.call([Postscript.VIEWER, self.f.name])

#-------------------------------------------------------------------------------
if __name__ == "__main__":
	ps = Postscript("postscript.ps", "A4")
	ps.comment()
	ps.prolog()
	ps.setFont("Times-Roman", 12.0)
	ps.show("Hello world, abcdefghijklmnopqrstuvwxyz")
	ps.newline()
	ps.show("Hello world, abcdefghijklmnopqrstuvwxyz")
	ps.newline()
	ps.setFont("Times-Bold", 16.0)
	ps.show(" Times-Bold")
#	ps.setFont("Symbol",6)
	ps.newline()
	ps.show(Postscript.escape("Another line..(&*^(*).."))
	ps.show(Postscript.escape("Background text"), (0.7, 0.6, 0.5))
#	ps.setColor(0,0,0)
#	ps.show(Postscript.escape("Background text"))
#	ps.rect(2*cm, 15*cm, 4*cm, 6*cm)

#	ps.lineWidth(1)
#	ps.rlineto(5*cm,0)
#	ps.rlineto(0,8)
#	ps.rlineto(-5*cm,0)
#	ps.stroke()
#	ps.newline()
#	ps.show("Hello world2")
	ps.close()
	ps.view()
