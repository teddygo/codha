'''
put comments here
if layer fg then go to second sub layer and project. if more second sub layer\'s then project them too
if layer mg then go to first sub layer and project. If more first sub layer\'s then project them too
if layer bg then go to first sub layer and project. If more first sub layer\'s then project them too

1) if fg bg or mg - done
2) find children layers - 
3) export children layers -

sw1 = 0 ok
sw1 = 1 not ok

swch = 0 ok
swch = 1 not ok
'''

#check if scene file is empty , prompt user to select file 

import nuke
import os

import re
from types import *

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
		self.fbxCamFile = []
		self.bDrop = []
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
		
		self.parentNode = ""

	def getfbxCam(self):
		'''
		get fbx camera file from user and validate
		'''
		sw1 = 0
		self.fbxCamFile = nuke.getFilename('Get Fbx Camera File ...','cam*.fbx')																				# camera
		print 'self.fbxCamFile : ',self.fbxCamFile,'\n'
		if ((self.fbxCamFile == "") or isinstance(self.fbxCamFile ,NoneType) or not (os.path.isfile(self.fbxCamFile))):
			sw1 = 1
		return sw1

	def getNkFile(self):
		sw1 = 0
		self.nkFile = nuke.getFilename('Select exported group nodes .nk files','*.nk',multiple=True)																			# get list of .nk
		if ((self.nkFile[0] == "") or isinstance(self.nkFile[0] ,NoneType) or not (os.path.isfile(self.nkFile[0] ))):
#			print 'Select File ( multiple ) ...'
			sw1 = 1
		return sw1

	def getfbxGroup(self):
		'''
		get fbx group files from user and validate
		'''
		sw1 = 0
		self.fbxFile = nuke.getFilename('Select fbx Files ...', '*.fbx',multiple=True)
		if ((self.fbxFile[0] == "") or isinstance(self.fbxFile[0] ,NoneType) or not (os.path.isfile(self.fbxFile[0] ))):
			sw1 = 1
		return sw1

	def getFilesAndVerify(self):
		'''
		get user inputs and
		find a better way of compacting if below
		'''
		sw1 = 0
		if (self.getfbxCam() == 0):
			if (self.getfbxGroup() == 0):
				if (self.getNkFile() == 0):
					for each in range(0,len(self.nkFile)):
						self.groupNode.append(nuke.nodePaste(self.nkFile[each]))
					print 'self.nkFile[each]',self.nkFile
				else:
					print '3names not matching ... get them to match then come here ... '
					sw1 = 1
			else:
				print '2names not matching ... get them to match then come here ... '
				sw1 = 1
		else:
			print '1names not matching ... get them to match then come here ... '
			sw1 = 1
		'''
		verify that no group object is nonetype
		'''
		for a in self.groupNode:
			if isinstance(a,NoneType):
				sw1 = 1
		return sw1
		
	def deselectAll(self):
#	    for n in nuke.selectedNodes():
		for n in nuke.allNodes():
			n['selected'].setValue(False)

	def levelDistinction(self):
		'''
		create scene and camera node
		'''
		i = 0
		swch = 0

		self.camera = nuke.createNode('Camera2', 'read_from_file true file %s' % self.fbxCamFile,inpanel=False)
#		self.camera = nuke.nodes.Camera(name='Camera2')
#		self.camera['read_from_file'].setValue('True')
#		self.camera['file'].setValue(self.fbxCamFile)
#       change all createnode to nuke.nodes..<>

		self.camera.forceValidate()
		self.camera.setXYpos( -77 , -1282 )
		self.bDropA  = nuke.nodes.BackdropNode(label="Cam imported from Maya")

		self.bDropA.setXYpos( -149 , -1360 )
		self.bDropA['bdwidth'].setValue(180)
		self.bDropA['bdheight'].setValue(260)

		self.scene = nuke.nodes.Scene()
		self.scene.setXYpos( -100 , -70)
		self.deselectAll()
		'''
		from within each of fg mg and bg read sub levels , call createNodeSet for each of them
		'''
		for i in range(0,len(self.fbxFile)):
			parent = os.path.basename(self.fbxFile[i]).split("_")[0]

			for j in range(0,len(self.groupNode)):
				if (parent == self.groupNode[j].name()):
					print 'parent =: ',self.groupNode[j].name() + ".nk",'\n'
					self.deselectAll()
					self.parentNodeCopy(self.groupNode[j])
					self.SceneIncr = self.SceneIncr + 1
