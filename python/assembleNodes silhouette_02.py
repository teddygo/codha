#!C:/Python27/python.exe
'''
"""nuke_stereo_getfromList.py: verify fbx with nk. take list of .nk files. """

__author__      = "Nishith P Singhai"
__copyright__   = "Copyright 2012, Futureworks"

'''

from types import *
import nuke
import os
import re

class assembleNodes():
	'''
	this functions gets executed first when this class object is run
	'''
	def __init__(self):
		self.zam = re.compile('^(fg|bg|mg)$',re.IGNORECASE)
		self.bDropA = ""
		self.list = []
		self.camera = []
		self.groupNode = []
		self.fbxFile = []
		self.nkFile = []
		self.nkNodeList = []
		self.fbxCamFile = []
		self.sNoteA = []
		self.copy = []
		self.prem = []
		self.dotA = []
		self.p3d = []
		self.am = []
		self.rGeo = []
		self.sNoteB = []
		self.dotB = []
		self.scene = ""
		self.Incr = 100
		self.var = 100
		self.dIncr = 0
		self.SceneIncr = -1

		self.topLevelGroupName = ""
		self.secondLevelName = ""
		
	def getfbxCam(self):
		'''
		get fbx camera file from user and validate
		'''
		sw1 = 0
		self.fbxCamFile = nuke.getFilename('Camera Node will appear on top of network ...','cam*.fbx')																											 # camera
		if ((self.fbxCamFile == "") or isinstance(self.fbxCamFile ,NoneType) or not (os.path.isfile(self.fbxCamFile))):
			sw1 = 1
		return sw1

	def getfbxGroup(self):
		'''
		get fbx group files from user and validate
		'''
		sw1 = 0
		self.fbxFile = nuke.getFilename('fg bg mg .fbx file', '*g.fbx',multiple=True)
		if ((self.fbxFile[0] == "") or isinstance(self.fbxFile[0] ,NoneType) or not (os.path.isfile(self.fbxFile[0] ))):
			sw1 = 1
		return sw1
		
	def getNkFile(self):
		sw1 = 0
		self.nkFile = nuke.getFilename('fg bg mg .nk file','*.nk',multiple=True)																			# get list of .nk
		if ((self.nkFile[0] == "") or isinstance(self.nkFile[0] ,NoneType) or not (os.path.isfile(self.nkFile[0] ))):
			sw1 = 1
		return sw1
		
	def getFilesAndVerify(self):
		'''
		get user inputs and 
		find a better way of compacting if below
		'''
		sw1 = 0
		try:
			self.getfbxCam()
		except:
			print 'Error in camera selection ... '
			sw1 = 1

		return sw1
		
	def levelDistinction(self):
		'''
		create scene and camera node
		'''
		swch = 0

		self.camera = nuke.createNode('Camera2', 'read_from_file true file %s' % self.fbxCamFile,inpanel=False)

		self.camera.forceValidate()
		self.camera.setXYpos( -77 , -1282 )
		self.bDropA  = nuke.createNode('BackdropNode', inpanel=False)
		self.bDropA['label'].setValue('Cam imported from Maya')

		self.bDropA.setXYpos( -149 , -1360 )
		self.bDropA['bdwidth'].setValue(180)
		self.bDropA['bdheight'].setValue(260)

		self.scene = nuke.createNode('Scene',inpanel=False)
		self.scene.setXYpos( -100 , -70)

		'''
		from within each of fg mg and bg read sub levels , call createNodeSet for each of them
		'''
		for single in self.nkNodeList:
			copiedNode = nuke.nodePaste(single)
			self.SceneIncr = self.SceneIncr + 1
			retv = self.createNodeSet(copiedNode,self.SceneIncr)

		return swch

# call createNodeSet for each "eacl"

	def createNodeSet(self,apple,sCount):
		print 'apple.Class() : apple.name() ',apple.Class(), apple.name() ,'sCount ',sCount,'\n'
		i = 0

		bdN_Val_X = -1000
		bdN_Val_Y = -1000

		apple.setXYpos( (bdN_Val_X + self.Incr + 50), ( bdN_Val_Y + 100 ) )	# this group node is taken from user

		self.sNoteA = nuke.createNode('StickyNote', inpanel=False)
		self.sNoteA['label'].setValue('Roto layer loads here')
		self.sNoteA.setXYpos( ( bdN_Val_X + self.Incr + 50 ), ( bdN_Val_Y  + 140) )

		self.dotA = nuke.createNode("Dot",inpanel=False)
		self.dIncr = self.dIncr + 500 
		self.dotA.setXYpos( bdN_Val_X  + (self.dIncr - 466) , bdN_Val_Y + (-58) )
		self.dotA.setInput(0,self.camera)

		self.copy = nuke.createNode("Copy", inpanel=False)
		self.copy.setXYpos( (bdN_Val_X + self.Incr - 100), ( bdN_Val_Y + 100 ) )
		self.copy.setInput(0,apple)

		self.prem = nuke.createNode('Premult', inpanel=False)
		self.prem.setXYpos( (bdN_Val_X + self.Incr - 100), (bdN_Val_Y + 200) )
		self.prem.setInput(0,self.copy)

		self.p3d = nuke.createNode("Project3D", inpanel=False)
		self.p3d.setXYpos( (bdN_Val_X + self.Incr - 100), (bdN_Val_Y + 300) )

		self.p3d.setInput(0,self.prem)

		self.p3d.setInput(1,self.dotA)

		self.am = nuke.createNode("ApplyMaterial", inpanel=False)               # apply material
		self.am.setXYpos( (bdN_Val_X + self.Incr - 100),  (bdN_Val_Y + 400) )

		self.rGeo = nuke.createNode("ReadGeo", inpanel=False)

		self.rGeo.setXYpos( (bdN_Val_X + self.Incr + 50) ,  (bdN_Val_Y + 400) )

		self.am.setInput(0,self.rGeo)
		self.am.setInput(1,self.p3d)

		self.sNoteB = nuke.createNode('StickyNote', inpanel=False)
		self.sNoteB['label'].setValue('fbx export loads here')
		self.sNoteB.setXYpos( (bdN_Val_X + self.Incr + 50), (bdN_Val_Y + 440) )

		self.dotB = nuke.createNode("Dot", inpanel=False)
		self.dotB.setXYpos( (bdN_Val_X + self.Incr - 60)  , (bdN_Val_Y + 500) )
		self.dotB.setInput(0,self.am)
		self.scene.setInput(sCount,self.dotB)

		self.Incr = self.Incr + 500

# put validation for viewer
		curViewer = nuke.activeViewer()
		if not isinstance(curViewer,NoneType):
			viewerNode = curViewer.node()
			viewer = viewerNode.name()                                          # viewer node
			viewerNode.setInput(0,self.scene)                                   # connect scene to viewer
			viewerNode.setXYpos( -85, 20 )
			
		return 1			

ooc = assembleNodes()
ogffu = ooc.getFilesAndVerify()
# call window to select nk files
if (ogffu == 0):
	ooc.nkNodeList = nuke.getFilename('This is your complete set of .fbx files','*.fbx',multiple=True)																			# get list of .nk
	ooc.levelDistinction()
