#!c:/Python26/python.exe -u
#-------------------------------------------------------------------------------
# Name: 	   setInternals
# Purpose:
#
# Author:	   nishith
#
# Created:	   25/09/2012
# Copyright:   (c) nishith 2012
# Licence:	   <your licence>
#-------------------------------------------------------------------------------

import maya.cmds as cmds
import maya.mel as mel
import maya.utils as utils
mel.eval('source "renderLayerBuiltinPreset.mel"')

class Callback(object): 
    def __init__(self, func, *args, **kwargs): 
        self.func = func 
        self.args = args 
        self.kwargs = kwargs
    def __call__(self, *args): 
        return self.func( *self.args, **self.kwargs ) 

class renderLayerCreate(object):
	def __init__(self):
		self.win = "RenderLayer"
		self.renPass1 = "checkBox1"
		self.renPass2 = "checkBox2"

		self.aa = ""
		self.bb = ""

		self.chkBx1Arr = ["Beauty"]
		self.chkBx2Arr = ["Ambient_Occlusion", "RGB", "cutMatte", "groundShadow"]


	def wu(self):
		if(cmds.window(self.win, q = 1, ex = 1)):
			cmds.deleteUI(self.win)
		if(cmds.windowPref(self.win, ex = True)):
			cmds.windowPref(self.win, r = True)

		cmds.window(self.win, t = "RenderLayer", h = 240, w = 260,rtf=1,s=0)
		mainCol = cmds.columnLayout()
		cmds.columnLayout()
		cmds.image( image="render_layers.png",w=300,h=45 )
		cmds.text(label="")
		self.aa = cmds.checkBoxGrp( self.renPass1 , numberOfCheckBoxes=1, label=" ",label1 = self.chkBx1Arr[0], vr=1)
		self.bb = cmds.checkBoxGrp( self.renPass2 , numberOfCheckBoxes=4, label="     ", labelArray4 = self.chkBx2Arr , vr=1)

		cmds.text(label = " ")
#		sRow = cmds.rowLayout(numberOfColumns=3)
		sRow = cmds.rowLayout(numberOfColumns=2,cl2=("right","left"),cw2=(120,120),ct2=("right","left"))
		cmds.button( label="Passes",command=Callback(self.qu))
		cmds.button( label=" Close ", command=("cmds.deleteUI(\"" + self.win + "\", window=True)") )
		cmds.setParent(sRow)
		cmds.setParent(mainCol)
		cmds.text(label="")
		cmds.showWindow(self.win)

	def createRenderLayerCommand(self,nm):
		print 'its this one...'
		if not (cmds.objExists(nm) and cmds.nodeType(nm) == "renderLayer" ):
			try:
				print "creating ",nm
				cmds.createRenderLayer( name= nm , number=1, noRecurse=True)
				return 
			except:
				print "Unexpected error:", sys.exc_info()[0]

	def qu(self):

		if (cmds.checkBoxGrp(self.aa, query=True, value1=True)):
			self.createRenderLayerCommand(self.chkBx1Arr[0])

		if (cmds.checkBoxGrp(self.bb, query=True, value1=True)):
			self.createRenderLayerCommand(self.chkBx2Arr[0])

		if (cmds.checkBoxGrp(self.bb, query=True, value2=True)):
			self.createRenderLayerCommand(self.chkBx2Arr[1])

		if (cmds.checkBoxGrp(self.bb, query=True, value3=True)):
			self.createRenderLayerCommand(self.chkBx2Arr[2])

		if (cmds.checkBoxGrp(self.bb, query=True, value4=True)):
			self.createRenderLayerCommand(self.chkBx2Arr[3])

		utils.executeDeferred(mel.eval('renderLayerEditorRenderable RenderLayerTab \"defaultRenderLayer\" 0;'))
		utils.executeDeferred(mel.eval('updateEditorFeedbackRenderLayer RenderLayerTab defaultRenderLayer;'))

		allRenderLayerName = cmds.ls(type='renderLayer')
		
		utils.executeDeferred(mel.eval('updateRendererUI;'))
		utils.executeDeferred(mel.eval('unifiedRenderGlobalsWindow ;'))

		for each in allRenderLayerName:
			cmds.editRenderLayerGlobals(currentRenderLayer=each)
			if(each=="Ambient_Occlusion"):
				print "AO"
				cmds.editRenderLayerAdjustment("defaultRenderGlobals.currentRenderer")

				cmds.setAttr("defaultRenderGlobals.currentRenderer", "mentalRay", type="string")
				cmds.editRenderLayerAdjustment("defaultRenderGlobals.imageFormat")

				cmds.setAttr("defaultRenderGlobals.imageFormat", 3)

				mel.eval("renderLayerBuiltinPreset occlusion " + each)			# comments missing
				ShadingGroup = cmds.listConnections(each, s=True, d=False, type="shadingEngine")
				SurfaceShader = cmds.listConnections(ShadingGroup[0], s=True,d=False)
				ao = cmds.listConnections(SurfaceShader[0], s=True, d=False )
				cmds.setAttr( (ao[0]+".samples"), 32)

				cmds.editRenderLayerAdjustment("miDefaultOptions.maxSamples")
				cmds.setAttr("miDefaultOptions.maxSamples", 2)

				cmds.editRenderLayerAdjustment("miDefaultOptions.filter")
				cmds.setAttr( "miDefaultOptions.filter", 1)
				cmds.editRenderLayerAdjustment("miDefaultOptions.rayTracing")
				cmds.editRenderLayerAdjustment("miDefaultOptions.maxReflectionRays")
				cmds.editRenderLayerAdjustment("miDefaultOptions.maxRefractionRays")
				cmds.editRenderLayerAdjustment("miDefaultOptions.maxRayDepth")
				cmds.editRenderLayerAdjustment("miDefaultOptions.maxShadowRayDepth")
				cmds.setAttr("miDefaultOptions.maxReflectionRays", 1)
				cmds.setAttr("miDefaultOptions.maxRefractionRays", 1)
				cmds.setAttr("miDefaultOptions.maxRayDepth", 1)
				cmds.setAttr("miDefaultOptions.maxShadowRayDepth", 2)
				utils.executeDeferred(mel.eval('applyOcclusion("Ambient_Occlusion")'))			# comments missing
				cmds.setAttr("miDefaultOptions.globalIllum", 0)
				cmds.setAttr("miDefaultOptions.finalGather", 0)

			elif (each == "Beauty"):
				print "Beauty"
				cmds.editRenderLayerMembers("Beauty",noRecurse=True)					# mentalrayIbl1
				cmds.editRenderLayerAdjustment("defaultRenderGlobals.currentRenderer")
				cmds.setAttr("defaultRenderGlobals.currentRenderer" , "mentalRay", type = "string" )
				cmds.editRenderLayerAdjustment("defaultRenderGlobals.imageFormat")
				cmds.setAttr("defaultRenderGlobals.imfPluginKey", "exr", type="string")
				cmds.setAttr("defaultRenderGlobals.imageFormat",51)
