from win32api import CloseHandle, GetLastError, SetConsoleCtrlHandler
import imp
import os
import sys 
import time
import pythoncom
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import pkgutil
import inspect
from shotgun_api3 import Shotgun

class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "timelog"
    _svc_display_name_ = "shotgun time log"

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        SetConsoleCtrlHandler(lambda x: True, True)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)

        self.count = 0
        self.estinmins = 0
        self.isAlive = True
        self.envv = ''
        self.prlist = []

        

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.run = False

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        self.sg = Shotgun('https://xxxxxxxxxxxxxxxx.shotgunstudio.com' , 'timelogservice', 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        self.main()

    def updateProject(self, projectid):
        servicemanager.LogWarningMsg( unicode(projectid))
        filters = [["project.Project.id", "is", projectid]]
        fields = ["time_logs_sum","est_in_mins"]
        for eventTimeLog in self.sg.find('Task', filters, fields):
            self.count = self.count + eventTimeLog['time_logs_sum']
            if eventTimeLog['est_in_mins'] is not None:
                self.estinmins = self.estinmins + eventTimeLog['est_in_mins']

        data = { 'sg_artisttimelog':self.count/600 }
        asset = self.sg.update("Project",projectid,data)
        data = { 'sg_total_bid':self.estinmins/600}
        asset = self.sg.update("Project",projectid,data)

    def main(self):
        while self.isAlive:
            filters = [["sg_status", "is", "active"]]
            fields = ['id']
            for f in self.sg.find('Project',filters,fields):
                self.prlist.append(f['id'])

            for prid in self.prlist:
                self.updateProject(prid)
                self.count = 0
                self.estinmins = 0
                if win32event.WaitForSingleObject(self.hWaitStop, 3000) == win32event.WAIT_OBJECT_0:
                    break

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)
