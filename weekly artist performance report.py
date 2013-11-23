from shotgun_api3 import Shotgun
from datetime import date, timedelta
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.Utils import COMMASPACE, formatdate
from email.MIMEText import MIMEText
from email import Encoders

import xlwt
import datetime
import tempfile
import os
import smtplib
import shutil
import imp

modOffice = imp.load_source('office365','//xx.xx.xx.xxx/shotgunpro/office365.py')
reload(modOffice)
off = modOffice.office365()
one_day = datetime.timedelta(days=1)
cellData = ""
#cellData temporary variable to display minutes in hour/minutes
#================================================================================

xlwt.add_palette_colour("blue_x30", 0x30) # replaces "cool blue"
xlwt.add_palette_colour("periwinkle_x18", 0x18) # replaces "periwinkle"
xlwt.add_palette_colour("white_x09", 0x09) # replaces "white"
xlwt.add_palette_colour("blueish", 0x2c) # replaces "" 
xlwt.add_palette_colour("green_x39", 0x39) # replaces "quiet green"
xlwt.add_palette_colour("aqua_x31", 0x31) # replaces "aqua"

BLANK_TASK_CELL = xlwt.easyxf(
				'font: bold 1, name Tahoma, height 160;'
				'align: vertical center, horizontal center, wrap on;'
				'borders: left thin, right thin, top thin, bottom thin;'
				'pattern: pattern solid, pattern_fore_colour aqua_x31, pattern_back_colour aqua_x31'
				)

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

#================================================================================



