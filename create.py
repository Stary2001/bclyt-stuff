from parse import *
from sys import argv

"""
f = LayoutFile()
f.materials = {}
f.textures = []
f.root_pane = Pane(name="RootPane", alpha=255, visibility=1, x=0, y=0, z=0, origin=4, x_rotate=0, y_rotate=0, z_rotate=0, x_scale=1, y_scale=1, width=400, height=240)
container = Pane(name="Root2", alpha=255, visibility=3, x=0, y=0, z=0, origin=4, x_rotate=0, y_rotate=0, z_rotate=0, x_scale=1, y_scale=1, width=400, height=240)
f.root_pane.children.append(container)
img = ImagePane(name="img", visibility=1, origin=4, alpha=255, alpha2=255, x=0, y=0, z=0, x_flip=0, y_flip=0, angle=0, x_mag=1, y_mag=1, width=128, height=128)
container.children.append(img)

print(repr(f.root_pane))

f.save(open('test.bclyt', 'wb'))"""

with open(argv[1], 'rb') as f:
	layout = LayoutFile.from_file(f)
	layout.save(open('test.bclyt', 'wb'))