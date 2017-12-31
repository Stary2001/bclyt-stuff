#!/usr/bin/env python3
import sys
from sys import argv
from parse import LayoutFile
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QFrame
from PyQt5.QtGui import QPalette, QColor

def create_frame(parent_pane, pane):
	frame = QFrame(parent_pane.qt_frame)

	if pane.visibility == 3:
		pane.width = parent_pane.width
		pane.height = parent_pane.height
	elif pane.visibility == 1:
		pass
	else:
	#	raise Exception("unk visibility")
		pass

	x = pane.origin % 3
	y = pane.origin // 3

	if x == 0:
		pane.x = 0
	elif x == 1:
		pane.x = (parent_pane.width - pane.width) / 2
	elif x == 2:
		pane.x = parent_pane.width - pane.width

	if y == 0:
		pane.y = 0
	elif y == 1:
		pane.y = (parent_pane.height - pane.height) / 2
	elif y == 2:
		pane.y = parent_pane.height - pane.height

	frame.setGeometry(pane.x, pane.y, pane.width, pane.height)
	frame.setFrameShape(QFrame.Box)
	frame.show()
	pane.qt_frame = frame

	for child in pane.children:
		create_frame(pane, child)

	return frame

with open(argv[1], 'rb') as f:
	layout = LayoutFile.from_file(f)
	
	app = QApplication(argv)
	w = QWidget()
	
	w.setGeometry(100,100,420,260)
	w.setWindowTitle("PyQt")
	w.show()
	
	frame = QFrame(w)
	frame.setGeometry(10, 10, layout.root_pane.width, layout.root_pane.height)
	frame.setFrameShape(QFrame.Box)
	palette = frame.palette()
	palette.setColor(QPalette.Foreground, QColor(255,0,255,255))
	frame.setPalette(palette)
	frame.show()
	layout.root_pane.qt_frame = frame

	for pane in layout.root_pane.children:
		create_frame(layout.root_pane, pane)

	sys.exit(app.exec_())