try:
	sg = Shotgun('https://futureworks.shotgunstudio.com', 't_script',\
	 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
except smtplib.SMTPAuthenticationError:
	print 'SMTPAuthenticationError'
#================================================================================
#  Return the full week (Sunday first) of the week containing the given date.
#
#  'date' may be a datetime or date instance (the same type is returned).
#--------------------------------------------------------------------------------
#
def get_week(date):
	day_idx = (date.weekday() + 1) % 7	# turn sunday into 0, monday into 1, etc.
	sunday = date - datetime.timedelta(days=day_idx)
	date = sunday
	for n in xrange(7):
		yield date
		date += one_day
#================================================================================
# return maxtask for each artist 
#--------------------------------------------------------------------------------
def get_maxTask(artistid):

	mtask = 0 							# initialize
#	use	datetime.datetime.now().date()- datetime.timedelta(days=7) to get report of last week
	for idx, val in enumerate(get_week(datetime.datetime.now().date() - datetime.timedelta(days=7))):
		if (val.isoformat() <= datetime.date.today().strftime("%Y-%m-%d")):
			ret = sg.find('TimeLog',[['user','is',{"type":"HumanUser","id":artistid}],["date","is",val.isoformat()]], ["duration"])
			if (ret != []):
				if ( mtask < len(ret)):
					mtask = len(ret)
	return mtask

#================================================================================
filters = [["sg_status_list", "is", "act"],["sg_location","is","Mumbai"],["permission_rule_set","is",{'type':'PermissionRuleSet','id':8}]]	  # 8 is artist
fields = ["id"]
perdaytotal = 0
AtrName = ""
row = 1
column = 1
book = xlwt.Workbook()
sh = book.add_sheet("TimeGoal", cell_overwrite_ok=True)

total  = cumulativetotalOfWeek = timeInHour = timeInMinutes = timeInHourtotal = timeInMinutestotal = MaxTask  = MaxTaskFirstPointer = switchForTask  = 0  # initialize

#width = 1600 * 500
sh.write(0, 0, "Artist Name\t\t" )
sh.write(0, 1, "\t")
sh.write(0, 2, "Sunday",HEADER_CELL)
sh.write(0, 3, "Monday",HEADER_CELL)
sh.write(0, 4, "Tuesday",HEADER_CELL)
sh.write(0, 5, "Wednesday",HEADER_CELL)
sh.write(0, 6, "Thursday",HEADER_CELL)
sh.write(0, 7, "Friday",HEADER_CELL)
sh.write(0, 8, "Saturday",HEADER_CELL)
sh.write(0, 9, "\t")
#sh.write(1, 10, "not filled \n# @ # ")
sh.write(1, 10, "blank\nno data filled",BLANK_TASK_CELL)
sh.col(0).width = 0x0ff0
sh.col(1).width = 0x0ff0
sh.col(2).width = 0x0ff0
sh.col(3).width = 0x0ff0
sh.col(4).width = 0x0ff0
sh.col(5).width = 0x0ff0
sh.col(6).width = 0x0ff0
sh.col(7).width = 0x0ff0
sh.col(8).width = 0x0ff0
sh.col(9).width = 0x0ff0
sh.col(10).width = 0x0ff0

#sh.row(0).write(col_0, 'Issue', HEADER_CELL)
for cont in sg.find('HumanUser',filters , fields):
	maxTaskinaWeek = get_maxTask(cont['id'])										# get max task for each artist for a week
	AtrName = sg.find_one('HumanUser',[["id","is",cont['id']]],['name'])['name']

	sh.write(row, 0, AtrName,ARTIST_CELL)
	MaxTaskFirstPointer = row
	#if (AtrName == "Gyaneshwar Reddy") :
	rowRegister = row						# save row initial value
	columnRegister = column 				# save column initial value

	for idx, val in enumerate(get_week(datetime.datetime.now().date() - datetime.timedelta(days=7))):				#for d in get_week(datetime.datetime.now().date()):
		total = 0
		column = column + 1
		if (val.isoformat() <= datetime.date.today().strftime("%Y-%m-%d")):
			ret = sg.find('TimeLog',[['user','is',{"type":"HumanUser","id":cont['id']}],\
			["date","is",val.isoformat()]], ["duration","entity"])
			if (ret != []):
				switchForTask = 1

				for i in range(0,len(ret)):
					timeInHour = (ret[i]['duration'])/60
					timeInMinutes = (ret[i]['duration'])%60
					total = total + int(ret[i]['duration'])
					timeInHourtotal = total/60
					timeInMinutestotal = total%60

					if (ret[i]['entity'] != None):
						cellData = ret[i]['entity']['name'] + " - " + format(timeInHour)+ ":" + format(timeInMinutes)
					else:
						cellData = " blank - " + format(timeInHour)+ ":" + format(timeInMinutes)

					row = row + 1

					if ("blank" in cellData):
						sh.write(row, column, cellData, BLANK_TASK_CELL)
					else:
						sh.write(row, column, cellData,TASK_CELL)

				cumulativetotalOfWeek  = cumulativetotalOfWeek	+ total 						
				
				#print "total ",total ," timeInHourtotal ",timeInHourtotal ," timeInMinutestotal ",timeInMinutestotal ," cumulativetotalOfWeek  ",cumulativetotalOfWeek
					
				#row = row + 2
			else:
				#switchForTask  = 0
				#row = row + 1
				sh.write(row, column, "not filled")
			row = row + 2
			if (switchForTask == 1):
				cellData = format(timeInHourtotal)+ ":" +format(timeInMinutestotal)
				sh.write(maxTaskinaWeek + MaxTaskFirstPointer + 2 , column, cellData,TASK_TOTAL)
				total = 0
		else:
			break
		row = rowRegister
		switchForTask = 0

	column = columnRegister
	#row = row + 5 + MaxTask
	row = row + 5 + maxTaskinaWeek

#	if day of week more than current day then leave blank

try:

	tmp_dir = tempfile.mkdtemp()  # create dir
	OUTPUT_FILE = os.path.join(tmp_dir,"WeeklyReport.xls")
	book.save(OUTPUT_FILE)
	mailConn = off.create_conn()
	isConn = off.is_connected(mailConn)
	if (isConn == True):
		listmsg = MIMEMultipart()
		listmsg['From'] = off.MAILUSER
		listmsg['To'] = ",".join(off.PRODGROUPID + off.SHOTGUNADMIN)
		#listmsg['Subject'] = off.subject_list
		listmsg['Subject'] = "weekly report"
		#listmsg.attach(MIMEText(off.text_list_report))
		listmsg.attach(MIMEText("click to download file"))
		part = MIMEBase('application', "octet-stream")
		part.set_payload( open(OUTPUT_FILE,"rb").read() )
		Encoders.encode_base64(part)
		part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(OUTPUT_FILE))
		listmsg.attach(part)
		try:
			#mailConn.sendmail(off.MAILUSER, off.SUPERGROUPID[1], listmsg.as_string())
			mailConn.sendmail(off.MAILUSER, off.SHOTGUNADMIN, listmsg.as_string())
			print "file sent to \"%s\" \n" % (off.MAILUSER + off.SHOTGUNADMIN[0])
		except smtplib.SMTPRecipientsRefused as e:
			mailConn.rset()
		mailConn.close()							# if everything went well then close mail server

finally:
	try:
		shutil.rmtree(tmp_dir)	# delete directory
	except OSError as exc:
		if exc.errno != 2:	# code 2 - no such file or directory
			raise  # re-raise exception
