#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################
#
#Copyright 2012  Futureworks Studio
#
#Permission to use, copy, modify, and distribute this software
#and its documentation for any purpose and without fee is hereby
#granted, provided that the above copyright notice appear in all
#copies and that both that the copyright notice and this
#permission notice and warranty disclaimer appear in supporting
#documentation, and that the name of the author not be used in
#advertising or publicity pertaining to distribution of the
#software without specific, written prior permission.
#
#The author disclaim all warranties with regard to this
#script, including all implied warranties of merchantability
#and fitness.  In no event shall the author be liable for any
#special, indirect or consequential damages or any damages
#whatsoever resulting from loss of use, data or profits, whether
#in an action of contract, negligence or other tortious action,
#arising out of or in connection with the use or performance of
#this software.
#
#   Author:     Futureworks
#   Version:    1.0
#
#   Description:
#	A quicktime (part 2 ) generator from ready image sequence. User is 
#	prompted to this path. "First_part_of_image_sequence".mov is created 
#	in same folder
#
#	switch use 1 if works, 0 if does not work
#	variable names selected randomly
#	This script is as loosely coupled as possible. There can be more scope
#	of it being as would be seen as design pattern

import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import os,subprocess, re
import random
import tempfile
from types import *
import shutil
import unicodedata
import time
import ctypes

class makeQuicktime(object):

	def __init__(self):

		self.fileExtension = ""
		self.backgroundImage = ""
		self.thumbnailImage = ""
		self.firstImage = ""
		self.tempFolder = ""
		self.symlinkFolder = ""
		self.oneImage = ""
		self.myTemp = ""
# variables from scene file and user
		self.elementName = ""
		self.qeName = ""
		self.date = ""
		self.imageSequence = ""
		self.lens = ""
		self.frameRange = ""
		self.notes = ""
		self.qnotes = ""
		self.currentFrame = ""
		self.imageregex = ""
		
		self.exepath = "D:/mayaslate/"
		self.ffmpeg = "ffmpeg.exe"
		self.composite = "composite.exe"
		self.dll = "vcomp100.dll"
		self.kerneldll = "kernel32.dll"

	def thirdpartyapp(self):
		"""
			D:/mayaslate/ has 3 executables. if any is missing admin will put it
		"""
		if not os.path.isfile(os.path.join (self.exepath ,self.ffmpeg)):
			OpenMaya.MGlobal.displayError("% app not present") % self.ffmpeg
		if not os.path.isfile(os.path.join (self.exepath ,self.composite)):
			OpenMaya.MGlobal.displayError("% app not present") % self.composite
		if not os.path.isfile(os.path.join (self.exepath ,self.dll)):
			OpenMaya.MGlobal.displayError("% app not present") % self.dll


	def setImageRegex(self,imageCountVar):																																	# check length of imageCountVar
		"""
		@setImageRegex: padding image count.
		"""	
		if (len(imageCountVar) == 5):
			irx = "%05d"
		elif (len(imageCountVar) == 4):
			irx = "%04d"
		elif (len(imageCountVar) == 3):
			irx =  "%03d"
		elif (len(imageCountVar) == 2):
			irx = "%02d"
		elif (len(imageCountVar) == 1):
			irx = "%01d"
		return irx

	def firstImageCount(self,listOfFiles):
		""" 
		file list : @listOfFiles , parameter passed
		firstImageCount, returns what should be number on first image
		
		"""	
		whisper = ""
#		nc = unicodedata.normalize('NFKD', listOfFiles[0].split('.')[1]).encode('ascii','ignore')
		nc = listOfFiles[0].split('.')[1]
		ic = str(int(nc) - 1)

		if ((len(nc) - len(ic)) == 0):
			whisper = ""
		elif ((len(nc) - len(ic)) == 1):
			whisper = "0"
		elif ((len(nc) - len(ic)) == 2):
			whisper = "00"
		elif ((len(nc) - len(ic)) == 3):
			whisper = "000"

		return (whisper + ic)

	def cleanDirectory(self,dName):
		for filen in os.listdir(dName):
			os.remove(dName.replace("\\","/") +"/"+filen)
		
	def makeTempFolder(self, fName):
		print 'fName : ',fName,'\n'
