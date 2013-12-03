from panda3d.core import *
loadPrcFileData("", "audio-library-name p3openal_audio")
import direct.directbase.DirectStart
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from pandac.PandaModules import Texture
from panda3d.core import TextNode
import sys,sonicandtails
  
  # Add some text
b=OnscreenImage(parent=render2dp, image="models/Sonic-and-Tails.jpg")
base.cam2dp.node().getDisplayRegion(0).setSort(-20)
bk_text = "This is my Demo"
textObject = OnscreenText(text = bk_text, pos = (0.95,-0.95), 
scale = 0.07,fg=(1,0.5,0.5,1),align=TextNode.ACenter,mayChange=1)

  # Callback function to set  text
def setText1():
	w=sonicandtails.World()
	b.hide()
	b1.hide()
	b2.hide()
	b3.hide()
	b4.hide()
	textObject.hide()

def setText2():
		bk_text = "Help"
		textObject.setText(bk_text)

def setText3():
		bk_text = "About"
		textObject.setText(bk_text)

def setText4():
		sys.exit()
		
  # Add button
b1 = DirectButton(text = ("Start"), scale=.1,pos=(0,0,0.8), command=setText1)
b2 = DirectButton(text = ("Help"), scale=.1, pos=(0,0,0.6),command=setText2)			    
b3 = DirectButton(text = ("About"), scale=.1,pos=(0,0,0.4), command=setText3)
b4 = DirectButton(text = ("Exit"), scale=.1, pos=(0,0,0.2),command=setText4)
# Run the tutorial
run()
