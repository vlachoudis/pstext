#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Author:	Vasilis.Vlachoudis@cern.ch
# Date:	21-Jun-2019
#from __future__ import print_function

__author__   = "Vasilis Vlachoudis"
__email__    = "Vasilis.Vlachoudis@cern.ch"
__version__  = "0.0"

import os
import sys
from postscript import *

import tkinter as tk
import tkinter.font as tkFont

#===============================================================================
# Text with postscript exporting capability
#===============================================================================
class PSTextExporter:
	# Text() tags to ignore
	IGNORE = set([
			"autoseparators",
#			"background",
			"bd",
			"bg",
			"blockcursor",
			"borderwidth",
			"cursor",
			"exportselection",
			"fg",
#			"font",
#			"foreground",
			"height",
			"highlightbackground",
			"highlightcolor",
			"highlightthickness",
			"inactiveselectbackground",
			"insertbackground",
			"insertborderwidth",
			"insertofftime",
			"insertontime",
			"insertunfocussed",
			"insertwidth",
			"maxundo",
			"padx",
			"pady",
			"relief",
			"selectbackground",
			"selectborderwidth",
			"selectforeground",
#			"setgrid",
			"spacing1",
			"spacing2",
			"spacing3",
			"state",
#			"tabs",
#			"tabstyle",
			"takefocus",
			"undo",
			"width",
			"wrap",
			"xscrollcommand",
			"yscrollcommand",
		])

	#-----------------------------------------------------------------------
	def __init__(self, text, filename, paper="A4", landscape=False):
		self.init()
		self.text = text
		self.ps = Postscript(filename, paper, landscape)
		self.ps.comment()
		self.ps.prolog()
		self.export()
		self.ps.close()
		process = self.ps.view()

	#-----------------------------------------------------------------------
	def setFont(self, fontname):
		try:
			font = tkFont.Font(name=fontname, exists=True)
		except tk.TclError:
			font = tkFont.Font(name=fontname)
		name = font.actual("family")
		if font.actual("weight") != "normal":
			name += "-%s"%(font.actual("weight"))
		if font.actual("slant") != "roman":
			name += "-italic"
		self.ps.setFont(name, font.actual("size"))

#		print("font=",font.actual("family"))
#		print("font-size=",font.actual("size"))
#		print("font-weight=",font.actual("weight"))
#		print("font-slant=",font.actual("slant"))
#		print("font=",font.actual("underline"))
#		print("font=",font.actual("overstrike"))
#		print("font=",font.metrics())
#		print("font=",font.configure())

	#-----------------------------------------------------------------------
	def init(self):
		self.bg    = None
		self.elide = False

	#-----------------------------------------------------------------------
	def updateTag(self, name, value):
		if name == "font":
			print("Set font",value)
			self.setFont(value)
		elif name == "foreground":
			print("Color", value)
			r,g,b = self.text.winfo_rgb(value)
			self.ps.setColor(r/65536,g/65536,b/65536)
		elif name == "background":
			self.bg = self.text.winfo_rgb(value)

		elif name == "elide":
			self.elide = bool(value)
			print("ELlDE = value=",value, self.elide)

		else:
			print("tag",name,value)

	#-----------------------------------------------------------------------
	def export(self):
		self.ps.enableBuffer()

		dump = self.text.dump("1.0",tk.END)

		#---------------------------------------------------------------
		def tagon(config):
			nonlocal tagstack
			nonlocal combinedtag

			# update tags that are changed
			for n,*a in config.values():
				if a[-1]=='': continue
				if n in PSTextExporter.IGNORE: continue
#				print("TAG",n,a)
				v = a[-1]
				tagstack[-1][1][n] = v
				combinedtag[n] = v
				self.updateTag(n,v)
		#---------------------------------------------------------------

		combinedtag = {}
		tagstack  = [("",{})]

		self.init()			# Initialize variables
		tagon(self.text.config())	# default configuration
		self.bg = None			# ignore global background

		for tag,value,pos in dump:
			print("\nDUMP:",tag,repr(value),pos)

			if tag=="tagon":
				tagstack.append((value,{}))
				tagon(self.text.tag_config(value))

			elif tag=="tagoff":
				# remove the last match of tag from stack and
				# recreate the combined tag
				for i in range(len(tagstack)-1,-1,-1):
					if tagstack[i][0] == value:
						del tagstack[i]
						break

				self.init()		# Initialize variables

				# re-create the combined tag
				combinedtag = {}
				for nd in tagstack:
					for n,v in nd[1].items():
						combinedtag[n] = v

				# update all tags from beginning
				for n,v in combinedtag.items():
					self.updateTag(n,v)

			elif tag=="text" and not self.elide:
				if "\n" in value:
					for i,line in enumerate(value.splitlines()):
						if i: self.ps.newline()
						self.ps.show(Postscript.escape(line), self.bg)
					if value[-1]=="\n": self.ps.newline()
				else:
					self.ps.show(Postscript.escape(value), self.bg)

			elif tag=="image":
				image = tk.PhotoImage(name=value)
				height = image.height()
				width  = image.width()
				data = image.cget("data")
				print(">>>>>>>>>>>>>>>>>",value, image, height, width, len(data))

