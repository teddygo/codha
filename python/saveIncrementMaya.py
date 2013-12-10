'''
#	for long format (movies)
#	show_scn_shNo_description_version_initials_comments(optional).extension

#	for commercials
#	show_shNo_description_version_initials_comments(optional).extension

#	check that project is set to local folder

# 1 = ok
# 0 = not ok

#\\white\projects\lakme\maya2011\shotno\mayafolderstructure\
									   \scenes\minor
											 \major
											 \latest
# comments start in column 72
# acknowledgements : Thomas Wouters for line
# presumption at present : user sets project when starting maya session
# presumption at present : user works from minor folder
'''

'''
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

class minor():
	def __init__(self):
		self.sqlConnected = 0
		self.errorMessage = ""
		self.sw1 = 0
		self.fileformat_1 = "show_scn_shNo_description_v(XXX)_ini_comments(optional).extension"
		self.fileformat_2 = "show_shNo_description_v(XXX)_ini_comments(optional).extension"
		self.l1 = ""
		self.l2 = ""
		self.l3 = ""
		self.t1 = ""
		self.l4 = ""
		self.l5 = ""
		self.l6 = ""
		self.l7 = ""
#		self.form = ""

		self.host = "localhost"
		self.user = "root"
		self.pwss = ""
		self.dbnm = "testmysql"
		self.underscore = "_"
		self.filext = "ma" # this can be passed as parameter
		self.dot = "."
		self.ffilename = ""

	def returnFileName(self):
		return cmds.file(query=True,shn=True,sn=True)

	def returnLongFileName(self):
		return cmds.file(query=True,sn=True)

	def isfileNameEmpty(self):
		self.sw1 = 0
		if (self.returnFileName() == ""):
			self.sw1 = 1
		return self.sw1
		

	def isfileNameConventionPresent(self,filename):
		'''
		# check the file name matched convention
		# xxx_xxx_xxx_vxxx_xxx.ma
		# show_scn_shNo_description_version_initials_comments(optional).extension
		# strict match
		#self.sw1 = 0 ok
		#1 not ok
		'''
		self.sw1 = 0
		regexp = r'''\b\w{3}_\w{6}_\w{2}\d{3}_[a-zA-Z]+_v\d{1,2}_[a-z]{3}_[a-zA-Z0-9]+.ma|\b\w{3}_\w{2}\d{3}_[a-zA-Z]+_v\d{1,2}_[a-z]{3}_[a-zA-Z0-9]+.ma'''

		if not re.match(regexp , filename):
			self.sw1 = 1
			self.errorMessage = "file name not matching. contact admin for help"
			print self.errorMessage
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
			field3nm = "prefix"
	#		field4nm = prjprx
			prtype = self.readSingleField(ft1, field1nm ,ft2, field2nm, ft3, field3nm, ft4, prjprx )[0]
			if (self.verifyShowName(prjprx) and self.verifyShotName(seqprx)):		
				if (prtype == 'm'):
					if (self.verifySequenceName(shtprx)):
						self.sw1 = 1
				else:
					self.sw1 = 1
			return self.sw1
		except Exception, E:
			message = str(E)
			print message

	def verifyShowName(self,prname):
		'''
		given the prefix for project "prname" , check that it exists in the table projects
		'''
		self.sw1 = 0
		try:
			selectStatement = "select prefix from projects"
			pList = self.readSql(selectStatement)
			for each in pList:
				if (prname == each):
					self.sw1 = 1
			return self.sw1
		except Exception, E:
			message = str(E)
			print message


	def verifySequenceName(self,scname):
		'''
		given the prefix for sequence scname , check that it exists in the table projects
		'''
		self.sw1 = 0
		try:
			selectStatement = "select prefix from seq"
			pList = self.readSql(selectStatement)
			for each in pList:
				if (scname == each):
					self.sw1 = 1
			return self.sw1
		except Exception, E:
			message = str(E)
			print message
			
		
	def verifyShotName(self,shname):
		'''
		given the prefix for sequence scname , check that it exists in the table projects
		'''
		self.sw1 = 0
		try:
			selectStatement = "select prefix from shots"
			pList = self.readSql(selectStatement)
			for each in pList:
				if (shname == each):
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
			self.errorMessage = "Set project folder. Error : " + str(E)
			print self.errorMessage

			
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

		selectStatement = "select folder_name from scenes_folder"
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
		sqlText = "select prefix from eq_users where machine_name = \"%s\"" % machinename
#		usrprx = self.readSql(sqlText)

		ft1 = "%s"
		ft2 = "%s"
		ft3 = "%s"
		ft4 = "%s"
		field1nm = "prefix"
		field2nm = "eq_users"
		field3nm = "machine_name"
#		field4nm = machinename

		usrprx = self.readSingleField( ft1, field1nm ,ft2, field2nm , ft3, field3nm , ft4, machinename )[0]
		pdata = "\\\\" + fldrNm.replace('D:',machinename).replace("/","\\\\")
		data = "INSERT INTO machinerecord (machinename, usrprx, publishdata ) VALUES (\"%s\",\"%s\",\"%s\")" %  (machinename,usrprx,pdata)
		print 'data  ',data ,'\n'

		if (self.sendSql(unicodedata.normalize('NFKD', data ).encode('ascii','ignore')) == 0):
			self.errorMessage = "statement %s incorrect. Check syntax" % (data)
			print self.errorMessage

	def changeOptionMenu(self):

		print 'change option menu'
		ft1 = "%s"
		ft2 = "%s"
		ft3 = "%s"
		ft4 = "%s"
		field1nm = "project_id"
		field2nm = "projects"
		field3nm = "project_name"
		field4nm = cmds.optionMenu(self.l1,query=True,value=True)								 #	 query first optionmenu
	
#																								 #
		pid = self.readSingleField(ft1, field1nm ,ft2, field2nm, ft3, field3nm, ft4, field4nm )[0]
		print 'pid : type pid',pid,' : ',type(pid),'\n'

		ft1 = "%s"
		ft2 = "%s"
		ft3 = "%s"
		ft4 = "%d"

		field1nm = "sq_name"
		field2nm = "seq"
		field3nm = "project_id"
	#	field4nm is pid

		seqrec = self.readSingleField(ft1, field1nm ,ft2, field2nm, ft3, field3nm, ft4, int(pid) )
		print 'seq based on pid  ',seqrec ,'\n'
		cmds.deleteUI(self.l2,control=True)
		self.l2 = cmds.optionMenu(label=' ',w=140)
		cmds.formLayout(self.form, edit=True, attachControl=[(self.l1, 'top', 10, self.t1),(self.l2, 'top', 10, self.t1),(self.l3, 'top', 10, self.t1), (self.l4, 'top', 10, self.t1),(self.l5, 'top', 10, self.t1), (self.l6, 'top', 10, self.t1),(self.l7, 'top', 10, self.t1), (self.l2,'left', 10, self.l1),(self.l3,'left', 10, self.l2), (self.l4,'left', 10, self.l3), (self.l5,'left', 10, self.l4), (self.l6,'left', 10, self.l5), (self.l7,'left', 10, self.l6)])
#		cmds.formLayout(form, edit=True, attachControl=[(l1, 'top', 10, t1),(l2, 'top', 10, t1),                              (l3, 'top', 10, t1),            (l4, 'top', 10, t1),         (l5, 'top', 10, t1),           (l6, 'top', 10, t1),          (l7, 'top', 10, t1),           (l2,'left', 10, l1),          (l3,'left', 10, l2),           (l4,'left', 10, l3),           (l5,'left', 10, l4),           (l6,'left', 10, l5),           (l7,'left', 10, l6)])
		cmds.optionMenu(self.l2, edit=True,w=140)
		for each in seqrec:
			cmds.menuItem( label=each ,parent=self.l2)
	
		field1nm = "shot_name"
		field2nm = "shots"
		field3nm = "project_id"
	#	field4nm is pid
		shorec = self.readSingleField(ft1, field1nm ,ft2, field2nm, ft3, field3nm, ft4, int(pid) )
		cmds.deleteUI(self.l3,control=True)
		self.l3 = cmds.optionMenu(label=' ',w=140)
		cmds.formLayout(self.form, edit=True, attachControl=[(self.l1, 'top', 10, self.t1),(self.l2, 'top', 10, self.t1),(self.l3, 'top', 10, self.t1), (self.l4, 'top', 10, self.t1),(self.l5, 'top', 10, self.t1), (self.l6, 'top', 10, self.t1),(self.l7, 'top', 10, self.t1), (self.l2,'left', 10, self.l1),(self.l3,'left', 10, self.l2), (self.l4,'left', 10, self.l3), (self.l5,'left', 10, self.l4), (self.l6,'left', 10, self.l5), (self.l7,'left', 10, self.l6)])

		cmds.optionMenu(self.l3, edit=True,w=140)
		for each in shorec:
			cmds.menuItem( label=each  ,parent=self.l3)

	def ask_user_for_project_shot_other_details_once_then_save_file_in_format(self):
		'''
		Not yet implemented : check if filename entered thru this window already exists
		'''
		self.form = cmds.setParent(q=True)

		cmds.formLayout(self.form, e=True, width=750)

#		t1 = cmds.text(l=' show 		  scn			 shNo		   description			   version			initials			  comments(optional)	 .extension')
		self.t1 = cmds.columnLayout()
		self.i1 = cmds.image( image='D:/test/versionsHeader.jpg')
		cmds.setParent('..')
		self.l1 = cmds.optionMenu(label=' ',w = 140, cc = 'onmi.changeOptionMenu()')
		showrec = self.readSql("select project_name from projects")
		for each in showrec:
			cmds.menuItem( label=each ,parent = self.l1)
	
		self.l2 = cmds.optionMenu(label=' ',w = 140 )
		cmds.menuItem( label=' ' ,parent = self.l2)
#		cmds.setParent( '..', menu=True )			 
		self.l3 = cmds.optionMenu(label=' ', w = 140 )
		cmds.menuItem( label=' ' ,parent = self.l3)

		self.l4 = cmds.textField()
		self.l5 = cmds.textField()
		self.l6 = cmds.textField()
		self.l7 = cmds.textField()

		cmds.textField( self.l4, edit=True, width = 100, enterCommand=('cmds.setFocus(\"' + self.l4 + '\")') )
		cmds.textField( self.l5, edit=True, width = 30, enterCommand=('cmds.setFocus(\"' + self.l5 + '\")'),text='01',enable=False )
		cmds.textField( self.l6, edit=True, width = 30, enterCommand=('cmds.setFocus(\"' + self.l6 + '\")'),text=onmi.returnUserPrefix()[0],enable=False )
		cmds.textField( self.l7, edit=True, width = 70, enterCommand=('cmds.setFocus(\"' + self.l7 + '\")') )

		self.l8 = cmds.button(label = 'ok, create first scene file',c='onmi.computeFileName();onmi.bbbb(onmi.folderName)')
		self.l9 = cmds.button(label = 'go ahead and check in project folder and then add')

		spacer = 5
		top = 5
		edge = 5

		cmds.formLayout(self.form, edit=True, attachForm=[(self.t1, 'top', 0), (self.t1, 'left', 0),(self.l1,'left', 10),(self.l8,'left',30)], attachControl=[(self.l1, 'top', 10, self.t1),(self.l2, 'top', 10, self.t1),(self.l3, 'top', 10, self.t1), (self.l4, 'top', 10, self.t1),(self.l5, 'top', 10, self.t1), (self.l6, 'top', 10, self.t1),(self.l7, 'top', 10, self.t1), (self.l8,'top',10, self.l1), (self.l9,'top',10, self.l1),(self.l9,'left',20, self.l8), (self.l2,'left', 10, self.l1),(self.l3,'left', 10, self.l2), (self.l4,'left', 10, self.l3), (self.l5,'left', 10, self.l4), (self.l6,'left', 10, self.l5), (self.l7,'left', 10, self.l6)])

#	print cmds.layoutDialog(ui=ask_user_for_project_shot_other_details_once_then_save_file_in_format)

	def save_file_in_minor_folder(self, lfn):
		'''
		get last version from minor folder for this fileName.
		#		get count of files with same name
		'''
		lvv = ""		
		single09 = r'''^[0-9]{1}$'''
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

		vn = re.search("_v"+list_From_glv[0] ,fileName)

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
#		global l1,l2,l3,t1,l4,l5,l6,l7,form
		self.sw1 = 1
		l1c = cmds.optionMenu(self.l1,query=True,value=True)
		l2c = cmds.optionMenu(self.l2,query=True,value=True)
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
		
			field1nm = "prefix"
			field2nm = "projects"
			field3nm = "project_name"
		#	 field4nm = l1c
			
			fn1 = self.readSingleField(ft1, field1nm ,ft2, field2nm, ft3, field3nm, ft4, l1c )
			if fn1:
#				print 'in self.sw1 2'
				ft1 = "%s"
				ft2 = "%s"
				ft3 = "%s"
				ft4 = "%s"
			
				field1nm = "prefix"
				field2nm = "seq"
				field3nm = "sq_name"
		#		field4nm = l2c
				
				fn2 = self.readSingleField(ft1, field1nm ,ft2, field2nm, ft3, field3nm, ft4, l2c )
				if fn2:
#					print 'in self.sw1 3'
					ft1 = "%s"
					ft2 = "%s"
					ft3 = "%s"
					ft4 = "%s"
				
					field1nm = "prefix"
					field2nm = "shots"
					field3nm = "shot_name"
			#		field4nm = l3c

					fn3 = self.readSingleField(ft1, field1nm ,ft2, field2nm, ft3, field3nm, ft4, l3c )
					print 'fn3 : ',type(fn3)
					if fn3:
#						print 'in self.sw1 4',type(fn1[0]),type(fn2[0]),'\n'
						self.ffilename = fn1[0] + self.underscore + fn2[0] + self.underscore + fn3[0] + self.underscore + l4c + self.underscore + "v" + l5c + self.underscore + l6c + self.underscore + l7c + self.dot + self.filext
						print 'self.ffilename : ',self.ffilename,'\n'

		else:
			print 'error message'
			
#		cmds.deleteUI( self.form, window=True )


	def saveFileName(self,fn):
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
		q1 = ("select " + ft1 + " from " + ft2 + " where " + ft3 + " = \"" + ft4 + "\"")
		q2 = q1 % ( field1nm , field2nm ,  field3nm , field4nm )
		print 'q2 : ',q2,'\n'
		return self.readSql(q2)

	def readSql(self,que):
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
		self.sw1 = 0
		dbcursor = self.db.cursor()
		try:
			dbcursor.execute(data)
			db.commit()
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

	def getProjectType(self,pN):# redundant
		'''
		obsolete : use readsinglefield
		'''
		return self.readSql("select prjType from projects where project_name = \"%s\"" % pN)[0]

	def returnUserPrefix(self):
		'''
		used in function ask_user_for_project_shot_other_details_once_then_save_file_in_format to fill user prefix text
		'''
		ft1 = "%s"
		ft2 = "%s"
		ft3 = "%s"
		ft4 = "%s"

		field1nm = "prefix"
		field2nm = "eq_users"
		field3nm = "login_id"
		field4nm = "n.solanki"

		uprf = self.readSingleField(ft1, field1nm ,ft2, field2nm, ft3, field3nm, ft4, field4nm )
		return uprf

	def bbbb(self, fldrNm):
		'''
		# ffilename holds first file name
		'''
		fPName = ""

		if not (self.ffilename == ""):
			'''
			if filename is empty then presuming user has set project just saving file itself is enough
			'''
			fPName = os.path.join(fldrNm , self.ffilename).replace("\\","/")
			print 'fPName : ',fPName,'\n'
			self.saveFileName(fPName)
		else:																					# filename already present

			nFName = self.save_file_in_minor_folder(self.returnLongFileName())
			self.saveFileName(os.path.join(fldrNm , nFName).replace("\\","/"))


	def __main__(self):
		'''
		this is engine. Where all functions get called in a manner.
		'''

		self.folderName = cmds.workspace(query=1,act=1) + "/scenes/minor/"
		print 'self.folderName',self.folderName,'\n'
		if (self.authenticatesql(self.host, self.user, self.pwss, self.dbnm) == 1):				# make connection to database
			if	(self.isfileNameEmpty() == 1):													# file name not present 
#				self.ask_user_for_project_shot_other_details_once_then_save_file_in_format()
				print cmds.layoutDialog(ui=onmi.ask_user_for_project_shot_other_details_once_then_save_file_in_format)
			elif	(self.isfileNameConventionPresent(self.returnFileName()) == 1):				# file name convention not existing
				message = ("\n" + (self.underscore*40) + "\n\tValid format :\n%s for a movie \nor\n%s for a commercial \nUse save to change to above matching format " + "\n" + (self.underscore*40)) % (self.fileformat_1 ,self.fileformat_2 )
				print message
			elif (self.is_folder_structure_proper(self.folderName) == 1):
				message = "Check Folder structure. Save File in folder %s " % (self.folderName)
				print message
			else:
				self.bbbb(self.folderName)
				self.send_path_to_table(platform.node(),self.folderName)
		else:
			message = "connection not made. connect to admin "
			print message

onmi = minor()
onmi.__main__()
