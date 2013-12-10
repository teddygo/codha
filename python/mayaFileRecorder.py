#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      
#
# Created:     23-09-2012
# Copyright:   (c)  2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python
'''
__author__      = "Nishith Singhai"
__copyright__   = "Copyright 2012, ibrowse"

#	acknowledgements : Thomas Wouters for line 213

Description :
		mayaFileRecorder.py: if filename not present then prompt user giving window option from database.
else increment version if valid file name structure but maintain only 5 files in minor folder.
This script presumes that user has set project

#	file name structure
#	for long format (movies)
#	show_scn_shNo_description_version_initials_comments(optional).extension

#	for commercials
#	show_shNo_description_version_initials_comments(optional).extension

#	Switch user : sw1
#	1 = ok
#	0 = not ok


modules needed in this script
'''

import maya.OpenMaya as onma
import maya.cmds as cmds
import MySQLdb as mdb
import unicodedata
import platform
import shutil
import os,re
import stat

class mayaFileRecorder(object):
	def __init__(self):
#		self.sqlConnected = 0
		self.message = ""
		self.sw1 = 0
		self.l1 = ""
#		self.l2 = ""
		self.l3 = ""
		self.t1 = ""
		self.l4 = ""
		self.l5 = ""
		self.l6 = ""
		self.l7 = ""
#		self.form = ""

		self.db = ""
		self.host = "localhost"
#		self.host = "192.168.1.12"
		self.user = "root"
		self.pwss = ""
		self.dbnm = "rgbashadow"
		self.underscore = "_"
		self.filext = "ma" # this can be passed as parameter
		self.dot = "."
		self.ffilename = ""
		self.minorFolderName = ""
		self.majorFolderName = ""
		self.latestFolderName = ""
		self.fileformat_1 = "show_scn_shNo_description_v(XXX)_ini_comments(optional).extension"
		self.fileformat_2 = "show_shNo_description_v(XXX)_ini_comments(optional).extension"



	def returnFileName(self):
		'''
		return file name
		'''
		return cmds.file(query=True,shn=True,sn=True)

	def returnLongFileName(self):
		'''
		return file path + file name
		'''
		return cmds.file(query=True,sn=True)

	def isfileNameEmpty(self):
		'''
		return 1 if file name empty
		'''
		self.sw1 = 0
		if (self.returnFileName() == ""):
			self.sw1 = 1
		return self.sw1


	def isfileNameConventionPresent(self,filename):
		'''
		#1 not ok
		'''
		self.sw1 = 0
#		regexp = r'''\b\w{3}_\w{6}_\w{2}\d{3}_[a-zA-Z]+_v\d{1,2}_[a-z]{3}_[a-zA-Z0-9]+.ma|\b\w{3}_\w{2}\d{3}_[a-zA-Z]+_v\d{1,2}_[a-z]{3}_[a-zA-Z0-9]+.ma'''
		regexp = r'''\b\w{3,4}(_\w{3}\d{2})?_\w{2}\d{2}_[a-zA-Z]+_v\d{1,2}_[a-z]{3}(_[a-zA-Z0-9]+)?.ma'''
		if not re.match(regexp , filename):
			self.sw1 = 1
			self.message = "file name not matching. contact admin for help"
			onma.MGlobal().displayError(self.message)
		else:
			try:
				self.prefixValidation(filename)
			except Exception, E:
				message = str(E)
				print message
		return self.sw1

	def prefixValidation(self, filename):
		'''
		only 3 components need to be validated against the sql table
		'''
		self.sw1 = 0
		try:
			prjprx = self.getFileComponents(filename,"_")[0]
			seqprx = self.getFileComponents(filename,"_")[1]
			shtprx = self.getFileComponents(filename,"_")[2]
			ft1 = "%s"
			ft2 = "%s"
			ft3 = "%s"
			ft4 = "%s"
			field1nm = "prjType"
			field2nm = "projects"
			field3nm = "prjPrefix"
	#		field4nm = prjprx
			prjtype = self.readSingleField(ft1, field1nm ,ft2, field2nm, ft3, field3nm, ft4, prjprx )[0]

			shSS = "select prjPrefix from projects"
			scSS = "select scnPrefix from scene"
			shSS = "select shotName from shots"

			if (self.verifyName(shSS, prjprx) and self.verifyName(shSS, seqprx)):
				if (prjtype == 'long'):
					if (self.verifyName(scSS, shtprx)):
						self.sw1 = 1
				else:
					self.sw1 = 1
			return self.sw1
		except Exception, E:
			message = str(E)
			print message

			
	def verifyName(self, selectStatement, name):
		'''
		given the prefix for project "prname" , check that it exists in the table projects
		'''
		self.sw1 = 0
		try:
