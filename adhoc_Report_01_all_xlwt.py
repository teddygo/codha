from shotgun_api3 import Shotgun

import os
import imp
import sys
import xlwt
import types

import shutil
import smtplib
import tempfile
import argparse

#from email.MIMEMultipart import MIMEMultipart
#from email.MIMEBase import MIMEBase
#from email.Utils import COMMASPACE, formatdate
#from email.MIMEText import MIMEText
#from email import Encoders

from calendar import monthrange
monthrange(2013,10)[1]



#=========================================================================================
# add this location to PYTHONPATH variable
sys.path.append("//00.00.00.000/shotgunpro/regular")

modOffice = imp.load_source('office365','//00.00.00.000/shotgunpro/regular/office365.py')
reload(modOffice)
off = modOffice.office365()

modFunc = imp.load_source('getModules','//00.00.00.000/shotgunpro/regular/getModules.py')
reload(modFunc)

#=========================================================================================

xlwt.add_palette_colour("blue_x30", 0x30) # replaces "cool blue"
xlwt.add_palette_colour("periwinkle_x18", 0x18) # replaces "periwinkle"
xlwt.add_palette_colour("white_x09", 0x09) # replaces "white"
xlwt.add_palette_colour("blueish", 0x2c) # replaces ""
xlwt.add_palette_colour("green_x39", 0x32) # replaces "quiet green"
xlwt.add_palette_colour("aqua_x31", 0x31) # replaces "aqua"

HEADER_CELL = xlwt.easyxf(
				'font: bold 1, name Tahoma, height 160;'
				'align: vertical center, horizontal center, wrap on;'
				'borders: left thin, right thin, top thin, bottom thin;'
				'pattern: pattern solid, pattern_fore_colour blue_x30, pattern_back_colour blue_x30'
				)

TASK_CELL = xlwt.easyxf(
				'font: bold 0, name Tahoma, height 160;'
				'align: vertical center, horizontal center, wrap on;'
				'borders: left thin, right thin, top thin, bottom thin;'
				'pattern: pattern solid, pattern_fore_colour periwinkle_x18, pattern_back_colour white_x09'
				)

TASK_TOTAL = xlwt.easyxf(
				'font: bold 1, name Tahoma, height 160;'
				'align: vertical center, horizontal center, wrap on;'
				'borders: left thin, right thin, top thin, bottom thin;'
				'pattern: pattern solid, pattern_fore_colour blueish, pattern_back_colour blueish'
				)

ARTIST_CELL = xlwt.easyxf('pattern: pattern solid, fore_colour green_x39;' 'align: horiz right, wrap yes;' "borders: left double;")
#=========================================================================================

numberOfDays = 30
totalcount = 0
firstday = ''
lastday = ''

monthsInAYear = ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]

fwxlocation = ["mumbai","chennai"]

dates = ["1","2","3","4","5","6","7","8","9","10",
        "11","12","13","14","15","16","17","18","19","20",
        "21","22","23","24","25","26","27","28","29","30","31"]

emailList = ["chennai.production@futureworks.in","bhawna.vijay@futureworks.in","kailash@futureworks.in","geetha.prabhuram@futureworks.in"]

weekBinary = ["true","false"]

row = 1
column = 1
cellData_01 = ''
cellData_02 = ''
cellData_03 = ''
cellData_04 = ''
cellData_05 = ''
cellData_06 = ''
book = xlwt.Workbook()
sh = book.add_sheet("TimeGoal", cell_overwrite_ok=True)

#=========================================================================================


