from minor_02 import minor
import maya.OpenMaya as onma
import maya.cmds as cmds
import MySQLdb as mdb
import unicodedata
import platform
import shutil
import os,re
import stat


class major(object):
	def __init__(self):
		self.win = "major File Name"
		self.major1 = "text"
		self.major2 = "textField"
		self.major3 = "button"

	def copy_To_Minor(self):
		'''
		this is engine. Where all functions get called in a manner.
		'''
		shNm = ""
		if (self.authenticatesql(self.host, self.user, self.pwss, self.dbnm) == 1):		# make connection to database
			if	(self.isfileNameEmpty() == 1):													# file name not present
	#				self.ask_user_for_project_shot_other_details_once_then_save_file_in_format()
				print cmds.layoutDialog(ui=self.ask_user_for_project_shot_other_details_once_then_save_file_in_format)
			# extract shot name from file
			prjNm = cmds.file(query=True,shn=True,sn=True).split("_")[0]
			prjType = self.returnProjectType(prjNm)
			if not (prjType == "long"):
				shNm = cmds.file(query=True,shn=True,sn=True).split("_")[1]
			else:
				shNm = cmds.file(query=True,shn=True,sn=True).split("_")[2]
	
			self.minorFolderName = cmds.workspace(query=1,act=1) + "/scenes/" + shNm  + "/minor/"
			if not os.path.isdir(self.minorFolderName):
				os.mkdir(self.minorFolderName)
			print 'self.minorFolderName',self.minorFolderName,'\n'
			if	(self.isfileNameConventionPresent(self.returnFileName()) == 1):				# file name convention not existing
				message = ("\n" + (self.underscore*40) + "\n\tValid format :\n%s for a movie \nor\n%s for a commercial \nUse save to change to above matching format " + "\n" + (self.underscore*40)) % (self.fileformat_1 ,self.fileformat_2 )
				print message
			elif (self.is_folder_structure_proper(self.minorFolderName) == 1):
				message = "Check Folder structure. Save File in folder %s " % (self.minorFolderName)
				print message
			else:
				self.saveFileName(self.minorFolderName,self.ffilename)
				self.send_path_to_table(platform.node(),self.minorFolderName)
		else:
			message = "connection not made. connect to admin "
			print message		

	def wu(self):
		if(cmds.window(self.win, q = 1, ex = 1)):
			cmds.deleteUI(self.win)
		if(cmds.windowPref(self.win, ex = True)):
			cmds.windowPref(self.win, r = True)

		cmds.window(self.win, t = "majorFileName", h = 240, w = 300,rtf=1,s=0)
		mainCol = cmds.columnLayout()
		cmds.columnLayout()
		cmds.image( image="//Fw-isilon-1/data/_3dAppDomain/_images/render_layers.png",w=300,h=45 )
		cmds.text(label="")
		self.major2 = cmds.textField()
		self.aa = cmds.textField( self.major2, edit=True, text= obj.returnFileName())
		cmds.text(label = " ")
		sRow = cmds.rowLayout(numberOfColumns=3)
		cmds.text(label="")
		cmds.button( label="save",command="obj.copy_To_Major()" )
		cmds.button( label=" Close ", command=("cmds.deleteUI(\"" + self.win + "\", window=True)") )
		cmds.setParent(sRow)
		cmds.setParent(mainCol)
		cmds.text(label="")
		cmds.showWindow(self.win)


abc = major()
abc.majorPrepare()