#			selectStatement = "select prjPrefix from projects"
			pList = self.readSql(selectStatement)
			for each in pList:
				if (name == each):
					self.sw1 = 1
			return self.sw1
		except Exception, E:
			message = str(E)
			print message


	def getFileComponents(self, filename,p):
		return filename.split(p)[0],filename.split(p)[1],filename.split(p)[2],filename.split(p)[3],filename.split(p)[4],filename.split(p)[5],filename.split(p)[6]


	def is_project_folder_set(self,folderName):
		'''
		workspace set to project name and verified with table
		according to filename project should be set to corresponding project folder
		'''
		self.sw1 = 0
		try:
			workSpace = cmds.workspace(query=True,dir=True)
			if (workSpace == folderName):									# do a strict check
				self.sw1 = 1
			return self.sw1
		except Exception, E:
			self.message = "Set project folder. Error : " + str(E)
			onma.MGlobal().displayWarning(self.message)


	def is_folder_structure_proper(self, filePathName):
		'''
		folderName is extracted from full path filename
		'''
		self.sw1 = 1
		listF = []
		pList = []
		print 'filePathName : ',filePathName,'\n'
		fn1 = os.path.dirname(filePathName)														# come to level edits, minor, major, latest
		fct = os.path.dirname(fn1)
		print 'fn1 : ',fct ,'\n'
		listF = [ name for name in os.listdir(fct) if os.path.isdir(os.path.join(fct, name)) ]

		selectStatement = "select folderName from scenesfolder"
		pList = self.readSql(selectStatement)
		print 'pList ',pList,'\n'

		for every in pList:
			print "-",every
			self.sw1 = 0
			for each in listF:
				print "+",each
				if (every == each):
					print "equal"
					self.sw1 = 0	# switch used only to check a condition
					break
			if (self.sw1 == 0):
				print "sw1 == 1"
				continue
			elif (self.sw1 == 1):
				print "mkdir"
				os.mkdir(fct+ "/" +every)
		return self.sw1

	def send_path_to_table(self,machinename,fldrNm):
		'''
		send publish data to machinerecord table
		'''

		usrprx = None
		aId = None

		ft1 = "%s"
		ft2 = "%s"
		ft3 = "%s"
		ft4 = "%s"
#		field4nm = machinename
		try:
#			field1nm = "artistPrefix"
#			field2nm = "artists"
#			field3nm = "machName"		
#			usrprx = self.readSingleField( ft1, field1nm ,ft2, field2nm , ft3, field3nm , ft4, machinename )[0]

			field1nm = "rec_id"
			field2nm = "workstations"
			field3nm = "machName"
			aId = self.readSingleField( ft1, field1nm ,ft2, field2nm , ft3, field3nm , ft4, machinename )[0]

		except Exception, E:								# customize this error message
			message = str(E)
			print message
	
		pdata = "\\\\" + fldrNm.replace('D:',machinename).replace("/","\\\\")
		print 'pdata : ',pdata,'\n'
		print 'usrprx',usrprx,'\n'
		print 'machinename',machinename,'\n'

		data = "INSERT INTO files (artistId, machName, path ) VALUES (\"%s\",\"%s\",\"%s\")" %  (aId, machinename, pdata)
		print 'data  ',data ,'\n'

		if (self.sendSql(unicodedata.normalize('NFKD', data ).encode('ascii','ignore')) == 0):
			self.message = "statement %s incorrect. Check syntax" % (data)
			onma.MGlobal().displayInfo(self.message)


	def changeOptionMenu(self):
		'''
		with change in project sequence and shot are displayed according to project highlighted. Calls readSingleField
		'''
		print 'change option menu'
		ft1 = "%s"
		ft2 = "%s"
		ft3 = "%s"
		ft4 = "%s"
		field1nm = "rec_id"
		field2nm = "projects"
		field3nm = "prjName"
		field4nm = cmds.optionMenu(self.l1,query=True,value=True)								 #	 query first optionmenu
		print 'field4nm',field4nm,'\n'