#		check tmp folder exst , if not flag message exit
#		sysTemp = tempfile.gettempdir().replace("\\","/")																													# get temp folder name
		sysTemp = "D:/mayaslate"																																			# get temp folder name
		if not os.path.exists(sysTemp):
			os.makedirs(sysTemp)
			mesg = "% now created " % (sysTemp)
			OpenMaya.MGlobal.displayInfo(mesg)
			return 1
		else:
			self.myTemp = os.path.join(sysTemp,fName).replace("\\","/")
			if not os.path.exists(self.myTemp):																																# if already exists then clear it else create it
				os.makedirs(self.myTemp)
				print 'self.tempFolder : ',self.tempFolder,'\n'
			else:
				self.cleanDirectory(self.myTemp)
			self.tempFolder = self.myTemp				
			return 0		

	def selectFolder( self, folderName, fileType):
		fName = unicodedata.normalize('NFKD', folderName).encode('ascii','ignore')
		if os.path.isdir(fName):
#			self.tempFolder = tempfile.gettempdir().replace("\\","/")																									# get temp folder name
			self.tempFolder = "D:/mayaslate"																																			# get temp folder name			
			self.symlinkFolder = self.tempFolder + "/symlink/"																											# create symlink folder within temp folder
			if not os.path.isdir(self.symlinkFolder):
				os.mkdir(self.symlinkFolder)
			print '%TEMP%',self.tempFolder,'\n'
#			for thumbnail
			temp_01 = os.listdir(fName)																															# get file name from user folder
			print 'temp_01 ',temp_01 ,'\n'
			sampleFileName = temp_01[random.randint(1,len(temp_01)-1)]																									# select random image

#			fpof = unicodedata.normalize('NFKD', (sampleFileName.split('.')[0])).encode('ascii','ignore')
			fpof = sampleFileName.split('.')[0]
			print 'fpof ',fpof ,'\n'
			retVal = self.makeTempFolder(sampleFileName.split(".")[0])																									# make folder with file name in %TEMP%			
			if (retVal == 0):
#				self.fileExtension = unicodedata.normalize('NFKD', sampleFileName.split('.')[2]).encode('ascii','ignore')
				self.fileExtension = sampleFileName.split('.')[2]
				print 'self.fileExtension : ',self.fileExtension,'\n'
	
				self.backgroundImage = self.tempFolder + "/background.jpg"

				self.thumbnailImage = self.tempFolder + "/thumbnail." + self.fileExtension

				temp_02 = fName + "/" + sampleFileName

				args = ["composite", "-compose", "Clear", "null:", temp_02, "-alpha", "Off", self.backgroundImage]

				process = subprocess.Popen(args,stdout=subprocess.PIPE)
				ret = process.wait()
				if (ret == 0):

					args = ["ffmpeg", "-i", temp_02 ,"-vf", "scale=iw/3.5:ih/3.5", "-frames:v", "1", self.thumbnailImage]

					process = subprocess.Popen(args, stdout=subprocess.PIPE)
					ret = process.wait()
					if (ret == 0):
						print 'mate'

						self.firstImage = self.tempFolder + "/firstImage." + self.fileExtension
						self.thumbnailImage = self.thumbnailImage.replace(':', '\:')
	
						temp_03 = "movie='%s' [watermark]; [in][watermark] overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/3 [out]" % self.thumbnailImage
						args = ["ffmpeg", "-i", self.backgroundImage , "-vf", temp_03 , self.firstImage]
	
						process = subprocess.Popen(args, stdout=subprocess.PIPE)
						ret = process.wait()
	
						if (ret == 0):

							print 'pen penultimate'
							oldid = os.listdir(fName)

							if not isinstance(oldid,NoneType):

								fiC = self.firstImageCount(oldid)
								self.oneImage = fName + "/" + fpof + "." + fiC + "." + self.fileExtension
								print 'self.oneImage : ',self.oneImage ,'\n'
