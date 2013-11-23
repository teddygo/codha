import smtplib
import os
import sys

#from email.mime.base import MIMEBase for python 3.0

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.Utils import COMMASPACE, formatdate
from email.MIMEText import MIMEText
from email import Encoders


class office365(object):

	def __init__(self):
		self.MAILUSER = "shotgunsupport@futureworks.in"
		self.PRODGROUPID = ['bhawna.vijay@futureworks.in']
		self.SHOTGUNADMIN = ['nishith.singhai@futureworks.in']
		self.SUPERGROUPID = ["xxxxxxx.cccccc@futureworks.in","xxxxxxxxxxx@futureworks.in"]
		self.text_02_report = "click to download file"
		self.MAILPASSWORD = 'xxxxxxxxxxxx'		

	def create_conn(self):
		try:
			conn = smtplib.SMTP('smtp.office365.com',587)
			conn.starttls()
			conn.ehlo()
			try:
				conn.login(self.MAILUSER, self.MAILPASSWORD)
				return conn
			except smtplib.SMTPAuthenticationError:
				print 'SMTPAuthenticationError'

		except smtplib.socket.gaierror:
			print 'smtplib.socket.gaierror'

	def is_connected(self,conn):
		try:
			status = conn.noop()[0]
		except:  # smtplib.SMTPServerDisconnected
			status = -1
		return True if status == 250 else False

	def sendAttachment(self, send_from, send_to, send_cc, subject, text, files=[], connect=""):
		# sent_to is a list
		listmsg = MIMEMultipart()
		listmsg['From'] = send_from
		listmsg['To'] = ', '.join(send_to)
		listmsg['Cc'] = ', '.join(send_cc)
		listmsg['Subject'] = subject
		listmsg.attach(MIMEText(text))

		for f in files:
			part = MIMEBase('application', "octet-stream")
			part.set_payload( open(f,"rb").read() )
			Encoders.encode_base64(part)
			part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
			listmsg.attach(part)

		try:
			if (connect == ""):
				sys.exit('Error! - no connection found. run office365.create_conn()')
			connect.sendmail(send_from, send_to+send_cc, listmsg.as_string())
		except smtplib.SMTPRecipientsRefused as e:
			connect.rset()
			
	def closeConnect(self,conn):
		conn.close()