#																								 #
		try:
			pid = self.readSingleField(ft1, field1nm ,ft2, field2nm, ft3, field3nm, ft4, field4nm )[0]
			print 'pid ',pid,'\n'
		except Exception, E:								# customize this error message
			message = str(E)
			print message

		print 'pid : type pid',pid,' : ',type(pid),'\n'

		ft1 = "%s"
		ft2 = "%s"
		ft3 = "%s"
		ft4 = "%d"

		field1nm = "scnName"
		field2nm = "scene"
		field3nm = "rec_id"
	#	field4nm is pid

		seqrec = self.readSingleField(ft1, field1nm ,ft2, field2nm, ft3, field3nm, ft4, int(pid) )
#		print 'seq based on pid  ',seqrec ,'\n'
#		cmds.deleteUI(self.l2,control=True)
#		self.l2 = cmds.optionMenu(label=' ',w=140)
#		cmds.formLayout(self.form, edit=True, attachControl=[(self.l1, 'top', 10, self.t1),(self.l2, 'top', 10, self.t1),(self.l3, 'top', 10, self.t1), (self.l4, 'top', 10, self.t1),(self.l5, 'top', 10, self.t1), (self.l6, 'top', 10, self.t1),(self.l7, 'top', 10, self.t1), (self.l2,'left', 10, self.l1),(self.l3,'left', 10, self.l2), (self.l4,'left', 10, self.l3), (self.l5,'left', 10, self.l4), (self.l6,'left', 10, self.l5), (self.l7,'left', 10, self.l6)])
		cmds.formLayout(self.form, edit=True, attachControl=[(self.l1, 'top', 10, self.t1),(self.l3, 'top', 10, self.t1), (self.l4, 'top', 10, self.t1),(self.l5, 'top', 10, self.t1), (self.l6, 'top', 10, self.t1),(self.l7, 'top', 10, self.t1), (self.l3,'left', 10, self.l1), (self.l4,'left', 10, self.l3), (self.l5,'left', 10, self.l4), (self.l6,'left', 10, self.l5), (self.l7,'left', 10, self.l6)])		
#		cmds.formLayout(form, edit=True, attachControl=[(l1, 'top', 10, t1),(l2, 'top', 10, t1),                              (l3, 'top', 10, t1),            (l4, 'top', 10, t1),         (l5, 'top', 10, t1),           (l6, 'top', 10, t1),          (l7, 'top', 10, t1),           (l2,'left', 10, l1),          (l3,'left', 10, l2),           (l4,'left', 10, l3),           (l5,'left', 10, l4),           (l6,'left', 10, l5),           (l7,'left', 10, l6)])
#		cmds.optionMenu(self.l2, edit=True,w=140)
#		for each in seqrec:
#			cmds.menuItem( label=each ,parent=self.l2)

		field1nm = "shotName"
		field2nm = "shots"
		field3nm = "rec_id"
#		field4nm is pid
		shorec = self.readSingleField(ft1, field1nm ,ft2, field2nm, ft3, field3nm, ft4, int(pid) )
		cmds.deleteUI(self.l3,control=True)
		self.l3 = cmds.optionMenu(label=' ',w=140)
#		cmds.formLayout(self.form, edit=True, attachControl=[(self.l1, 'top', 10, self.t1),(self.l2, 'top', 10, self.t1),(self.l3, 'top', 10, self.t1), (self.l4, 'top', 10, self.t1),(self.l5, 'top', 10, self.t1), (self.l6, 'top', 10, self.t1),(self.l7, 'top', 10, self.t1), (self.l2,'left', 10, self.l1),(self.l3,'left', 10, self.l2), (self.l4,'left', 10, self.l3), (self.l5,'left', 10, self.l4), (self.l6,'left', 10, self.l5), (self.l7,'left', 10, self.l6)])
		cmds.formLayout(self.form, edit=True, attachControl=[(self.l1, 'top', 10, self.t1),(self.l3, 'top', 10, self.t1), (self.l4, 'top', 10, self.t1),(self.l5, 'top', 10, self.t1), (self.l6, 'top', 10, self.t1),(self.l7, 'top', 10, self.t1), (self.l3,'left', 10, self.l1), (self.l4,'left', 10, self.l3), (self.l5,'left', 10, self.l4), (self.l6,'left', 10, self.l5), (self.l7,'left', 10, self.l6)])

		cmds.optionMenu(self.l3, edit=True,w=140)
		for each in shorec:
			cmds.menuItem( label=each  ,parent=self.l3)

	def ask_user_for_project_shot_other_details_once_then_save_file_in_format(self):
		'''

		'''
		self.form = cmds.setParent(q=True)

		cmds.formLayout(self.form, e=True, width=750)