#			print("STACK=",[t[0] for t in tagstack])

#-------------------------------------------------------------------------------
def export2Ps(event=None):
	global text
	PSTextExporter(text, "pstext.ps", "A4")

INFO_ICON = """
		R0lGODlhEAAQAOfEAAAAADVZkSZeryRfsCZfsCtgriZisydjtCdmtyZtvCljsyhltShntyxptSho
		uClpuiprvCtsuChvvSpsvCptvipuvSpuvi1quS1sui5uvC5vvSdyvCZyvitwvy5wvjVqpztqpjxs
		tDByvCtwwStxwSxywSxywi5zwy50wjB1xDF1xDZ6xjd6xjh6xzl8yD18yD19yT59yFJoj01zqEx0
		skh5vlFwoVNxoFFxpFRyoFRyoll4qVt5qVN7t1Z/tFl+sGJ7pUB6wER7wkZ6wEZ7wEh7wEh9wk2B
		tEmAulCAtlGGulGGu1iEuV2Jt2qErmCDsGCDuW2IsXGHq3GKsnSQvniQtnyUukGAyUeEzEmEzE2G
		zk6IzlGEwVCExVCJx1CJz16LxFeN0liO0l+Qz2CMxWKMxWKNx2ONx2SKxGSNx2KRy2uY1G6Y026b
		2HSSwXeVw3OXzHueznydzXyezn6czH6fzn+ezn+fznCa1HGa1HKb1HCd03Ce2nCf3H+gz3Cg1nyn
		2nym3I2duI+hv5imu4OYwIKbw4Wdwoidw4Ch0Ieu3ous3Y2s3pCkypyqwJe23Ziw1Jiw15uy152y
		15qy2Juz2Jq23Jyz2J602JCw5JCx5JS05pS056KvyKSyyKu1xrbF37PF4rXF4bfG4rjH4brI4r/O
		5sDG1t/f38TV6szX6MzZ7dTd7NTe7Njg7tbg8tvi8Nrk8uTi4OTn7OTo7ejp7eDn8uDo9Orv9urw
		9urw+O7y+O7y+fH0+ff5+/b5/Pf5/Pf6/Pn7/Pr7/f//////////////////////////////////
		////////////////////////////////////////////////////////////////////////////
		////////////////////////////////////////////////////////////////////////////
		/////////////////////////////////////////////////////yH5BAEAAP8ALAAAAAAQABAA
		AAj6AP8JFNipUKNGiDwNXPgvh6FXrCKyWkXlBkMcoVyxgtXLFqtWriLZGKjjEqlRonYRGwZq1KhS
		dID8+wRlkiRJlEz5UgWp0k1MND4lgWPnjp85cRLVSZRIDpoQBQL4SFPmjBlLt3TxIlNEwQABBHwk
		qTGEiBEhj4gBa+CAwYIDBpJguIAhgwYPe4j9ikABwgMHCJRUkFChQwkUf9SKODHCwoQETapwMKGi
		xQtAxIIFgcEiBYkNVf4hcXElixZFxIR12YIlxoolAq14+SImUKxcuFKNCcOFiYyBh9TwaYNHTx42
		a/qA6cFwkBtGmjhtyrTojRSGAwseTMgwIAA7
		"""