#								elementname and notes are gotten from user
								self.date = (time.strftime("%d"+"\/ "+"%m"+"\/ "+"%Y"+" \- "+"%H"+"\:"+"%M"+"\:"+"%S"))
								self.imageSequence = fpof

								self.lens = str(int(cmds.getAttr('shotcamShape.focalLength')))																										# get from globals
								self.frameRange = (str(int(cmds.getAttr('defaultRenderGlobals.startFrame'))) + " - " + str(int(cmds.getAttr('defaultRenderGlobals.endFrame'))))							# get from globals

								args = ["ffmpeg", "-i", self.firstImage, "-vf", "[in]drawtext=fontsize=32:fontcolor=White:fontfile='C\:/Windows/Fonts/arial.ttf':text='shotName':x=(w)/2:y=(h)-50,drawtext=fontsize=28:fontcolor=White:fontfile='C\:/Windows/Fonts/arial.ttf':text='Notes \:':x=(w)/5:y=(h)-90,drawtext=fontsize=28:fontcolor=White:fontfile='C\:/Windows/Fonts/arial.ttf':text='"+ self.qnotes +"':x=((w)/5)+250:y=(h)-90,drawtext=fontsize=28:fontcolor=White:fontfile='C\:/Windows/Fonts/arial.ttf':text='Frame Range \:':x=(w)/5:y=(h)-130,drawtext=fontsize=28:fontcolor=White:fontfile='C\:/Windows/Fonts/arial.ttf':text='"+ self.frameRange +"':x=((w)/5)+250:y=(h)-130,drawtext=fontsize=28:fontcolor=White:fontfile='C\:/Windows/Fonts/arial.ttf':text='Lens \:':x=(w)/5:y=(h)-170,drawtext=fontsize=28:fontcolor=White:fontfile='C\:/Windows/Fonts/arial.ttf':text='"+ self.lens +"':x=((w)/5)+250:y=(h)-170,drawtext=fontsize=28:fontcolor=White:fontfile='C\:/Windows/Fonts/arial.ttf':text='Image Sequence \:':x=(w)/5:y=(h)-210,drawtext=fontsize=28:fontcolor=White:fontfile='C\:/Windows/Fonts/arial.ttf':text='"+ self.imageSequence +"':x=((w)/5)+250:y=(h)-210,drawtext=fontsize=28:fontcolor=White:fontfile='C\:/Windows/Fonts/arial.ttf':text='Date \:':x=(w)/5:y=(h)-250,drawtext=fontsize=28:fontcolor=White:fontfile='C\:/Windows/Fonts/arial.ttf':text='"+ self.date +"':x=((w)/5)+250:y=(h)-250,drawtext=fontsize=28:fontcolor=White:fontfile='C\:/Windows/Fonts/arial.ttf':text='Element Name \:':x=(w)/5:y=(h)-290,drawtext=fontsize=28:fontcolor=White:fontfile='C\:/Windows/Fonts/arial.ttf':text='"+ self.qeName +"':x=((w)/5)+250:y=(h)-290,drawtext=fontfile='C\:/Windows/Fonts/arial.ttf':text='FUTUREWORKS':x=130:y=200:fontsize=54:fontcolor=White[out]", self.oneImage ]

								process = subprocess.Popen(args, stdout=subprocess.PIPE)
								ret = process.wait()

								if (ret == 0):																																	# "D:/imagesequence/dpx/brn_055.%04d.dpx"
									print 'penultimate\n'
									self.imageregex  = self.setImageRegex(sampleFileName.split('.')[1])

									newList = os.listdir(fName)																											# get file name from user folder
									bunchOfPictures = self.symlinkFolder + fpof + "." + self.imageregex  + "." + self.fileExtension
									tempBunchOfPictures = self.tempFolder + "/" + fpof + "." + self.imageregex  + "." + self.fileExtension

									objSym = symlinkHouseKeep()
									objSym.createLink( newList , fName, self.symlinkFolder, self.fileExtension , fpof, self.imageregex)
#									print 'bunchOfPictures  : ',bunchOfPictures ,'\n'
#									print 'tempBunchOfPictures : ',tempBunchOfPictures ,'\n'
									cnt = 0
									for each in os.listdir(self.symlinkFolder):
										aaaa = self.symlinkFolder + "/" + each
										bbbb = self.tempFolder + "/" + each
										args = ["ffmpeg", "-i", aaaa  , "-vf", "drawtext=fontfile='C\:/Windows/Fonts/arial.ttf':text='shotcam':x=(w)/2:y=(h)-35:fontsize=24:fontcolor=Yellow,drawtext=fontfile='C\:/Windows/Fonts/arial.ttf':text='Frame \:':x=(w)-600:y=(h)-35:fontsize=24:fontcolor=Yellow,drawtext=fontfile='C\:/Windows/Fonts/arial.ttf':text='" + str(cnt) +"':x=(w)-300:y=(h)-35:fontsize=24:fontcolor=Yellow,drawtext=fontfile='C\:/Windows/Fonts/arial.ttf':text='Focal Length \:':x=(w)-600:y=(h)-65:fontsize=24:fontcolor=Yellow,drawtext=fontfile='C\:/Windows/Fonts/arial.ttf':text='" + self.lens +"':x=(w)-300:y=(h)-65:fontsize=24:fontcolor=Yellow", bbbb  ]
										process = subprocess.Popen(args, stdout=subprocess.PIPE)
										ret = process.wait()
										if (ret == 0):
											cnt = cnt + 1										
											continue
									print 'ultimate\n'