#		t1 = cmds.text(l=' show 		  scn			 shNo		   description			   version			initials			  comments(optional)	 .extension')
		self.t1 = cmds.columnLayout()
		self.i1 = cmds.image( image='D:/test/versionsHeader.jpg')
		cmds.setParent('..')
		self.l1 = cmds.optionMenu(label=' ',w = 140, cc = 'onmi.changeOptionMenu()')
		showrec = self.readSql("select prjName from projects")
		for each in showrec:
			cmds.menuItem( label=each ,parent = self.l1)

#		self.l2 = cmds.optionMenu(label=' ',w = 140 )
#		cmds.menuItem( label=' ' ,parent = self.l2)

		self.l3 = cmds.optionMenu(label=' ', w = 140 )
		cmds.menuItem( label=' ' ,parent = self.l3)

		self.l4 = cmds.textField()
		self.l5 = cmds.textField()
		self.l6 = cmds.textField()
		self.l7 = cmds.textField()

		cmds.textField( self.l4, edit=True, width = 100, enterCommand=('cmds.setFocus(\"' + self.l7 + '\")') )
		cmds.textField( self.l5, edit=True, width = 30, enterCommand=('cmds.setFocus(\"' + self.l5 + '\")'),text='01',enable=False )
		cmds.textField( self.l6, edit=True, width = 30, enterCommand=('cmds.setFocus(\"' + self.l6 + '\")'),text=self.returnUserPrefix()[0] )
		cmds.textField( self.l7, edit=True, width = 70, enterCommand=('cmds.setFocus(\"' + self.l7 + '\")') )

		self.l8 = cmds.button(label = 'ok, create first scene file',c='onmi.computeFileName();onmi.saveFileName(onmi.minorFolderName,onmi.ffilename)')
		self.l9 = cmds.button(label = 'go ahead check in project folder')

		spacer = 5
		top = 5
		edge = 5

#		cmds.formLayout(self.form, edit=True, attachForm=[(self.t1, 'top', 0), (self.t1, 'left', 0),(self.l1,'left', 10),(self.l8,'left',30)], attachControl=[(self.l1, 'top', 10, self.t1),(self.l2, 'top', 10, self.t1),(self.l3, 'top', 10, self.t1), (self.l4, 'top', 10, self.t1),(self.l5, 'top', 10, self.t1), (self.l6, 'top', 10, self.t1),(self.l7, 'top', 10, self.t1), (self.l8,'top',10, self.l1), (self.l9,'top',10, self.l1),(self.l9,'left',20, self.l8), (self.l2,'left', 10, self.l1),(self.l3,'left', 10, self.l2), (self.l4,'left', 10, self.l3), (self.l5,'left', 10, self.l4), (self.l6,'left', 10, self.l5), (self.l7,'left', 10, self.l6)])
		cmds.formLayout(self.form, edit=True, attachForm=[(self.t1, 'top', 0), (self.t1, 'left', 0),(self.l1,'left', 10),(self.l8,'left',30)], attachControl=[(self.l1, 'top', 10, self.t1),(self.l3, 'top', 10, self.t1), (self.l4, 'top', 10, self.t1),(self.l5, 'top', 10, self.t1), (self.l6, 'top', 10, self.t1),(self.l7, 'top', 10, self.t1), (self.l8,'top',10, self.l1), (self.l9,'top',10, self.l1),(self.l9,'left',20, self.l8), (self.l3,'left', 10, self.l1), (self.l4,'left', 10, self.l3), (self.l5,'left', 10, self.l4), (self.l6,'left', 10, self.l5), (self.l7,'left', 10, self.l6)])

#	print cmds.layoutDialog(ui=ask_user_for_project_shot_other_details_once_then_save_file_in_format)

	def save_file_in_minor_folder(self, lfn):
		'''
		get last version from minor folder for this fileName.
		#		get count of files with same name
		'''
		lvv = ""
		single09 = r'''^[0-9]{1}$'''
		double09 = r'''_v[0-9]{2}'''
		fileName = os.path.basename(lfn)
		folderName = os.path.dirname(lfn)
		print 'save_file_in_minor_folder fileName ',fileName ,'\n'
		print 'folderName : ',folderName,'\n'
		list_From_glv = self.get_last_version(fileName , folderName)
		print 'list_From_glv : ',list_From_glv,'\n'
		unlv = str(int(unicodedata.normalize('NFKD', list_From_glv[0]).encode('ascii','ignore')))

		if re.match(single09, unlv):
			if not (int(unlv) == 9):
				lvv = "0" + str(int(unlv) + 1)
			else:
				lvv = str(int(unlv) + 1)
			print 'single09 ',lvv
		else:
			lvv = str(int(unlv) + 1)
		print 'lvv',lvv,'\n'

		cof = list_From_glv[1]

		ffn =  unicodedata.normalize('NFKD', list_From_glv[2]).encode('ascii','ignore')

		vn = re.search(double09 ,fileName)													# to extract for new file name