#					nuke.nodes.nodename( self.groupNode[i].name() )
					print 'self.parentNode name',self.parentNode.name() ,'\n'
					retv = self.createNodeSet(self.fbxFile[i], self.parentNode , self.SceneIncr)
					if not retv:
						swch = 1
						print 'not run proper creatNode'
#						break

# 					send fbx file , parent / grandparent of fbx file, incrementCount

	def parentNodeCopy(self,papaNode):
		papaNode.knob("selected").setValue(True)
		nuke.nodeCopy('%clipboard%')
		self.parentNode = nuke.nodePaste('%clipboard%')

	

	def createNodeSet(self,apple, appleParent, sCount):
		print 'apple ',apple , 'appleParent ',appleParent.name() ,'sCount ', sCount,'\n'

		i = 0

		bdN_Val_X = -1000
		bdN_Val_Y = -1000

#		self.bDrop = nuke.createNode('BackdropNode', inpanel=False)
#		self.bDrop['label'].setValue('These are the imported roto and maya object files. Number of copies of these depends on number of stereo layers defined in xml file.  ')
		self.bDrop = nuke.nodes.BackdropNode(label="These are the imported roto and maya object files")
		self.bDrop.setXYpos( (bdN_Val_X + self.Incr), bdN_Val_Y )
		self.bDrop['bdwidth'].setValue(bdN_Val_X + 1200)
		self.bDrop['bdheight'].setValue(bdN_Val_Y + 1500)


		appleParent.setXYpos( (bdN_Val_X + self.Incr + 50), ( bdN_Val_Y + 100 ) )	# this group node is taken from user

#		self.sNoteA = nuke.createNode('StickyNote', inpanel=False)
#		self.sNoteA['label'].setValue('Roto layer loads here')
		self.sNoteA = nuke.nodes.StickyNote(label="Roto layer loads here")
		self.sNoteA.setXYpos( ( bdN_Val_X + self.Incr + 50 ), ( bdN_Val_Y  + 140) )

#		self.dotA = nuke.createNode("Dot",inpanel=False)
		self.dotA = nuke.nodes.Dot()
		self.dIncr = self.dIncr + 500 
		self.dotA.setXYpos( bdN_Val_X  + (self.dIncr - 466) , bdN_Val_Y + (-58) )
		self.dotA.setInput(0,self.camera)
		
#		self.copy = nuke.createNode("Copy", inpanel=False)
		self.copy = nuke.nodes.Copy()
		self.copy.setXYpos( (bdN_Val_X + self.Incr - 100), ( bdN_Val_Y + 100 ) )
		self.copy.setInput(0,appleParent)

#		self.prem = nuke.createNode('Premult', inpanel=False)
		self.prem = nuke.nodes.Premult()
		self.prem.setXYpos( (bdN_Val_X + self.Incr - 100), (bdN_Val_Y + 200) )
		self.prem.setInput(0,self.copy)

#		self.p3d = nuke.createNode("Project3D", inpanel=False)
		self.p3d = nuke.nodes.Project3D()
		self.p3d.setXYpos( (bdN_Val_X + self.Incr - 100), (bdN_Val_Y + 300) )

		self.p3d.setInput(0,self.prem)
		self.p3d.setInput(1,self.dotA)

#		self.am = nuke.createNode("ApplyMaterial", inpanel=False)               # apply material
		self.am = nuke.nodes.ApplyMaterial()
		self.am.setXYpos( (bdN_Val_X + self.Incr - 100),  (bdN_Val_Y + 400) )
		print 'apple ',apple,'\n'
#		self.rGeo = nuke.createNode("ReadGeo", inpanel=False)
		self.rGeo = nuke.nodes.ReadGeo()
#		self.rGeo['file'].setValue(apple)
		fileKnob = self.rGeo.knob("file")
		fileKnob.setValue(apple)
		self.rGeo.setXYpos( (bdN_Val_X + self.Incr + 50) ,  (bdN_Val_Y + 400) )

		self.am.setInput(0,self.rGeo)
		self.am.setInput(1,self.p3d)

#		self.sNoteB = nuke.createNode('StickyNote', inpanel=False)
		self.sNoteB = nuke.nodes.StickyNote()
		self.sNoteB['label'].setValue('fbx export loads here')
		self.sNoteB.setXYpos( (bdN_Val_X + self.Incr + 50), (bdN_Val_Y + 440) )
		
#		self.dotB = nuke.createNode("Dot", inpanel=False)
		self.dotB = nuke.nodes.Dot()
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
if (ogffu == 0):
	ooc.levelDistinction()