#				if not (cmds.isConnected( 'Beauty.renderPass', 'depth.owner' )):
#					cmds.connectAttr('Beauty.renderPass', 'depth.owner', nextAvailable=True)
#				else:
				if ((cmds.connectionInfo( 'defaultRenderLayer.renderPass', isDestination=True) == False) and (cmds.connectionInfo( 'defaultRenderLayer.renderPass', isSource=True) == False)):
					cmds.connectAttr("defaultRenderLayer.renderPass", "depth.owner",na=True)
					cmds.connectAttr("defaultRenderLayer.renderPass", "diffuse.owner",na=True)
					cmds.connectAttr("defaultRenderLayer.renderPass", "incandescence.owner",na=True)
					cmds.connectAttr("defaultRenderLayer.renderPass", "indirect.owner",na=True)
					cmds.connectAttr("defaultRenderLayer.renderPass", "mv2DToxik.owner",na=True)
					cmds.connectAttr("defaultRenderLayer.renderPass", "reflection.owner",na=True)
					cmds.connectAttr("defaultRenderLayer.renderPass", "refraction.owner",na=True)
					cmds.connectAttr("defaultRenderLayer.renderPass", "shadow.owner",na=True)
					cmds.connectAttr("defaultRenderLayer.renderPass", "specular.owner",na=True)

			elif (each == "RGB"):
				print "RGB"
				cmds.editRenderLayerAdjustment('defaultRenderGlobals.currentRenderer')
				cmds.setAttr('defaultRenderGlobals.currentRenderer', 'mayaSoftware', type='string')
				cmds.editRenderLayerAdjustment('defaultRenderGlobals.imageFormat')
				cmds.setAttr('defaultRenderGlobals.imageFormat', 4)
				rendQual = cmds.listConnections('defaultRenderGlobals.qual')
				cmds.setAttr(rendQual[0]+'.shadingSamples', 2)
				cmds.setAttr(rendQual[0]+'.maxShadingSamples', 8)
				cmds.setAttr(rendQual[0]+'.visibilitySamples', 1)
				cmds.setAttr(rendQual[0]+'.maxVisibilitySamples', 4)
				cmds.setAttr(rendQual[0]+'.edgeAntiAliasing', 0)
				cmds.setAttr(rendQual[0]+'.useMultiPixelFilter', 1)
				cmds.setAttr(rendQual[0]+'.redThreshold', 0.4)
				cmds.setAttr(rendQual[0]+'.greenThreshold', 0.3)
				cmds.setAttr(rendQual[0]+'.blueThreshold', 0.6)
				cmds.setAttr('defaultRenderGlobals.motionBlur', 1)
				cmds.setAttr('defaultRenderGlobals.motionBlurUseShutter', 1)
				cmds.setAttr('defaultRenderGlobals.motionBlurShutterOpen', 0)
				cmds.setAttr('defaultRenderGlobals.motionBlurShutterClose', 0)
				cmds.setAttr('defaultRenderGlobals.motionBlurUseShutter', 0)
				cmds.setAttr('defaultRenderGlobals.motionBlur', 0)
				
				
		if(cmds.window(self.win, q = 1, ex = 1)):
			cmds.deleteUI(self.win,window=True)