#		vn = re.search("_v"+list_From_glv[0] ,fileName)			

		nFileName = fileName[:vn.start()] + "_v" + lvv + fileName[vn.end():]
		print 'nFileName ',nFileName ,'\n'
		if (cof >= 5):
			#shutil.rmtree( os.path.join(folderName,ffn) )
			os.chmod(os.path.join(folderName,ffn), stat.S_IWRITE)
			os.remove(os.path.join(folderName,ffn))
#																										delete first file with same name
		return nFileName

	def get_last_version(self, fileName , folderName):
		'''
		return count of files with same name
		return last file version number
		'''
		lff = []
		print 'get_last_version fileName ',fileName ,'\n'
#		fileName = os.path.basename(lfn)
#		folderName = os.path.dirname(lfn)
		aaa = fileName.split("_")[0]+"_"+fileName.split("_")[1]+"_"+fileName.split("_")[2]
		for root, dirs, files in os.walk(folderName):
			for file in files:
				if (re.search(aaa+"\B",file )):
					lff.append(file)
		print lff
		return (self.chew_version_from_filename(lff[len(lff)-1]),len(lff),lff[0])

	def computeFileName(self):
		'''
		from user prompted selection return file name
		'''

		self.sw1 = 1
		l1c = cmds.optionMenu(self.l1,query=True,value=True)
#		l2c = cmds.optionMenu(self.l2,query=True,value=True)
		l3c = cmds.optionMenu(self.l3,query=True,value=True)

		l4c = cmds.textField(self.l4,query=True,text=True)
		if not l4c:
			print 'empty'
			self.sw1 = 0
		else:
			print 'l4c ',l4c ,'\n'
		l5c = cmds.textField(self.l5,query=True,text=True)
		l6c = cmds.textField(self.l6,query=True,text=True)
		l7c = cmds.textField(self.l7,query=True,text=True)
		if not l7c:
			print 'empty'
			self.sw1 = 0
		else:
			print 'l7c ',l7c ,'\n'

	# compute file name
	#	get prefix of project, seq, shot
	#
		if (self.sw1 == 1):
#			print 'in self.sw1 1'
			ft1 = "%s"
			ft2 = "%s"
			ft3 = "%s"
			ft4 = "%s"

			field1nm = "prjPrefix"
			field2nm = "projects"
			field3nm = "prjName"
		#	 field4nm = l1c

			fn1 = self.readSingleField(ft1, field1nm ,ft2, field2nm, ft3, field3nm, ft4, l1c )
			if fn1:
#				print 'in self.sw1 3'
				ft1 = "%s"
				ft2 = "%s"
				ft3 = "%s"
				ft4 = "%s"

				field1nm = "shPrefix"
				field2nm = "shots"
				field3nm = "shotName"
#				field4nm = l3c

				fn3 = self.readSingleField(ft1, field1nm ,ft2, field2nm, ft3, field3nm, ft4, l3c )
				print 'fn3 : ',type(fn3)
				if fn3:
#					print 'in self.sw1 4',type(fn1[0]),type(fn2[0]),'\n'
#					self.ffilename = fn1[0] + self.underscore + fn2[0] + self.underscore + fn3[0] + self.underscore + l4c + self.underscore + "v" + l5c + self.underscore + l6c + self.underscore + l7c + self.dot + self.filext
					self.ffilename = fn1[0] + self.underscore + fn3[0] + self.underscore + l4c + self.underscore + "v" + l5c + self.underscore + l6c + self.underscore + l7c + self.dot + self.filext
					print 'self.ffilename : ',self.ffilename,'\n'
		else:
			print 'error message'

#		cmds.deleteUI( self.form, window=True )
		cmds.layoutDialog( dismiss = 'close' )

	def writeFileName(self,fn):
		'''
		save file name
		'''
		cmds.file( rename=fn)
		cmds.file( save=True, type='mayaAscii' )


	def authenticatesql(self, host, user, pwss, dbnm):
		'''
		connect to sql once at the beginning of the script
		'''
		try:
