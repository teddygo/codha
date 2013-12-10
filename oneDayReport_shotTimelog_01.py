from shotgun_api3 import Shotgun

import os
import re
import imp
import xlwt
import types

import shutil
import smtplib
import tempfile
import argparse

from datetime import date, datetime , timedelta
COMMASPACE = ', '
#=========================================================================================

class RegexValidator(object):
    """
    Performs regular expression match on value.
    If match fails a ValueError is raised
    """

    def __init__(self, pattern, statement=None):
        self.pattern = re.compile(pattern)
        self.statement = statement
        if not self.statement:
            self.statement = "must match pattern %s" % self.pattern

    def __call__(self, string):

#        parse("2003-19-15")
        match = self.pattern.search(string)
        if not match:
            raise argparse.ArgumentTypeError(self.statement)
        return string


#=========================================================================================

modOffice = imp.load_source('office365','//00.00.00.000/shotgunpro/regular/office365.py')
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
column = 0
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
	global row,column, cellData_01, cellData_02, cellData_03, cellData_04, cellData_05

	date_filter = datetime.strptime(options.date1, '%Y-%m-%d')			
	firstday = (date_filter).strftime('%Y-%m-%d')

	date_filter = datetime.strptime(options.date2, '%Y-%m-%d')			
	lastday = (date_filter).strftime('%Y-%m-%d')

	filters_01 = [["date","between", firstday, lastday]]
	fields_01 = ['entity','project','user','duration']
	order_01 = [{'field_name':'project','direction':'asc'}]

	sh.write(0, 0, "Project\t\t",HEADER_CELL )
	sh.write(0, 1, "Shot\t\t",HEADER_CELL)
	sh.write(0, 2, "Artist\t\t",HEADER_CELL)
	sh.write(0, 3, "Logged Time",HEADER_CELL)
	sh.write(0, 4, "(hrs:mnts)",TASK_CELL)

	#sh.col(0).width = 0x0ff0
	#sh.col(1).width = 0x0ff0
	#sh.col(2).width = 0x0ff0
	#sh.col(3).width = 0x0ff0
	#sh.col(4).width = 0x0ff0
	#sh.col(5).width = 0x0ff0

	for alls in sg.find('TimeLog',filters_01,fields_01,order_01):

		#sh.write(row, 0, aname,ARTIST_CELL)
		row = row + 1
		column = 0
		if not isinstance(alls['entity'],types.NoneType) and not isinstance(alls['project'], types.NoneType) and not isinstance(alls['user'], types.NoneType):
			if (alls['duration'] is not None):
				totalcount = totalcount + int(alls['duration'])
				cellData_04 = str(int(alls['duration'])/60)+":"+str(int(alls['duration'])%60)
			else:
				cellData_04 = "0:0"

			cellData_01 = alls['project']['name']
			cellData_02 = alls['entity']['name']
			cellData_03 = alls['user']['name']

			sh.write(row, column, cellData_01, TASK_CELL)
			column = column + 1
			sh.write(row, column, cellData_02, TASK_CELL)
			column = column + 1
			sh.write(row, column, cellData_03, TASK_CELL)
			column = column + 1
			sh.write(row, column, cellData_04, TASK_CELL)

			row = row + 1
			column = 3

		cellData_05 = str(totalcount/60)+" hrs "+str(totalcount%60)+' mins'
		sh.write(row, column, cellData_05 , TASK_TOTAL)

		row = row + 1

		totalcount = 0

parser = argparse.ArgumentParser()
parser.add_argument('-location', default='mumbai',choices=fwxlocation)
parser.add_argument('-date1', dest='date1', type=RegexValidator("^\d\d\d\d-(0[1-9]|1[0-2])-(0*([1-9]|[12][0-9]|3[01]))$", statement="must be of the form yyyy-mm-dd"))
parser.add_argument('-date2', dest='date2', type=RegexValidator("^\d\d\d\d-(0[1-9]|1[0-2])-(0*([1-9]|[12][0-9]|3[01]))$", statement="must be of the form yyyy-mm-dd"))
parser.add_argument('-email', default=[], nargs='*',choices=emailList)

parser.parse_args()	
options, unk = parser.parse_known_args()

sg = Shotgun('https://futureworks.shotgunstudio.com' , 't_script', 'eb703a27885e0bf726651b77cb587bc9d831d03a')

printReport()

listofemailaddress = []
listofemailaddress.append(options.email) # mandatory


tmp_dir = tempfile.mkdtemp()  # create dir
OUTPUT_FILE = os.path.join(tmp_dir,"ShotReport.xls")
book.save(OUTPUT_FILE)
files = []
files.append(OUTPUT_FILE)
mailConn = off.create_conn()
isConn = off.is_connected(mailConn)
if (isConn == True):
	try:
		#mailConn.sendmail(off.MAILUSER, listofemailaddress, listmsg.as_string())
		off.sendAttachment(off.MAILUSER, options.email , [], "auto generated shot specific report", "send message to shotgunsupport@futureworks.in for further queries.", files, mailConn)
		print "file sent to \"%s\" \n" % (listofemailaddress[0])
	except smtplib.SMTPRecipientsRefused as e:
		mailConn.rset()
	mailConn.close()							# if everything went well then close mail server
try:
	shutil.rmtree(tmp_dir)	# delete directory
	del listofemailaddress
except OSError as exc:
	if exc.errno != 2:	# code 2 - no such file or directory
		raise  # re-raise exception