#************************************************************************************
# since the first image is going to be "0000" until ffmpeg takes any other, following line has the number hard coded to over overwrite 1st image from fname, it is without yellow labels									
#************************************************************************************
									shutil.copy(self.oneImage,(self.tempFolder + "/" + fpof + ".0000." + self.fileExtension) )
#************************************************************************************									
									quicktimeFile = fName + "/" + fpof + ".mov"

									args = ["ffmpeg", "-i", tempBunchOfPictures , "-vcodec", "png", "-pix_fmt", "rgb32", "-y", quicktimeFile]

									process = subprocess.Popen(args, stdout=subprocess.PIPE)
									ret = process.wait()
									if (ret == 0):
										message = "completed quicktime : %s %s" % (quicktimeFile," ... deleting temp folder")
										OpenMaya.MGlobal.displayInfo(message)
										
									"""
									clean up commands
									"""										
									os.remove(self.oneImage)																		# when running script perpetually, only first image number is constant delete this image once mov is created
									shutil.rmtree(self.myTemp)																	
									shutil.rmtree(self.symlinkFolder)
						else:
							OpenMaya.MGlobal.displayWarning("nothing in the folder")
		else:
			OpenMaya.MGlobal.displayWarning("Folder not existing. Create it then run this script")

#************************************************************************************
# userWindow
#************************************************************************************

	def userWindow(self):
		window = cmds.window( title="maya slate", iconName='ms', widthHeight=(200, 55) )
		cmds.columnLayout( adjustableColumn=True )
		cmds.text( label='Element Name' )
		self.elementName = cmds.optionMenuGrp( 'renderwith', label=' ', columnWidth=(2, 80) )
		cmds.menuItem( label='cones' )
		cmds.menuItem( label='rmcurves' )
		cmds.menuItem( label='mesh' )
		cmds.menuItem( label='headmesh' )
		cmds.text( label='Notes' )
		self.notes = cmds.scrollField( 'notes',editable=True, wordWrap=True, text='addtional info here...' )
		cmds.button( label='Close', command=('a.qeName  = cmds.optionMenuGrp( a.elementName , query=True, value=True )\na.qnotes = cmds.scrollField(a.notes , query = True, text = True)\ncmds.deleteUI(\"' + window + '\", window=True)\ncmds.fileBrowserDialog( m=4, fc=a.selectFolder, ft=\'directory\', an=\'Where should .mov reside in\')') )
		cmds.setParent( '..' )
		cmds.showWindow( window )

#************************************************************************************
# symlinkHouseKeep
#************************************************************************************
# type    : class 
# func    : createlink - create symbolic link of all files in folder
# listIm  : folderName
# fldr    : root folder name
# tmpfldr : sytem temp folder
# xtn     : file extension
# fpf     : first part of file
#************************************************************************************

class	symlinkHouseKeep(object):

	def __init__(self):
		self.nwidth = ""
		self.number = 0
		self.kdll = ctypes.windll.LoadLibrary(a.kerneldll)

	def givenos(self, nwid , numbr):
		x = ""
		for i in range(0,nwid - len(numbr )):
			x = x + "0"
		return x + str(numbr)

	def createLink(self, listIm, fldr, tmpfldr, xtn, fpf,imx):
		npad = int(re.findall("\d+", imx)[0])
		count = 0
		for filename in listIm:
			inpt = os.path.join(tmpfldr,(fpf + "." + self.givenos(npad ,str(count)) + "." + xtn )).replace("\\","/")
			count = count + 1
			output = os.path.join(fldr, filename).replace("\\","/")
			print 'inpt / output ',inpt ,  ' / ', output ,'\n'
			self.kdll.CreateSymbolicLinkA(inpt , output, 0)

a = makeQuicktime()

if	(cmds.file(query=True,sn=True,shn=True) == ""):
	OpenMaya.MGlobal.displayError("file not saved/ either empty file or save file!")
else:
	a.userWindow()