def printReport():
	global totalcount
	global row,column, cellData_01, cellData_02, cellData_03, cellData_04
	import datetime
	currentYear = datetime.date.today().strftime("%Y")
	currentDay = datetime.date.today().strftime("%d")

	if (not isinstance(options.week,types.NoneType) or (options.week == True)) and (not isinstance(options.month,types.NoneType)):
		print "week not none type then calculate week"
		if isinstance(options.day,types.NoneType):
			print 'cannot be none'
			#logger.info()
			#logger.debug()
			return -1
		#options.day set in format 
		weeklist = modFunc.returnWeek(options.day)
		print ' weeklist' ,weeklist,'\n'
		
	
	
		from datetime import date, datetime , timedelta
		date_filter = datetime.strptime(argdate1, '%b %d %Y')			# search for records not before 1 sept 2013
		firstday = (date_filter).strftime('%Y-%m-%d')
	
		date_filter = datetime.strptime(argdate2, '%b %d %Y')			# search for records not before 1 sept 2013
		lastday = (date_filter).strftime('%Y-%m-%d')
		
	else:
		print 'specify month day week'

	if isinstance(options.day,types.NoneType):
		argdate1 = (options.month).title() + ' 1 ' + currentYear
		argdate2 = (options.month).title() + ' 31 ' + currentYear
	else:
		argdate1 = (options.month).title() + ' ' + options.day + ' ' + currentYear
		argdate2 = (options.month).title() + ' ' + options.day + ' ' + currentYear

	filters_01 = [["sg_location","is",options.location],[ "groups", "is", { "type": "Group", "id": 5 } ],["sg_status_list","is","act"]]          # group id 5 is for mumbai
	fields_01 = ["id","name"]

	fields_02 = ['duration','entity.Task.entity','project','date']

	#print "Artist Name \t\t\tProject\t\t\tShot Name\t\t\tLogged Time (hrs:mnts)\t\t\t\n"
	
	sh.write(0, 0, "Artist Name\t\t" )
	sh.write(0, 1, "Date",HEADER_CELL)
	sh.write(0, 2, "Project",HEADER_CELL)
	sh.write(0, 3, "Shot Name",HEADER_CELL)
	sh.write(0, 4, "Logged Time",HEADER_CELL)
	sh.write(0, 5, "(hrs:mnts)",HEADER_CELL)

	sh.col(0).width = 0x0ff0
	sh.col(1).width = 0x0ff0
	sh.col(2).width = 0x0ff0
	sh.col(3).width = 0x0ff0
	sh.col(4).width = 0x0ff0
	sh.col(5).width = 0x0ff0

	for alls in sg.find('HumanUser',filters_01,fields_01):
		artistId = alls['id']
		aname = alls['name']
		column = 1
		sh.write(row, 0, aname,ARTIST_CELL)
		row = row + 1
		filters_02 = [["date","between", firstday, lastday], [ "user", "is", { "type": "HumanUser", "id": artistId } ]]
		for ulls in sg.find('TimeLog',filters_02,fields_02):
			column = 1
			if not isinstance(ulls['entity.Task.entity'],types.NoneType) and not isinstance(ulls['project'], types.NoneType):
				if isinstance(ulls['entity.Task.entity']['name'],types.NoneType) and isinstance(ulls['project']['name'], types.NoneType):
					#print '\t\t\t',ulls['date'],'\t\t\t','no data','\t\t\t',
					#'no data','\t\t\t',(ulls['duration']/60)+":"+(ulls['duration']%60)

					cellData_01 = ulls['date']
					cellData_02 = 'no data'
					cellData_03 = 'no data'
					cellData_04 = str(ulls['duration']/60)+":"+str(ulls['duration']%60)

				elif isinstance(ulls['entity.Task.entity']['name'],types.NoneType):
					#print '\t\t\t',ulls['date'],'\t\t\t',ulls['project']['name'],
					#'\t\t\t','no data','\t\t\t',str(ulls['duration']/60)+":"+str(ulls['duration']%60)

					cellData_01 = ulls['date']
					cellData_02 = ulls['project']['name']
					cellData_03 = 'no data'
					cellData_04 = str(ulls['duration']/60)+":"+str(ulls['duration']%60)

				elif isinstance(ulls['project']['name'],types.NoneType):
					#print '\t\t\t',ulls['date'],'\t\t\t','no data','\t\t\t',
					#ulls['entity.Task.entity']['name'],'\t\t\t',str(ulls['duration']/60)+":"+str(ulls['duration']%60)

					cellData_01 = ulls['date']
					cellData_02 = 'no data'
					cellData_03 = ulls['entity.Task.entity']['name']
					cellData_04 = str(ulls['duration']/60)+":"+str(ulls['duration']%60)

				else:
					if (ulls['duration'] is not None):
						#print '\t\t\t',ulls['date'],'\t\t\t',ulls['project']['name'],'\t\t\t',
						#ulls['entity.Task.entity']['name'],'\t\t\t',str(ulls['duration']/60)+":"+str(ulls['duration']%60)

						cellData_01 = ulls['date']
						cellData_02 = ulls['project']['name']
						cellData_03 = ulls['entity.Task.entity']['name']
						cellData_04 = str(ulls['duration']/60)+":"+str(ulls['duration']%60)

					else:
						#print '\t\t\t',ulls['date'],'\t\t\t',ulls['project']['name'],'\t\t\t',
						#ulls['entity.Task.entity']['name'],'\t\t\t','no data'

						cellData_01 = ulls['date']
						cellData_02 = ulls['project']['name']
						cellData_03 = ulls['entity.Task.entity']['name']
						cellData_04 = 'no data'
						
			else:
				#print '\t\t\t',ulls['date'],'\t\t\t','some data missing','\t\t\t\t\t\t',
				#str(ulls['duration']/60)+":"+str(ulls['duration']%60)

				cellData_01 = ulls['date']
				cellData_02 = 'no data'
				cellData_03 = 'no data'
				cellData_04 = str(ulls['duration']/60)+":"+str(ulls['duration']%60)

			if (ulls['duration'] is not None):
				totalcount = totalcount + ulls['duration']
				

			sh.write(row, column, cellData_01, TASK_CELL)
			column = column + 1
			sh.write(row, column, cellData_02, TASK_CELL)
			column = column + 1
			sh.write(row, column, cellData_03, TASK_CELL)
			column = column + 1
			sh.write(row, column, cellData_04, TASK_CELL)

			row = row + 1


		row = row + 1
		column = 4
		print '\n\t\t\t\t\t\t\t\t\t\t\tTotal Time : \t',str(totalcount/60)+" hrs "+str(totalcount%60),' mins\n'
		cellData_05 = str(totalcount/60)+" hrs "+str(totalcount%60)+' mins'
		sh.write(row, column, cellData_05 , TASK_TOTAL)

		row = row + 1

		totalcount = 0

