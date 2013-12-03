import direct.directbase.DirectStart
from panda3d.core import CollisionTraverser,CollisionNode
from panda3d.core import CollisionHandlerQueue,CollisionRay
from panda3d.core import Filename,AmbientLight,DirectionalLight,PointLight
from panda3d.core import PandaNode,NodePath,Camera,TextNode
from panda3d.core import Vec3,Vec4,BitMask32,VBase4
from direct.gui.OnscreenText import OnscreenText
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *
from direct.interval.LerpInterval import LerpPosInterval
from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from panda3d.core import Point3
import random, sys, os, math
from math import *
from direct.gui.DirectGui import *

SPEED = 0.5
i=0
j=0
# Function to put instructions on the screen.
def addInstructions(pos, msg):
	return OnscreenText(text=msg, style=1, fg=(1,1,1,1),
						pos=(-1.3, pos), align=TextNode.ALeft, scale = .05)

# Function to put title on the screen.
def addTitle(text):
	return OnscreenText(text=text, style=1, fg=(1,1,1,1),
						pos=(1.3,-0.95), align=TextNode.ARight, scale = .07)
def light(directionalLight):
		#print "chaging light",directionalLight,i,j
		rate=0.03
		global i,j
		if(i<1000):
			j=0
			i=i+1
			directionalLight.setDirection(Vec3(0,directionalLight.getDirection().y-rate, -5))
		else:
			if(j>1000):
				i=0
			j=j+1
			directionalLight.setDirection(Vec3(0,directionalLight.getDirection().y+rate, -5))


