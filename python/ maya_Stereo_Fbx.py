# <future development>
		# if path does not exist then show button to take image path from ( only maya_export_fbx.png ). once taken then display image
		# add button to accept preset
# </future development>
import maya.OpenMaya as OpenMaya
import maya.cmds as cmds
import maya.mel as mel
import unicodedata
import sys

class maya_Stereo_Fbx(object):
	def __init__(self):
		'''
		load fbxmaya plugin in initialisation
		'''
		try:
			plugin = cmds.pluginInfo( query=True, listPlugins=True, version=True )
			fbxplugin = 'fbxmaya'
			
			if cmds.pluginInfo(fbxplugin+ ".mll", query=True, loaded=True):
				cmds.pluginInfo(fbxplugin + ".mll", edit=True, autoload=True)
			else:
				cmds.loadPlugin(fbxplugin + ".mll")
		except:
			print "fbxMaya was not found on MAYA_PLUG_IN_PATH:", sys.exc_info()[0]

		self.listGrp = []
		self.children = []
		self.childrenLong = []
#		self.listGrp.append('FG')
#		self.listGrp.append('BG')
#		self.listGrp.append('MG')
		self.listGrp = ['fg','mg','bg']

		self.upperL = r'''[A-Z]'''
		'''
		window variables
		'''
		self.win = "fbxExport"
		self.fbxPath1 = "textfield"
		self.fbxPath2 = "button"
		self.expPath = ""

	def getPathDialog(self):

		mel.eval( 'global string $FOUNDATION_FILEBROWSE = ""' )
		mel.eval( 'global proc foundation_melBrowseCallback(string $path, string $type){ global string $FOUNDATION_FILEBROWSE; $FOUNDATION_FILEBROWSE = $path; }' )
		mel.eval( 'global proc string foundation_melGetBrowsePath(){ global string $FOUNDATION_FILEBROWSE; return $FOUNDATION_FILEBROWSE; }' )
		mel.eval( 'fileBrowser "foundation_melBrowseCallback" "Current Project" "" 4;' )
		path = mel.eval( 'foundation_melGetBrowsePath()' )
		if path:
			return path

	def sortAndExport(self):

		path = cmds.textField(obj.expPath,query=True,text=True).replace("\\","/")
		print 'path ',path ,'\n'

		try:
			otp = [cmds.objExists(grp) for grp in self.listGrp]
			for i in range(0,len(otp)):
				if (otp[i] == 0):
					print 'not existing %s' % self.listGrp[i]
		except:
			print "Unexpected error:", sys.exc_info()[0]
			obj.close()
		else:
			try:
				self.listGrp.remove('fg')

				for l in [cmds.listRelatives(each, children=True, noIntermediate=True, fullPath=True) for each in self.listGrp]:
					if (len(l) == 1):
	
						self.children.append(l[0])
					else:
						print 'else self.children : ',self.children,'\n'
						for each in l:
							self.children.append(each)
	
				'''
				list only fg\'s relatives
				'''
				_1stLevel = [cmds.listRelatives('fg', children=True, noIntermediate=True, fullPath=True)]
				for l in [cmds.listRelatives(each , children=True, noIntermediate=True, fullPath=True) for each in _1stLevel ]:
					if (len(l) == 1):
						self.children.append(l[0])
					else:
						for each in l:
							self.children.append(each)
							
				print 'self.children ',self.children,'\n'

				for each in range(0,len(self.children)):
					print 'each   ',self.children[each]
					cmds.select(self.children[each],r=True)
					#evalStr = 'FBXExport -s FBXExportAnimationOnly -v true FBXExportFileVersion FBX201000 -f\"' + path + "/"+ self.children[each].split("|")[len(self.children[each].split("|"))-1] + '\"'
					evalStr = 'FBXLoadExportPresetFile -f "C:/Users/nishith.FWDOMAIN/Documents/maya/FBX/Presets/2013.1/export/Prem_fbx.fbxexportpreset"; \
					FBXExport -s -f\"' + path + "/"+ self.children[each].split("|")[len(self.children[each].split("|"))-1] + '\"'
					print 'evalStr ',evalStr ,'\n'
					mel.eval(evalStr)
				obj.close()
			except:
				print "Objects Not Existing - ", sys.exc_info()[0]
				obj.close()

	def abc(self):
		rt = obj.getPathDialog()
		cmds.textField(self.expPath, edit=True,text=rt)

	def close(self):
		cmds.deleteUI(obj.win, window=True)

	def nu(self):
		if(cmds.window(self.win, q = 1, ex = 1)):
			cmds.deleteUI(self.win)
		if(cmds.windowPref(self.win, ex = True)):
			cmds.windowPref(self.win, r = True)

		cmds.window(self.win, t = "Export as FBX", h = 170, w = 250,rtf=1,s=0)
		mainCol = cmds.columnLayout()
		cmds.columnLayout()
		cmds.image( image="//10.10.35.93/data/_3dAppDomain/_images/maya_export_fbx.png",w=250,h=45 )
		cmds.text(label="")
		uRow = cmds.columnLayout()
		#zRow = cmds.rowLayout(numberOfColumns=1,cl1="left",cw1=170,ct1="left")
		cmds.button(label='click to set preset file')		
		#cmds.setParent(zRow)
		tRow = cmds.rowLayout(numberOfColumns=2,cl2=("right","left"),cw2=(170,70),ct2=("right","left"))

		self.expPath = cmds.textField()
		cmds.textField( self.expPath , edit=True, width = 140, enterCommand=('cmds.setFocus(\"' + self.expPath + '\")') )
		cmds.button(label='Browse',command='obj.abc()')
		cmds.setParent(tRow)
		cmds.setParent(uRow)
		cmds.text(label = " ")
		sRow = cmds.rowLayout(numberOfColumns=2,cl2=("center","center"),cw2=(120,130),ct2=("both","both"),co2=(10,05))
		butExp = cmds.button( label='Push Export', command='obj.sortAndExport()')
		cmds.button( label=" Close ", command=("obj.close()"))
		cmds.setParent(sRow)
		cmds.setParent(mainCol)
#		cmds.text(label="")
		cmds.showWindow(self.win)

obj = maya_Stereo_Fbx()
if not (cmds.file(query=True, shn=True, sn=True)):
	OpenMaya.MGlobal.displayWarning("scene file should give you data you need. Without it you will be blank as now")
else:
	obj.nu()