#-------------------------------------------------------------------------------
if __name__ == "__main__":
	root = tk.Tk()
	text = tk.Text(root, wrap=tk.WORD)

	image = tk.PhotoImage(data=INFO_ICON)
	print(image.width(), image.height(), image.cget("data"))
	for i in range(1,50):
		text.insert(tk.END, "%d. The quick "%(i))
		if i==4: text.image_create(tk.END, image=image)
		text.insert(tk.END, "brown", "brown" if i%2 else "")
		text.insert(tk.END, " fox jumps over the lazy dogs tail\n")
		text.tag_add("line%d"%(i), "%d.0"%(i), "%d.end"%(i))

	text.insert(tk.END,"\n")
	text.insert(tk.END,"LOREM IPSUM", "elide")
	text.insert(tk.END,"LOREM IPSUM", "lorem")
	text.insert(tk.END,"""
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Suspendisse potenti nullam ac tortor vitae purus faucibus ornare suspendisse. Sapien et ligula ullamcorper malesuada. Imperdiet nulla malesuada pellentesque elit. Mi ipsum faucibus vitae aliquet nec. Ultricies lacus sed turpis tincidunt id aliquet. Porttitor rhoncus dolor purus non enim praesent elementum facilisis leo. Nulla facilisi morbi tempus iaculis. Amet facilisis magna etiam tempor orci eu lobortis. Egestas fringilla phasellus faucibus scelerisque eleifend donec. Urna et pharetra pharetra massa massa ultricies mi quis. Suspendisse faucibus interdum posuere lorem ipsum dolor. Congue nisi vitae suscipit tellus. Semper eget duis at tellus.

Id ornare arcu odio ut sem nulla pharetra diam sit. Ut pharetra sit amet aliquam id diam maecenas ultricies mi. Et netus et malesuada fames ac turpis egestas sed. Tortor vitae purus faucibus ornare suspendisse sed. Tincidunt augue interdum velit euismod in pellentesque massa placerat duis. A iaculis at erat pellentesque adipiscing commodo elit at imperdiet. Ut porttitor leo a diam sollicitudin. Nisi quis eleifend quam adipiscing vitae. Vitae suscipit tellus mauris a diam maecenas sed enim. A scelerisque purus semper eget duis at tellus at urna. Erat velit scelerisque in dictum non consectetur a erat nam.

Vitae justo eget magna fermentum iaculis eu. Lectus vestibulum mattis ullamcorper velit sed ullamcorper. Quam pellentesque nec nam aliquam. Feugiat sed lectus vestibulum mattis ullamcorper velit sed ullamcorper. Id eu nisl nunc mi ipsum faucibus vitae. Turpis massa tincidunt dui ut ornare lectus sit amet. Porta nibh venenatis cras sed. Eget gravida cum sociis natoque penatibus. Ac feugiat sed lectus vestibulum mattis ullamcorper velit. Fringilla ut morbi tincidunt augue interdum velit. Ultricies integer quis auctor elit sed vulputate. Egestas egestas fringilla phasellus faucibus scelerisque eleifend donec. Pretium fusce id velit ut tortor pretium viverra. At auctor urna nunc id. Quam id leo in vitae turpis massa sed. Eget est lorem ipsum dolor sit amet consectetur.

Eu mi bibendum neque egestas congue quisque. Facilisis magna etiam tempor orci eu lobortis. At in tellus integer feugiat scelerisque varius morbi enim. Sed enim ut sem viverra aliquet eget sit amet tellus. Aliquet nec ullamcorper sit amet risus nullam eget felis eget. Id porta nibh venenatis cras sed felis eget velit aliquet. Convallis convallis tellus id interdum velit laoreet id donec. Adipiscing elit ut aliquam purus sit amet luctus venenatis. Pellentesque diam volutpat commodo sed egestas egestas fringilla phasellus. Luctus accumsan tortor posuere ac ut consequat semper viverra. Risus at ultrices mi tempus imperdiet nulla malesuada.

Pharetra pharetra massa massa ultricies mi quis hendrerit dolor magna. Nam at lectus urna duis convallis. Mauris cursus mattis molestie a iaculis at. Donec adipiscing tristique risus nec feugiat in fermentum. Sit amet porttitor eget dolor morbi non arcu risus quis. Vitae elementum curabitur vitae nunc sed velit dignissim sodales. Adipiscing at in tellus integer feugiat scelerisque. Sed viverra tellus in hac habitasse platea dictumst. Feugiat scelerisque varius morbi enim nunc faucibus a. Pharetra vel turpis nunc eget lorem dolor sed viverra. Arcu odio ut sem nulla pharetra. Euismod in pellentesque massa placerat duis. Aliquet enim tortor at auctor urna nunc. Malesuada bibendum arcu vitae elementum curabitur. Vulputate mi sit amet mauris. Nisi scelerisque eu ultrices vitae auctor eu augue ut. Enim sed faucibus turpis in eu mi. Diam maecenas sed enim ut sem.
""")

	text.tag_config("brown", font="Helvetica 30", foreground="Brown")
	text.tag_config("line2", background="Gray", font="Times 20 bold")
	text.tag_config("line5", background="Yellow", font="Times,25,italic")
	text.tag_config("lorem", font="Helvetica 40", foreground="Red")
	text.tag_config("elide", elide=True)

	text.pack(fill=tk.BOTH, expand=tk.YES)
	text.bind("<Key-v>", export2Ps)
	text.bind("<Key-q>", lambda e: text.quit())
	text.after(1000, export2Ps)
	text.focus_set()
	text.config(state=tk.DISABLED)
	root.deiconify()
	root.wait_visibility()
	root.mainloop()