parser = argparse.ArgumentParser(description="A program to generate report from any workstation")
parser.add_argument("-location", choices = fwxlocation ,
                    help='\nLocation of which report is needed. Allowed values are  '+', '.join(fwxlocation),metavar='',choices = fwxlocation)
parser.add_argument("-month",
                    help='\nWhich month would you like report for. Allowed values are '+', '.join(monthsInAYear), metavar='', choices = monthsInAYear)
parser.add_argument("-day", nargs='?',
                    help='\nWhich day would you like report for. Allowed values are '+', '.join(dates), metavar='', choices = dates)
parser.add_argument("-week", nargs='?',
                    help='\nsay yes if you want report for. Allowed values are '+', '.join(weekBinary), metavar='', choices = weekBinary )
parser.add_argument("-emailid1", nargs='?',
                    help='\nWho should read this report. Allowed values are '+', '.join(emailList), metavar='', choices = emailList, default = "shotgunsupport@futureworks.in")
parser.add_argument("-emailid2", nargs='?',
                    help='\nWho should read this report. Allowed values are '+', '.join(emailList), metavar='', choices = emailList, default = "shotgunsupport@futureworks.in")

#args = parser.parse_args()
options, unk = parser.parse_known_args()

sg = Shotgun('https://jhkjhkhs.jhkjhkkkdio.com' , 'khkhcript', 'eb703a2kjhgkjhkjh7cb587bc9d831d03a')

printReport()

tmp_dir = tempfile.mkdtemp()  # create dir
OUTPUT_FILE = os.path.join(tmp_dir,"AnyTimeReport.xls")
book.save(OUTPUT_FILE)
mailConn = off.create_conn()
isConn = off.is_connected(mailConn)
if (isConn == True):
	#listmsg = MIMEMultipart()
	#listmsg['From'] = off.MAILUSER
	#listmsg['To'] = ",".join(listofemailaddress + off.SHOTGUNADMIN)
	#listmsg['Subject'] = "test timelog report from python command line"
	#listmsg.attach(MIMEText("send message to shotgunsupport@futureworks.in for further queries."))

	#part = MIMEBase('application', "octet-stream")
	#part.set_payload( open(OUTPUT_FILE,"rb").read() )
	#Encoders.encode_base64(part)
	#part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(OUTPUT_FILE))
	#listmsg.attach(part)
	try:
		mailConn.sendmail(off.MAILUSER, listofemailaddress, listmsg.as_string())
		#sendAttachment(self, send_from, send_to, send_cc, subject, text, files=[], connect=""):
		print "file sent to \"%s\" \n" % (off.MAILUSER + off.SHOTGUNADMIN[0])
	except smtplib.SMTPRecipientsRefused as e:
		mailConn.rset()
	mailConn.close()							# if everything went well then close mail server
try:
	shutil.rmtree(tmp_dir)	# delete directory
except OSError as exc:
	if exc.errno != 2:	# code 2 - no such file or directory
		raise  # re-raise exception