class World(DirectObject):
	
	def cameraControl(self, task):
		if(self.keyMap["firstPerson"]==0 and self.keyMap["ThirdPerson"]!=0):
			return task.cont
		dt = globalClock.getDt()
		if(dt > .20):
		   return task.cont
		    
		if(base.mouseWatcherNode.hasMouse() == 1):
		   mpos = base.mouseWatcherNode.getMouse()
		   base.camera.setP(mpos.getY() * 30)
		   base.camera.setH(mpos.getX() * -50)
		   if (mpos.getX() < 0.1 and mpos.getX() > -0.1 ):
		      self.sonic.setH(self.sonic.getH())
		   else:
		      self.sonic.setH(self.sonic.getH() + mpos.getX() * -1)
		   
		if(self.keyMap["w"] == 1):
		   self.sonic.setY(self.sonic, 15 * dt)
		   print("camera moving forward")
		   return task.cont
		elif(self.keyMap["s"] == 1):
		   self.sonic.setY(self.sonic, -15 * dt)
		   print("camera moving backwards")
		   return task.cont
		elif(self.keyMap["a"] == 1):
		   self.sonic.setX(self.sonic, -10 * dt)
		   print("camera moving left")
		   return task.cont
		elif(self.keyMap["d"] == 1):
		   self.sonic.setX(self.sonic, 10 * dt)
		   print("camera moving right")
		   return task.cont
		else:
		   return task.cont

	def __init__(self):
		self.keyMap = {"left":0, "right":0, "forward":0,"backward":0, "cam-left":0, "cam-right":0,"res":0,
		"w" : 0, "s" : 0, "a" : 0, "d" : 0,"firstPerson":0,"ThirdPerson":1,"l":0}
		base.win.setClearColor(Vec4(0,0,0,1))
		wp = WindowProperties()
		wp.setFullscreen(1)
		wp.setSize(1024,768)
		base.openMainWindow()
		base.win.requestProperties(wp)
		base.graphicsEngine.openWindows()
		#Post the instructions
		
		#Intro Starts
		tex = MovieTexture("name")
		assert tex.read("models/play/entrance.avi"), "Failed to load video!"
		cm = CardMaker("My Fullscreen Card");
		cm.setFrameFullscreenQuad()
		cm.setUvRange(tex)
		card = NodePath(cm.generate())
		card.reparentTo(render2d)
		card.setTexture(tex)
		card.setTexScale(TextureStage.getDefault(), tex.getTexScale())
		sound=loader.loadSfx("models/play/entrance.avi")
		tex.synchronizeTo(sound)
		tex.setLoop(False)
		sound.play()
		def myTask(task):
			if (int(tex.getTime()) >=14):
				print "Stoping"
				card.remove()
				return task.done
			return task.cont
		taskMgr.add(myTask, "Task")
		
		mytimer = DirectLabel()
		mytimer.reparentTo(render)
		#mytimer.setY(0)
		textObject = OnscreenText(text = "", pos = (0.95,-0.95), 
scale = 0.07,fg=(1,0.5,0.5,1),align=TextNode.ACenter,mayChange=1)

		def dCharstr(theString):
			if len(theString) != 2:
				theString = '0' + theString
				return theString
	    
		


		def timerTask(task):
			secondsTime = int(task.time)
			minutesTime = int(secondsTime/60)
			hoursTime = int(minutesTime/60)
			mytimer['text'] = "%02d:%02d:%02d" % (hoursTime, minutesTime%60, secondsTime%60)
			#print mytimer['text']
			textObject.setText(mytimer['text'])
			return task.cont

		taskMgr.add(timerTask, 'timerTask')
		mytimer.reparentTo(render)
		
		self.inst1 = addInstructions(0.95, "[ESC]: Quit")
		self.inst2 = addInstructions(0.90, "[L]: Map View")
		self.inst3 = addInstructions(0.85, "Movement: Arrow Keys")
		self.inst2 = addInstructions(0.80, "[R]: Reset Position")

		self.road = loader.loadModel("models/floor")
		
		emin,emax =self.road.getTightBounds()
		env = []
		esize=20
		for en in range(0,esize):
			for j in range(0,esize):
				#if (j%2==0):
				#print j+(en*9),"Here"
				env.append(self.road)
				env[j+(en*9)].copyTo(render)
				env[j+(en*9)].setPos(emin.x*(en-esize/2),emax.y*(j-esize/2),0)
		
		self.BuildingRow = [loader.loadModel("models/BuildingCluster1col"),
					loader.loadModel("models/BuildingCluster2col"),
					loader.loadModel("models/BuildingCluster3col"),
					loader.loadModel("models/BuildingCluster4col")]

		e0,e1=env[0].getTightBounds()
		mapsize=e0.x*len(env)
		self.vehicle_carsx=loader.loadModel("models/vehicles/carnsxcol")
		self.sign=Actor("models/squarrow-model",{
                        "play":"models/squarrow-anim"})
		self.sign1=Actor("models/squarrow-model",{
                        "play":"models/squarrow-anim"})
		self.vehicle_ford=loader.loadModel("models/vehicles/fordcol")
		self.vehicle_girlcar=loader.loadModel("models/vehicles/girlcarcol")
		self.vehicle_policecar=loader.loadModel("models/vehicles/policecarcol")
		self.vehicle_fireengine=loader.loadModel("models/vehicles/fireenginecol")
		self.vehicle_carsx.reparentTo(render)
		self.sign.reparentTo(render)
		self.sign1.reparentTo(render)
		self.vehicle_carsx.setPos(-35,295,0)
		self.vehicle_carsx.setScale(5)
		self.vehicle_ford.reparentTo(render)
		self.vehicle_ford.setPos(52,270,0)
		self.vehicle_ford.setScale(3)
		self.vehicle_girlcar.reparentTo(render)
		self.vehicle_girlcar.setPos(200,20,0)
		self.vehicle_girlcar.setScale(5)
		self.vehicle_girlcar.setH(-90)
		self.vehicle_policecar.reparentTo(render)
		self.vehicle_policecar.setPos(-33,295,0)
		self.vehicle_policecar.setScale(3)
		self.vehicle_fireengine.reparentTo(render)
		self.vehicle_fireengine.setPos(-60,-294,0)
		self.vehicle_fireengine.setH(90)
		self.vehicle_fireengine.setScale(3)
		self.sign1.setPos(-129,-44,150)
		self.sign.setPos(89,172.6,150)
                self.sign1.setHpr(-90,0,60)
                self.sign.setHpr(-90,0,60)
		self.sign1.loop("play")
		self.sign.loop("play")
		self.vehicle_carsxinterval=LerpPosInterval(self.vehicle_carsx, 10,Vec3(-33,-325,0) ,Vec3(52,295,0))
		self.vehicle_carsxinterval.loop()
		self.vehicle_fordinterval=LerpPosInterval(self.vehicle_ford, 10,Vec3(52,-325,0) ,Vec3(52,270,0))
		self.vehicle_fordinterval.loop()
		self.vehicle_policecarinterval=LerpPosInterval(self.vehicle_policecar, 10,Vec3(-33,295,0) ,Vec3(-33,-325,0))
		self.vehicle_policecarinterval.loop()
		self.vehicle_fireengineinterval=LerpPosInterval(self.vehicle_fireengine, 10,Vec3(52,270,0) ,Vec3(52,-350,0))
		self.vehicle_girlcar=LerpPosInterval(self.vehicle_girlcar,10,Vec3(-54,33,6),Vec3(-258,33,6))
		self.vehicle_girlcar.loop()
		
		for j in self.BuildingRow:
			j.setPos(e0.x,e1.y,0)
		
		building=[]
		for j in range(0,8):
			building.append(self.BuildingRow)
			offset=0
			c=env[0].getX()
			x=e0.x
			y=e1.y+(emin.x*4*j);
			for i in building[j]:
				x=x-emin.x
				i.copyTo(render)
				min,max =i.getTightBounds()
				width=max-min
				i.setPos(x,y,0)
				x=x-emin.x
				i.copyTo(render)
				i.setPos(-x+50,y,0)
		
							
		# Create the main character, Ralph
		sonicStartPos = (0,0,-2)
		self.sonic = Actor("models/people/sonic/sonic",{
			"board":"models/people/sonic/sonic-board",
			"fallingwboard":"models/people/sonic/sonic-fallingwboard",
			"fallingwoboard":"models/people/sonic/sonic-fallingwoboard",
			"run":"models/people/sonic/sonic-run",
			"win":"models/people/sonic/sonic-win",
			})
		self.sonic.reparentTo(render)
		self.sonic.setScale(.5)
		self.sonic.setPos(sonicStartPos)
		
		# Create a floater object.  We use the "floater" as a temporary
		# variable in a variety of calculations.
		
		self.floater = NodePath(PandaNode("floater"))
		self.floater.reparentTo(render)

		# Accept the control keys for movement and rotation

		self.accept("escape", sys.exit)
		self.accept("arrow_left", self.setKey, ["left",1])
		self.accept("arrow_right", self.setKey, ["right",1])
		self.accept("arrow_up", self.setKey, ["forward",1])
		self.accept("arrow_down", self.setKey, ["backward",1])
		self.accept("arrow_left-up", self.setKey, ["left",0])
		self.accept("arrow_right-up", self.setKey, ["right",0])
		self.accept("arrow_up-up", self.setKey, ["forward",0])
		self.accept("arrow_down-up", self.setKey, ["backward",0])

		self.accept("z", self.setKey, ["cam-left",1])
		self.accept("x", self.setKey, ["cam-right",1])
		self.accept("z-up", self.setKey, ["cam-left",0])
		self.accept("x-up", self.setKey, ["cam-right",0])
		self.accept("l", self.setKey, ["l", 1])
		self.accept("l-up", self.setKey, ["l", 0])
		self.accept("w", self.setKey, ["w", 1])
		self.accept("s", self.setKey, ["s", 1])   
		self.accept("a", self.setKey, ["a", 1])   
		self.accept("d", self.setKey, ["d", 1])
		self.accept("r", self.setKey, ["res", 1])
		self.accept("w-up", self.setKey, ["w", 0])
		self.accept("s-up", self.setKey, ["s", 0])
		self.accept("a-up", self.setKey, ["a", 0])
		self.accept("d-up", self.setKey, ["d", 0])

		self.accept("j", self.setKey, ["firstPerson",1])
		self.accept("j", self.setKey, ["ThirdPerson",0])
		self.accept("k", self.setKey, ["firstPerson",0])
		self.accept("k", self.setKey, ["ThirdPerson",1])
		
		

		# taskMgr.add(self.cameraControl, "Camera Control")
		taskMgr.add(self.move,"moveTask")

		# Game state variables
		self.isMoving = False

		# Set up the camera
		
		#base.disableMouse()
		base.camera.setPos(self.sonic.getX(),self.sonic.getY()-10,40)
		# base.camera.setH(-90)
		self.cTrav = CollisionTraverser()

		self.sonicGroundRay = CollisionRay()
		self.sonicGroundRay.setOrigin(0,0,1000)
		self.sonicGroundRay.setDirection(0,0,-1)
		self.sonicGroundCol = CollisionNode('sonicRay')
		self.sonicGroundCol.addSolid(self.sonicGroundRay)
		self.sonicGroundCol.setFromCollideMask(BitMask32.bit(0))
		self.sonicGroundCol.setIntoCollideMask(BitMask32.allOff())
		self.sonicGroundColNp = self.sonic.attachNewNode(self.sonicGroundCol)
		self.sonicGroundHandler = CollisionHandlerQueue()
		self.cTrav.addCollider(self.sonicGroundColNp, self.sonicGroundHandler)

		# Uncomment this line to see the collision rays
		#self.sonicGroundColNp.show()
		#self.camGroundColNp.show()
	   
		# Uncomment this line to show a visual representation of the 
		# collisions occuring
		#self.cTrav.showCollisions(render)
		
		# Create some lighting
		ambientLight = AmbientLight("ambientLight")
		ambientLight.setColor(Vec4(.3, .3, .3, 1))
		directionalLight = DirectionalLight("dlight")
		directionalLight.setDirection(Vec3(0,-5, -5))
		directionalLight.setColor(Vec4(1, 1, 1, 1))
		#directionalLight.setHpr(0, -60, 0)
		directionalLight.setSpecularColor(Vec4(1, 1, 1, 1))
		ml=render.attachNewNode(directionalLight)
		#self.mylight= render.attachNewNode("dl")
		inter=Func(light,directionalLight)
		#directionalLight.reparentTo(self.mylight)
		#print dir(inter)
		inter.start()
		inter.loop()
		render.setLight(render.attachNewNode(ambientLight))
		render.setLight(ml)

		
	#Records the state of the arrow keys
	def setKey(self, key, value):
		self.keyMap[key] = value
	
	# Accepts arrow keys to move either the player or the menu cursor,
	# Also deals with grid checking and collision detection
	def move(self, task):

		# If the camera-left key is pressed, move camera left.
		# If the camera-right key is pressed, move camera right.

		base.camera.lookAt(self.sonic)
		if (self.keyMap["cam-left"]!=0):
			print "z"
			base.camera.setX(base.camera, -20 * globalClock.getDt())
		if (self.keyMap["cam-right"]!=0):
			print "x"
			base.camera.setX(base.camera, +20 * globalClock.getDt())

		if (self.keyMap["res"]==1):
			self.sonic.setPos(0,0,-2)
			self.keyMap["res"]=0


		startpos = self.sonic.getPos()

		if (self.keyMap["left"]!=0):
			self.sonic.setH(self.sonic.getH() + 300 * globalClock.getDt())
		if (self.keyMap["right"]!=0):
			self.sonic.setH(self.sonic.getH() - 300 * globalClock.getDt())
		if (self.keyMap["forward"]!=0):
			self.sonic.setY(self.sonic, -50 * globalClock.getDt())
		if (self.keyMap["backward"]!=0):
			self.sonic.setY(self.sonic, +50 * globalClock.getDt())

		if (self.keyMap["forward"]!=0) and (self.keyMap["backward"]==0):
			if self.isMoving is False:
				self.sonic.loop("board")
				self.isMoving = True

		elif (self.keyMap["backward"]!=0) and (self.keyMap["forward"]==0):
			if self.isMoving is False:
				self.sonic.loop("board")
				self.isMoving = True
				
		elif (self.keyMap["backward"]==0) and (self.keyMap["forward"]==0):
			if self.isMoving:
				self.sonic.stop()
				self.sonic.pose("run",5)
				print self.sonic.getX(),self.sonic.getY(),self.sonic.getZ()
				self.isMoving = False
		

		# If the camera is too far from ralph, move it closer.
		# If the camera is too close to ralph, move it farther.

		camvec = self.sonic.getPos() - base.camera.getPos()
		camvec.setZ(15)
		camdist = camvec.length()
		camvec.normalize()
		if (camdist > 10.0):
			base.camera.setPos(base.camera.getPos() + camvec*(camdist-10))
			camdist = 10.0
		if (camdist < 5.0):
			base.camera.setPos(base.camera.getPos() - camvec*(5-camdist))
			camdist = 5.0

		# Now check for collisions.

		self.cTrav.traverse(render)

		entries = []
		for i in range(self.sonicGroundHandler.getNumEntries()):
			entry = self.sonicGroundHandler.getEntry(i)
			entries.append(entry)
		entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
									 x.getSurfacePoint(render).getZ()))
		if (len(entries)>0) and (entries[0].getIntoNode().getName() == "BuildingCluster1"):
			self.sonic.setPos(startpos)
			self.isMoving = False
		elif (len(entries)>0) and (entries[0].getIntoNode().getName() == "BuildingCluster2"):
			self.sonic.setPos(startpos)
			self.isMoving = False
		elif (len(entries)>0) and (entries[0].getIntoNode().getName() == "BuildingCluster4"):
			self.sonic.setPos(startpos)
			self.isMoving = False
		elif (len(entries)>0) and (entries[0].getIntoNode().getName() == "BuildingCluster5"):
			self.sonic.setPos(startpos)
			self.isMoving = False
		elif (len(entries)>0):
			print entries[0].getIntoNode().getName(),self.sonic.getPos()
			if(entries[0].getIntoNode().getName()=="parked_car" or entries[0].getIntoNode().getName()=="body"):
				self.sonic.setY(self.sonic.getY()-50)
				self.sonic.setX(self.sonic.getX()-5)
			elif(entries[0].getIntoNode().getName()=="PoliceCar"):
				self.sonic.setY(self.sonic.getY()+50)
				self.sonic.setX(self.sonic.getX()-5)
			elif(entries[0].getIntoNode().getName()=="girlRacer"):
				self.sonic.setX(self.sonic.getX()+50)
				self.sonic.setY(self.sonic.getY()+5)
			elif(entries[0].getIntoNode().getName()=="building1"):
				if(abs(abs(self.sonic.getX())-130)<10 and abs(abs(self.sonic.getY())-44)<10):
					print "Pizza Delivery"
					#Intro Starts
					tex = MovieTexture("name")
					assert tex.read("models/play/happy.mp4"), "Failed to load video!"
					cm = CardMaker("My Fullscreen Card");
					cm.setFrameFullscreenQuad()
					cm.setUvRange(tex)
					card = NodePath(cm.generate())
					card.reparentTo(render2d)
					card.setTexture(tex)
					card.setTexScale(TextureStage.getDefault(), tex.getTexScale())
					sound=loader.loadSfx("models/play/happy.mp4")
					tex.synchronizeTo(sound)
					tex.setLoop(False)
					sound.play()
					def myTask(task):
						if (int(tex.getTime()) >=20):
					 		print "Stoping"
							c=0
					 		card.remove()
					 		self.sonic.setPos(0,0,-2)
							self.keyMap["res"]=0
							myscore = DirectLabel()
							myscore.reparentTo(render)
							#mytimer.setY(0)
							textObj = OnscreenText(text = "", pos = (0.95,0.95), 
							scale = 0.07,fg=(1,0.5,0.5,1),align=TextNode.ACenter,mayChange=1)
							c=c+1
							myscore['text'] = "Score:"+"1"
							#print mytimer['text']
							textObj.setText(myscore['text'])
							return task.done
							#if myMovieTexture.getTime() == myMovieLength:
							#	print "movie puri"
					 	return task.cont
					taskMgr.add(myTask, "Task")
					

				elif(abs(abs(self.sonic.getX())-88)<10 and abs(abs(self.sonic.getY())-172)<10):
					print "Pizza Delivery"
					#Intro Starts
					tex = MovieTexture("name")
					assert tex.read("models/play/angry.mp4"), "Failed to load video!"
					cm = CardMaker("My Fullscreen Card");
					cm.setFrameFullscreenQuad()
					cm.setUvRange(tex)
					card = NodePath(cm.generate())
					card.reparentTo(render2d)
					card.setTexture(tex)
					card.setTexScale(TextureStage.getDefault(), tex.getTexScale())
					sound=loader.loadSfx("models/play/angry.mp4")
					tex.synchronizeTo(sound)
					tex.setLoop(False)
					sound.play()
					def myTask(task):
					 	if (int(tex.getTime()) >=20):
					 		print "Stoping"
							c=0
					 		card.remove()
					 		self.sonic.setPos(0,0,-2)
							self.keyMap["res"]=0
							myscore = DirectLabel()
							myscore.reparentTo(render)
							#mytimer.setY(0)
							textObj = OnscreenText(text = "", pos = (0.95,0.95), 
							scale = 0.07,fg=(1,0.5,0.5,1),align=TextNode.ACenter,mayChange=1)
							c=c+1
							myscore['text'] = "Score:"+"2"
							#print mytimer['text']
							textObj.setText(myscore['text'])
							return task.done
							#if myMovieTexture.getTime() == myMovieLength:
							#	print "movie puri"
					 	return task.cont
					taskMgr.add(myTask, "Task")

			#self.sonic.setPos(startpos)

		# Keep the camera at one foot above the terrain,
		# or two feet above ralph, whichever is greater.
		
		'''entries = []
		for i in range(self.camGroundHandler.getNumEntries()):
				entry = self.camGroundHandler.getEntry(i)
				entries.append(entry)
		entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
																 x.getSurfacePoint(render).getZ()))
		if (len(entries)>0) and (entries[0].getIntoNode().getName() == "BuildingCluster1"):
				base.camera.setZ(entries[0].getSurfacePoint(render).getZ()+1.0)
		if (base.camera.getZ() < self.sonic.getZ() + 2.0):
				base.camera.setZ(self.sonic.getZ() + 2.0)'''

		# The camera should look in ralph's direction,
		# but it should also try to stay horizontal, so look at
		# a floater which hovers above ralph's head.
		
		base.camera.setPos(self.sonic.getPos())
		base.camera.setY(self.sonic.getY()+50*cos(self.sonic.getH()*pi/180))
		base.camera.setX(self.sonic.getX()-50*sin(self.sonic.getH()*pi/180))
		base.camera.setZ(self.sonic.getZ() + 15.0)
		if(self.keyMap["l"]==1):
			base.camera.setZ(self.sonic.getZ() + 1000.0)	
		sa =self.sonic.getPos();
		base.camera.lookAt(sa.x,sa.y,sa.z+15)
		

		# self.floater.setPos(self.sonic.getX()-4, self.floater.getY()-4, 5)
		# base.camera.setY(-base.camera.getY())
		# self.floater.setX(self.sonic.getX()-10)
		# base.camera.reparentTo(self.sonic)
		# self.floater.setH(180)
		# base.camera.setZ(+50)
		# base.camera.lookAt(self.floater)

		return task.cont

#w = World()
#run()