#			self.DB = sqlite.connect( self.dbFilePath )
			self.db = mdb.connect(host=host,user=user,passwd=pwss,db=dbnm)
			return 1
		except Exception, E:
			message = str(E)
			print message
			return 0


	def readSingleField( self, ft1, field1nm ,ft2, field2nm , ft3, field3nm , ft4, field4nm ):
		'''
		return sql query record
		'''
		q1 = ("select " + ft1 + " from " + ft2 + " where " + ft3 + " = \"" + ft4 + "\"")
		q2 = q1 % ( field1nm , field2nm ,  field3nm , field4nm )
		print 'q2 : ',q2,'\n'
		return self.readSql(q2)

	def readSql(self,que):
		'''
		return sql query record
		'''
		relist = []
		with self.db:
			try:
				cur = self.db.cursor()
				cur.execute(que)
				rows = cur.fetchall()
	#			 emaillist = "\n".join(item[0] for item in queryresult)
				for row in rows:
					print type(row[0])
					relist.append(row[0])
				return relist
			except Exception, E:
				message = str(E)
				print message
				return 0

	def sendSql(self, data):
		'''
		insert record in sql table
		'''
		self.sw1 = 0
		dbcursor = self.db.cursor()
		try:
			dbcursor.execute(data)
			self.db.commit()
			self.sw1 = 1
			return self.sw1
		except Exception, E:
			self.message = str(E)
			print self.message

	def chew_version_from_filename(self, fileName):
		'''
		extract version number from filename with naming convention
		'''
		print fileName
		ex = re.findall("v\d+",fileName)															# extract version number
		return filter(lambda x: x.isdigit(), ex[0])


	def returnUserPrefix(self):
		'''
		used in function ask_user_for_project_shot_other_details_once_then_save_file_in_format to fill user prefix text
		'''
		ft1 = "%s"
		ft2 = "%s"
		ft3 = "%s"
		ft4 = "%s"

		field1nm = "artistPrefix"
		field2nm = "artists"
		field3nm = "machName"
#		field4nm = "n.solanki"					# change it after all testing is done
		field4nm = platform.node()

		uprf = self.readSingleField(ft1, field1nm ,ft2, field2nm, ft3, field3nm, ft4, field4nm )
		print 'uprf',uprf,'\n'
		return uprf

	def saveFileName(self, fldrNm, fflnm):
		'''
		# fflnm holds first file name
		# fldrNm holds workspace + "scenes/minor"
		'''
		fPName = ""

		if not (fflnm == ""):
			'''
			if filename is empty then presuming user has set project just saving file itself is enough
			'''
			fPName = os.path.join(fldrNm , fflnm).replace("\\","/")
#			self.writeFileName(fPName)
		else:																					# filename already present
			nFName = self.save_file_in_minor_folder(self.returnLongFileName())
			fPName = os.path.join(fldrNm , nFName).replace("\\","/")
		print 'fPName : ',fPName,'\n'
		self.writeFileName(fPName)
		
	def returnProjectType(self,prjNm):
		ft1 = "%s"
		ft2 = "%s"
		ft3 = "%s"
		ft4 = "%s"

		field1nm = "prjType"
		field2nm = "projects"
		field3nm = "prjName"
#			field4nm = prjNm

		fn3 = self.readSingleField(ft1, field1nm ,ft2, field2nm, ft3, field3nm, ft4, prjNm )
		print 'fn3 : ',type(fn3)
		if not fn3:
			self.message = "Check database. looks like some records are missing"
			onma.MGlobal().error(self.message)
		return fn3
		
			

	def copy_To_Latest(self):
		regexp = r'''_v\d{2}'''
		self.latestFolderName = cmds.workspace(query=1,act=1) + "/scenes/latest/"
		fn = self.returnFileName().split(".")[0]
		vn = re.search(regexp ,fn)
		nFileName = fn[:vn.start()] + fn[vn.end():] + "_latest"
		print 'nFileName',nFileName,'\n'
		print 'self.latestFolderName',self.latestFolderName,'\n'
		try:
			shutil.copyfile(self.returnLongFileName(), self.latestFolderName + nFileName + "." + self.returnFileName().split(".")[1] )
			self.message = "%s file copied to %s folder" % (nFileName, self.latestFolderName)
			onma.MGlobal().displayInfo(self.message)
			
		except Exception, E:
			self.message = str(E)
			print self.message


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
