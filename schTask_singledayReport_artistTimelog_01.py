from shotgun_api3 import Shotgun

import os
import imp
import xlwt
import types

import shutil
import smtplib
import tempfile
import argparse

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.Utils import COMMASPACE, formatdate
from email.MIMEText import MIMEText
from email import Encoders



#=========================================================================================

modOffice = imp.load_source('office365','//xx.xx.xx.xxx/d$/shotgunpro/regular/office365.py')
#reload(modOffice)
off = modOffice.office365()

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

emailList = ["nishith.singhai@futureworks.in","bhawna.vijay@futureworks.in","chennai.production@futureworks.in","kailash.jadhav@futureworks.in","geetha.prabhuram@futureworks.in"]

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
	today = datetime.date.today().strftime("%Y-%m-%d")

	from datetime import date, datetime , timedelta

	filters_01 = [["sg_location","is",options.location],[ "groups", "is", { "type": "Group", "id": 5 } ],["sg_status_list","is","act"]]          # group id 5 is for mumbai
	fields_01 = ["id","name"]

	fields_02 = ['duration','entity.Task.entity','project','date']

	
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
		filters_02 = [["date","is", today], [ "user", "is", { "type": "HumanUser", "id": artistId } ]]
		for ulls in sg.find('TimeLog',filters_02,fields_02):
			column = 1
			if not isinstance(ulls['entity.Task.entity'],types.NoneType) and not isinstance(ulls['project'], types.NoneType):
				if isinstance(ulls['entity.Task.entity']['name'],types.NoneType) and isinstance(ulls['project']['name'], types.NoneType):


					cellData_01 = ulls['date']
					cellData_02 = 'no data'
					cellData_03 = 'no data'
					cellData_04 = str(ulls['duration']/60)+":"+str(ulls['duration']%60)

				elif isinstance(ulls['entity.Task.entity']['name'],types.NoneType):


					cellData_01 = ulls['date']
					cellData_02 = ulls['project']['name']
					cellData_03 = 'no data'
					cellData_04 = str(ulls['duration']/60)+":"+str(ulls['duration']%60)

				elif isinstance(ulls['project']['name'],types.NoneType):


					cellData_01 = ulls['date']
					cellData_02 = 'no data'
					cellData_03 = ulls['entity.Task.entity']['name']
					cellData_04 = str(ulls['duration']/60)+":"+str(ulls['duration']%60)

				else:
					if (ulls['duration'] is not None):


						cellData_01 = ulls['date']
						cellData_02 = ulls['project']['name']
						cellData_03 = ulls['entity.Task.entity']['name']
						cellData_04 = str(ulls['duration']/60)+":"+str(ulls['duration']%60)

					else:


						cellData_01 = ulls['date']
						cellData_02 = ulls['project']['name']
						cellData_03 = ulls['entity.Task.entity']['name']
						cellData_04 = 'no data'
						
			else:


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

		cellData_05 = str(totalcount/60)+" hrs "+str(totalcount%60)+' mins'
		sh.write(row, column, cellData_05 , TASK_TOTAL)

		row = row + 1

		totalcount = 0

parser = argparse.ArgumentParser(description="A program to generate report from any workstation")
parser.add_argument("location", choices = fwxlocation ,
                    help='Location of which report is needed. Allowed values are  '+', '.join(fwxlocation),metavar='')
parser.add_argument("emailid1", 
                    help='Who should read this report. Allowed values are '+', '.join(dates), metavar='', choices = emailList, default = "shotgunsupport@futureworks.in")
parser.add_argument("emailid2", nargs='?',
                    help='Who should read this report. Allowed values are '+', '.join(dates), metavar='', choices = emailList, default = "chennai.production@futureworks.in")

#args = parser.parse_args()
options, unk = parser.parse_known_args()

sg = Shotgun('https://futureworks.shotgunstudio.com' , 't_script', 'eb703a27885e0bf726651b77cb587bc9d831d03a')

printReport()
listofemailaddress = []
listofemailaddress.append(options.emailid1) # mandatory
if options.emailid2 is not None:				# optional
	listofemailaddress.append(options.emailid2)

tmp_dir = tempfile.mkdtemp()  # create dir
OUTPUT_FILE = os.path.join(tmp_dir,"WeeklyReport.xls")
book.save(OUTPUT_FILE)
mailConn = off.create_conn()
isConn = off.is_connected(mailConn)
if (isConn == True):
	listmsg = MIMEMultipart()
	listmsg['From'] = off.MAILUSER
	listmsg['To'] = ",".join(listofemailaddress + off.SHOTGUNADMIN)
	listmsg['Subject'] = "test timelog report from python command line"
	listmsg.attach(MIMEText("send message to shotgunsupport@futureworks.in for further queries."))

	part = MIMEBase('application', "octet-stream")
	part.set_payload( open(OUTPUT_FILE,"rb").read() )
	Encoders.encode_base64(part)
	part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(OUTPUT_FILE))
	listmsg.attach(part)
	try:
		mailConn.sendmail(off.MAILUSER, listofemailaddress, listmsg.as_string())
		print "file sent to \"%s\" \n" % (off.MAILUSER + listofemailaddress[0])
	except smtplib.SMTPRecipientsRefused as e:
		mailConn.rset()
	mailConn.close()							# if everything went well then close mail server
try:
	shutil.rmtree(tmp_dir)	# delete directory
	del listofemailaddress
except OSError as exc:
	if exc.errno != 2:	# code 2 - no such file or directory
		raise  # re-raise exception
