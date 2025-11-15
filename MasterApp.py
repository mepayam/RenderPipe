"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
#########################################################################
    MasterApp handles the core master function of RenderPipe. 
    Copyright (C) 2012 Hadi Saraf , Payam Memar

    MasterApp is part of RenderPipe.

    RenderPipe is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#########################################################################
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""



import os
import sys
import socket
import time
import tkinter
import tkinter.filedialog
import subprocess
import threading
import pickle
import random

import HiStreamServer
import MasterGUI
import MasterConfig
import JobServer
import MayaServer
import XSIServer
import _3DSMaxServer
import NukeServer



# message strings for networking\ 
# communication of master/slave connections
#
EXIT_SLAVE_MSGN =       '01010101'
START_CLIENT_MSGN =     '10011001'
STOP_CLIENT_MSGN =      '01100110'
STPWP_CLIENT_MSGN =     '00110011'
FINISH_CLIENT_MSGN =    '11001100'



class JobPackage:
    "class to bundle the job data"
    def __init__ (self,
                  jobName = None,
                  jobState = None, jobPrio = 0, 
                  jobStartFrm = None, jobEndFrm = None, jobPackSize = None, 
                  jobSrcFile = None, jobDestPath = None, jobOutName = None,
                  jobMaster = None, jobPort = None, jobServers = None):
        self.jobName = jobName
        self.jobState = jobState
        self.jobPrio = jobPrio
        self.jobStartFrm = jobStartFrm
        self.jobEndFrm = jobEndFrm
        self.jobPackSize = jobPackSize
        self.jobSrcFile = jobSrcFile
        self.jobDestPath = jobDestPath
        self.jobOutName = jobOutName
        self.jobMaster = jobMaster
        self.jobPort = jobPort
        self.jobServers = jobServers

        



class Connection( HiStreamServer.RequestPack ):
    """class to handle the master connections,
        inherited from HiStreamServer.RequestPack,
        overrides the handle method"""
    BUFFER_SIZE = MasterConfig.BUFFER_SIZE
    def __init__ (self,
                  sock,
                  addr,
                  master,
                  connectCallback,
                  closeCallback,
                  recvCallback):
        self.ServerState = JobServer.SERVER_IDLE_STAT
        self.ServerJob = 0
        self.WPFlag = False
        HiStreamServer.RequestPack.__init__( self,
                                              sock,
                                              addr,
                                              master,
                                              connectCallback,
                                              closeCallback,
                                              recvCallback )
    def handle (self):
        while True:
            # Receive the message from all connections
            # Check the closing condition of the connection
            # If closed, then terminate handle() method and fall into the finish() method and call closeCallback()
            #
            if self.exitFlag:
                sys.exit()
            if not self.verifyConnection( self.recvMsg() ):
                return






class MasterApp( HiStreamServer.MultiStreamServer ):
    """class to handle the application,
        inherited from HiStreamServer.MultiStreamServer"""
    ADDR_FAMILY = socket.AF_INET
    SOCK_TYPE = socket.SOCK_STREAM
    HOST_NAME = socket.gethostname()
    MASTER_PORT = MasterConfig.MASTER_PORT
    BUFFER_SIZE = MasterConfig.BUFFER_SIZE

    Jobs_List = []
    Servers_List = []

    LockThrd = threading.Lock()

    
    def __init__ (self):
        """ runs the master GUI and master application """ 
        MasterGUI.MasterGUI.__init__( self )      # initiates the master GUI
        HiStreamServer.MultiStreamServer.__init__( self, (MasterApp.HOST_NAME, MasterApp.MASTER_PORT), Connection, 
                                                self.onConnect, self.onClose, self.onRecv )    # initiates the master application

        time.sleep( 1 )
        threading.Thread( target = self.runMasterGUI, args = () ).start()   # runs the thread of master GUI
        time.sleep( 1 )
        threading.Thread( target = self.runMasterApp, args = () ).start()   # runs the thread of master application
        


    def runMasterGUI (self):
        """ runs the master GUI """
        self.setMayaGUI()
        self.runGUI()



    def runMasterApp (self):
        """ runs the server.handleRequestAlways() method """
        self.handleRequestAlways()



    def onConnect (self, connection):
        """ this is called whenever a connection is established, 
            connection : the connected server object"""
        serverAddrs = []
        for thisServer in MasterApp.Servers_List:
            serverAddrs.append( thisServer.clientAddr[0] )
        if not connection.clientAddr[0] in serverAddrs:
            MasterApp.Servers_List.append( connection )
            self.insertLog( str( connection.clientAddr[0] ) + " is connected", 'inf', 1 )
            self.appendServer( connection )
        else:
            self.insertLog( "another slave with the IP, " + connection.clientAddr[0] + " is trying to connect" )
            msg = pickle.dumps( [EXIT_SLAVE_MSGN] )
            connection.sendMsg( msg )
            self.insertLog( "the second slave, " +\
                            connection.clientAddr[0] + " is closed", 'inf' )
            
                            
                            
    def onClose (self, connection):
        """ this is called whenever a connection is closed, 
            connection : the closed server object"""
        thisJob = connection.ServerJob
        if thisJob:
            try:
                thisJob.Servers.remove( connection )
                if not thisJob.Servers:
                    self.updateJob( thisJob, JobServer.JOB_STOPPED_STAT )
            except ValueError as err:
                print( "unexpected error while calling onClose  ->  " + str( err ) )
        if connection in MasterApp.Servers_List:
            MasterApp.Servers_List.remove( connection )
            self.removeServer( connection.clientAddr[0] )
            connection.exitFlag = True
            self.insertLog( connection.clientAddr[0] + " is closed", 'inf', 1 )

            



    def onRecv (self, connection, msg):
        """ this is called whenever a connection recieves a message, 
            connection : the receiving server object, 
            msg : the recevied message"""
        self.insertLog( repr( msg ) + " recved from " + connection.clientAddr[0], 'inf', 1 )




    def onMessage (self, msg, *args):
        """ callback function to handle master/server communications, 
            msg : the message received from server job, 
            args : the extra information relating to msg"""
        if msg == JobServer.PRESENT_MSG:
            client = args[0]
            job = args[1]
            server = self.mapClientAddr2Connection( client.clientAddr[0] )
            if server.WPFlag:
                job.jobFinishedFlag = True
                serverL = []
                serverL.append( server )
                self.stopClients( job, serverL )
                return True
            else:
                return False
            
        elif msg == JobServer.PACK_SENT_MSG:
            client = args[0]
            job = args[1]
            packNum = args[2]
            self.updateJob( job, None, None, packNum )
            
        elif msg == JobServer.SERVER_FINISHED_MSG:
            client = args[0]
            job = args[1]
            self.insertLog( "the slave, " + client.clientAddr[0] + " has finished the job, " + job.JobName, 'inf', True )
            self.finishServer( client, job )
                
        elif msg == JobServer.JOB_FINISHED_MSG:
            job = args[0]
            self.insertLog( "the job, " + job.JobName + " has been finished", 'inf', True )
            self.updateJob( job, JobServer.JOB_FINISHED_STAT, None, MasterConfig.MAX_PROGRESS_DASH_COUNT )

            

    def finishServer (self, client, job):
        """finishes the server job task, 
            client : the finished client, 
            job : the job to which the finished client is dedicated"""
        server = self.mapClientAddr2Connection( client.clientAddr[0] )
        job.Servers.remove( server )
        msg = pickle.dumps( [FINISH_CLIENT_MSGN, job.JobName, job.getServerType()] )
        server.sendMsg( msg )
        if server.ServerState == JobServer.SERVER_AUTOMATED_STAT:
            self.updateServer( server, 0 )
            if not self.manageServer( server ):
                self.updateServer( server, None, JobServer.SERVER_IDLE_STAT )
        else:
            self.updateServer( server, 0, JobServer.SERVER_IDLE_STAT )



    def manageServer (self, server):
        """handles the finished server, 
            server : the finished server"""
        precedentJob = self.getPrecedentJob()
        if precedentJob:
            self.insertLog( "the job, " + precedentJob.JobName + " is started", 'inf', True )
            serverAddrL = []
            serverAddrL.append( server.clientAddr[0] )
            self.updateJob( precedentJob, JobServer.JOB_RUNNING_STAT )
            self.activateClients( precedentJob, serverAddrL )
            return True
        return False



    def getPrecedentJob (self):
        """returns the next precedent job"""
        minPrio = 100000
        unfinishedJobs = []
        for thisJob in MasterApp.Jobs_List:
            if not thisJob.jobFinishedFlag:
                unfinishedJobs.append( thisJob )
                if thisJob.JobPrio < minPrio:
                    minPrio = thisJob.JobPrio
                    
        if not unfinishedJobs:
            return None

        precedentJobs = []
        for thisJob in unfinishedJobs:
            if thisJob.JobPrio == minPrio:
                precedentJobs.append( thisJob )
                
        minClientsCount = 100000
        for thisJob in precedentJobs:
            if len( thisJob.Servers ) < minClientsCount:
                minClientsCount = len( thisJob.Servers )
        for thisJob in precedentJobs:
            if len( thisJob.Servers ) == minClientsCount:
                return thisJob
            
        return None
        
        
            

    def updateJob (self, job, state = None, prio = None, packNum = None):
        """updates the job attributes based on arguments given, 
            job : the job that needs to be updated, 
            state : the new state of job, 
            prio : the new priority of job, 
            packNum : the new pack number of job"""
        if job in MasterApp.Jobs_List:
            index = self.removeJob( job.JobName )
        if state != None:
            job.JobState = state
        if prio != None:
            job.JobPrio = prio
        if packNum != None:
            job.jobPackNum = packNum
        self.appendJob( job )            




    def updateServer (self, server, job = None, state = None):
        """updates the server attributes based on arguments given, 
            server : the server that needs to be updated, 
            job : the new job to which server is dedicated, 
            state : the new state of server"""
        if server in MasterApp.Servers_List:
            self.removeServer( server.clientAddr[0] )
        if job != None:
            server.ServerJob = job
        if state != None:
            server.ServerState = state
        self.appendServer( server )

    
                

    def changePriority (self):
        """changes the priority of job, 
            this is called whenever <Change Prio> button is pressed"""
        jobNamesList = []
        for thisJob in MasterApp.Jobs_List:
            if not thisJob.jobFinishedFlag:
                jobNamesList.append( thisJob.JobName )
        entry = MasterGUI.EntryListboxDialog( self, "select the jobs to change the priority", jobNamesList, "enter new priority", True ).get()
        MasterApp.LockThrd.acquire()
        if entry:
            selectedJobNames = entry[0]
            if selectedJobNames:
                prio = entry[1]
                if prio:
                    try:
                        newPrio = int( prio )
                    except ValueError as err:
                        self.insertLog( "wrong priority entered", 'err')
                        self.insertLog( "failed to change the priority of the jobs, " + str( selectedJobNames ), 'err')
                    else:
                        for thisJobName in selectedJobNames:
                            thisJob = self.mapJobName2Job( thisJobName )
                            self.updateJob( thisJob, None, newPrio, None )
                        self.insertLog( "the job(s), " + str( selectedJobNames ) + " are changed to new priority successfully", 'inf' )
                else:
                    self.insertLog( "no priority given", 'inf' )
            else:
                self.insertLog( "no slaves are selected", 'inf' )
        else:
            self.insertLog( "canceled to change the priority", 'inf' )
        MasterApp.LockThrd.release()



    def queueJob (self, jobName = None,
                  jobStartFrm = None, jobEndFrm = None, jobPackSize = None,
                  jobSrcFile = None, jobDestPath = None, jobOutName = None):
        """make the job queued, 
            this is called whenever <Queue Job> button is pressed,
            the arguments are self explanatory"""
        if not jobName:
            jobName = self.jobNameData.get()
            jobState = None
            jobStartFrm = self.jobStartFrmData.get()
            jobEndFrm = self.jobEndFrmData.get()
            jobPackSize = self.jobPackSizeData.get()
            jobSrcFile = self.jobSrcFileData.get()
            jobDestPath = self.jobDestPathData.get()
            jobOutName = self.jobOutNameData.get()
        else:
            jobState = JobServer.JOB_QUEUED_STAT
        jobPrio = 0
        jobServer = MasterApp.HOST_NAME
        jobPort = self.getUnusedPort()
        
        jPack = JobPackage( jobName,
                            jobState, jobPrio, 
                            jobStartFrm, jobEndFrm, jobPackSize, 
                            jobSrcFile, jobDestPath, jobOutName,
                            jobServer, jobPort, [] ) 

        MasterApp.LockThrd.acquire()
        jobServer, jobThread = self.activateServer( jPack )    # activates the server side and add the job process id to the job package
        MasterApp.LockThrd.release()
        
        if jobServer:
            prio = MasterGUI.EntryDialog( self, "enter the priority number" ).get()
            MasterApp.LockThrd.acquire()
            if prio:
                try:
                    jobPrio = int( prio )
                    self.updateJob( jobServer, JobServer.JOB_QUEUED_STAT, jobPrio, 0 )
                    MasterApp.Jobs_List.append( jobServer )     # appends the job to the Jobs_List
                    jobThread.start()
                    self.insertLog( "the job " + jobName + " is queued successfully", 'inf' )
                except ValueError as err:
                    self.insertLog( "wrong input enetered as the priority number", 'err' )
                    self.insertLog( "failed to queue the job, " + jobName, 'err' )
                except Exception as err:
                    MasterApp.Jobs_List.remove( jobServer )
            else:
                self.insertLog( "failed to queue the job, " + jobName, 'err' )
            MasterApp.LockThrd.release()
        else:
            self.insertLog( "failed to queue the job, " + jobName, 'inf' )




    def runJob (self):
        """starts the job based on GUI set attributes,
            this is called whenevr <Start Job> button is pressed"""
        jobName = self.jobNameData.get()
        jobState = None
        jobPrio = 0
        jobStartFrm = self.jobStartFrmData.get()
        jobEndFrm = self.jobEndFrmData.get()
        jobPackSize = self.jobPackSizeData.get()
        jobSrcFile = self.jobSrcFileData.get()
        jobDestPath = self.jobDestPathData.get()
        jobOutName = self.jobOutNameData.get()
        jobMaster = MasterApp.HOST_NAME
        jobPort = self.getUnusedPort()

        jPack = JobPackage( jobName,
                            jobState, jobPrio, 
                            jobStartFrm, jobEndFrm, jobPackSize, 
                            jobSrcFile, jobDestPath, jobOutName,
                            jobMaster, jobPort, [] )

        MasterApp.LockThrd.acquire()
        jobServer, jobThread = self.activateServer( jPack )    # activates the server side and add the job process id to the job package
        MasterApp.LockThrd.release()
        
        if jobServer:
            idleServers = []
            for thisServer in MasterApp.Servers_List:
                if thisServer.ServerState == JobServer.SERVER_IDLE_STAT:
                    idleServers.append( thisServer.clientAddr[0] )
            if idleServers:
                selectedServers = MasterGUI.ListboxDialog( self, "select the slave(s) to run on the job, " + jobServer.JobName, idleServers, True ).get()
                MasterApp.LockThrd.acquire()
                if selectedServers:
                    self.updateJob( jobServer, JobServer.JOB_RUNNING_STAT, 0, 0 )
                    MasterApp.Jobs_List.append( jobServer )     # appends the job to the Jobs_List
                    jobThread.start()
                    time.sleep( MasterConfig.WAITE_SERVER_SLAVE_ACTIVATION )     # wait untill the server is established
                    #MasterApp.LockThrd.acquire()
                    if not self.activateClients( jobServer, selectedServers ):    # activates the client side
                        self.insertLog( "activating the clients, " + str( selectedServers ) + " failed", 'err' )
                    #MasterApp.LockThrd.release()
                    self.insertLog( "the job " + jobName + " is started successfully", 'inf', True )
                else:
                    self.insertLog( "canceled to start the job, " + jobName, 'err' )
                MasterApp.LockThrd.release()
            else:
                self.insertLog( "no slave is currently idle", 'inf' )
                prio = MasterGUI.EntryDialog( self, "do you want to make this job queued?\nif so enter priority number" ).get()
                MasterApp.LockThrd.acquire()
                if prio:
                    try:
                        jobPrio = int( prio )
                        self.updateJob( jobServer, JobServer.JOB_QUEUED_STAT, jobPrio, 0 )
                        MasterApp.Jobs_List.append( jobServer )     # appends the job to the Jobs_List
                        jobThread.start()
                        self.insertLog( "the job " + jobName + " is queued successfully", 'inf', True )
                    except ValueError as err:
                        self.insertLog( "wrong input enetered as the priority number", 'err' )
                        self.insertLog( "failed to queue the job, " + jobName, 'err' )
                    except Exception as err:
                        MasterApp.Jobs_List.remove( jobServer )
                else:
                    self.insertLog( "failed to queue the job, " + jobName, 'err' )
                MasterApp.LockThrd.release()
        else:
            self.insertLog( "failed to start the job, " + jobName, 'err' )

            


    def activateServer (self, jPack):
        """activates the server side of the connection,
            jPack : the bundled attributes of job"""
        if not self.checkIfDataIsValid( jPack ):    # check the validation of the data given
            return None, None
        try:
            Server = None
            if self.engineTypeData.get() == JobServer.MAYA_NGN:
                Server = MayaServer.MayaServer( jPack.jobName,
                                                    jPack.jobState, jPack.jobPrio, 
                                                    jPack.jobStartFrm, jPack.jobEndFrm, jPack.jobPackSize, 
                                                    jPack.jobSrcFile, jPack.jobDestPath, jPack.jobOutName,
                                                    jPack.jobMaster, jPack.jobPort, jPack.jobServers,
                                                    self.insertLog, self.insertRLog,
                                                    self.onMessage)
            elif self.engineTypeData.get() == JobServer.XSI_NGN:
                Server = XSIServer.XSIServer( jPack.jobName,
                                                    jPack.jobState, jPack.jobPrio, 
                                                    jPack.jobStartFrm, jPack.jobEndFrm, jPack.jobPackSize, 
                                                    jPack.jobSrcFile, jPack.jobDestPath, "set from source file",
                                                    jPack.jobMaster, jPack.jobPort, jPack.jobServers,
                                                    self.insertLog, self.insertRLog,
                                                    self.onMessage)                
            elif self.engineTypeData.get() == JobServer._3DSMAX_NGN:
                Server = _3DSMaxServer._3DSMaxServer( jPack.jobName,
                                                    jPack.jobState, jPack.jobPrio, 
                                                    jPack.jobStartFrm, jPack.jobEndFrm, jPack.jobPackSize, 
                                                    jPack.jobSrcFile, jPack.jobDestPath, jPack.jobOutName,
                                                    jPack.jobMaster, jPack.jobPort, jPack.jobServers,
                                                    self.insertLog, self.insertRLog,
                                                    self.onMessage)                
            elif self.engineTypeData.get() == JobServer.NUKE_NGN:
                Server = NukeServer.NukeServer( jPack.jobName,
                                                    jPack.jobState, jPack.jobPrio, 
                                                    jPack.jobStartFrm, jPack.jobEndFrm, jPack.jobPackSize, 
                                                    jPack.jobSrcFile, "set from source file", "set from source file",
                                                    jPack.jobMaster, jPack.jobPort, jPack.jobServers,
                                                    self.insertLog, self.insertRLog,
                                                    self.onMessage)
            jobThread = threading.Thread( target = Server.runServer, args = () )
            
            self.insertLog( "activating the server " + jPack.jobMaster + "..", 'inf' )

            return Server, jobThread
        except Exception as err:
            print( "activating the server " + jPack.jobMaster + " failed -> " + str( err ) )
            return None, None
        



    def activateClients (self, job, slaveAddrsList):
        """activates the client side of the connection,
            job : the job to which the clients are to be dedicated, 
            slaveAddrsList : the addresses of the clients dedicated to job"""
        jobName = job.JobName
        jobPort = job.Port
        for thisClientAddr in slaveAddrsList[:]:
            thisConnection = self.mapClientAddr2Connection( thisClientAddr )
            thisConnection.WPFlag = False
            if thisConnection:
                msg = None
                if job.getServerType() == JobServer.MAYA_NGN:
                    msg = pickle.dumps( [START_CLIENT_MSGN, jobName, JobServer.MAYA_NGN, jobPort] )
                elif job.getServerType() == JobServer.XSI_NGN:
                    msg = pickle.dumps( [START_CLIENT_MSGN, jobName, JobServer.XSI_NGN, jobPort] )
                elif job.getServerType() == JobServer._3DSMAX_NGN:
                    msg = pickle.dumps( [START_CLIENT_MSGN, jobName, JobServer._3DSMAX_NGN, jobPort] )
                elif job.getServerType() == JobServer.NUKE_NGN:
                    msg = pickle.dumps( [START_CLIENT_MSGN, jobName, JobServer.NUKE_NGN, jobPort] )
                thisConnection.sendMsg( msg )
                job.Servers.append( thisConnection )
                if thisConnection.ServerState == JobServer.SERVER_AUTOMATED_STAT:
                    self.updateServer( thisConnection, job )
                else:
                    self.updateServer( thisConnection, job, JobServer.SERVER_WAITJOB_STAT )                    
                self.insertLog( "activating the slave(s) " + thisClientAddr, 'inf' )
            else:
                print( "unexpected error on calling activateClients" )
                return 0
        return 1
            



    def activateAddedClients (self):
        """activates added clients on prestarted jobs"""
        idleServers = []
        for thisServer in MasterApp.Servers_List:
            if thisServer.ServerState == JobServer.SERVER_IDLE_STAT:
                idleServers.append( thisServer.clientAddr[0] )
        selectedServers = MasterGUI.ListboxDialog( self, "select the slave(s) to add to", idleServers, True ).get()
        MasterApp.LockThrd.acquire()
        if selectedServers:
            QSJobNames = []
            for thisJob in MasterApp.Jobs_List:
                if thisJob.JobState == JobServer.JOB_QUEUED_STAT or thisJob.JobState == JobServer.JOB_STOPPED_STAT:
                    QSJobNames.append( thisJob.JobName )
            selectedJob = MasterGUI.ListboxDialog( self, "select the job to which the slaves be added", QSJobNames, False ).get()
            if selectedJob:
                thisJob = self.mapJobName2Job( selectedJob )
                self.updateJob( thisJob, JobServer.JOB_RUNNING_STAT )
                self.activateClients( thisJob, selectedServers )
                self.insertLog( "the slave(s) " + str( selectedServers ) + " is been added to the job, " + thisJob.JobName, 'inf', 1 )
            else:
                self.insertLog( "failed to add the slave(s), " + str( selectedServers ), 'inf' )
        else:
            self.insertLog( "canceled to add the slave(s)", 'inf' )
        MasterApp.LockThrd.release()




    def stopJobs (self):
        """stopes the jobs given from GUI,
            this is called whenever <Stop Jobs> button is pressed"""
        unfinishedJobNames = []
        for thisJob in MasterApp.Jobs_List:
            if thisJob.JobState != JobServer.JOB_FINISHED_STAT and thisJob.JobState != JobServer.JOB_STOPPED_STAT:
                unfinishedJobNames.append( thisJob.JobName )
        selectedJobNames = MasterGUI.ListboxDialog( self, "select the jobs to be stopped", unfinishedJobNames, True ).get()
        MasterApp.LockThrd.acquire()
        if selectedJobNames:
            for thisJobName in selectedJobNames:
                thisJob = self.mapJobName2Job( thisJobName )
                if thisJob.JobState == JobServer.JOB_FINISHED_STAT or thisJob.JobState == JobServer.JOB_STOPPED_STAT:
                    continue
                thisJob.jobFinishedFlag = True
                self.updateJob( thisJob, JobServer.JOB_STOPPED_STAT )
                if thisJob.Servers:
                    self.stopClients( thisJob, thisJob.Servers )
            self.insertLog( "the job(s), " + str( selectedJobNames ) + " are stopped successfully", 'inf', True )
        else:
            self.insertLog( "canceled to stop the jobs", 'inf' )
        MasterApp.LockThrd.release()


            

    def makeJobsWP (self):
        """makes the jobs waited pack given from GUI,
            this is called whenever <Job WP> button is pressed"""
        unfinishedJobNames = []
        for thisJob in MasterApp.Jobs_List:
            if thisJob.JobState == JobServer.JOB_RUNNING_STAT:
                unfinishedJobNames.append( thisJob.JobName )
        selectedJobNames = MasterGUI.ListboxDialog( self, "select the jobs to be waited pack", unfinishedJobNames, True ).get()
        MasterApp.LockThrd.acquire()
        if selectedJobNames:
            for thisJobName in selectedJobNames:
                thisJob = self.mapJobName2Job( thisJobName )
                if thisJob.JobState != JobServer.JOB_RUNNING_STAT:
                    continue
                thisJob.jobFinishedFlag = True
                self.updateJob( thisJob, JobServer.JOB_WAITPACK_STAT )
                if thisJob.Servers:
                    self.makeClientsWP( thisJob, thisJob.Servers )
            self.insertLog( "the job(s), " + str( selectedJobNames ) + " are waited pack successfully", 'inf', True )
        else:
            self.insertLog( "canceled to waited pack the jobs", 'inf' )
        MasterApp.LockThrd.release()




    def makeJobsQue (self):
        """makes the jobs queued given from GUI,
            this is called whenever <Jobs Queue> is pressed"""
        jobNamesList = []
        for thisJob in MasterApp.Jobs_List:
            if thisJob.JobState == JobServer.JOB_STOPPED_STAT:
                jobNamesList.append( thisJob.JobName )
        entry = MasterGUI.EntryListboxDialog( self, "select the jobs to be queued", jobNamesList, "Enter priority", True ).get()
        MasterApp.LockThrd.acquire()
        if entry:
            selectedJobNames = entry[0]
            if selectedJobNames:
                prio = entry[1]
                if prio:
                    try:
                        newPrio = int( prio )
                    except ValueError as err:
                        self.insertLog( "wrong priority entered", 'err')
                        self.insertLog( "failed to make the jobs queued", 'inf')                
                    else:
                        for thisJobName in selectedJobNames:
                            thisJob = self.mapJobName2Job( thisJobName )
                            if thisJob.JobState != JobServer.JOB_STOPPED_STAT:
                                continue
                            thisJob.jobFinishedFlag = False
                            self.updateJob( thisJob, JobServer.JOB_QUEUED_STAT, newPrio )
                        self.insertLog( "the job(s), " + str( selectedJobNames ) + " are queued successfully", 'inf' )
                else:
                    for thisJobName in selectedJobNames:
                        thisJob = self.mapJobName2Job( thisJobName )
                        thisJob.jobFinishedFlag = False
                        self.updateJob( thisJob, JobServer.JOB_QUEUED_STAT )        
            else:
                self.insertLog( "no jobs are seletced", 'inf' )
                self.insertLog( "failed to make the jobs queued", 'inf' )
        else:
            self.insertLog( "canceled to make the jobs queued", 'inf' )
        MasterApp.LockThrd.release()


            

    def stopClients (self, job = None, servers = None):
        """stopes the clients either given from GUI or by another method,
            this is also called whenever <Stop Slaves> button is pressed, 
            job : the job to which servers are dedicated,
            servers : the servers that are to be closed"""
        if not job:
            runningServerAddrs = []
            for thisServer in MasterApp.Servers_List:
                if thisServer.ServerState != JobServer.SERVER_IDLE_STAT:
                    runningServerAddrs.append( thisServer.clientAddr[0] )
            selectedServerAddrs = MasterGUI.ListboxDialog( self, "select the slaves to be stopped", runningServerAddrs, True ).get()
            MasterApp.LockThrd.acquire()
            if selectedServerAddrs:
                for thisServerAddr in selectedServerAddrs:
                    thisServer = self.mapClientAddr2Connection( thisServerAddr )
                    if thisServer.ServerState == JobServer.SERVER_IDLE_STAT:
                        continue
                    job = thisServer.ServerJob
                    msg = pickle.dumps( [STOP_CLIENT_MSGN, job.JobName, job.getServerType()] )
                    thisServer.sendMsg( msg )
                    job.Servers.remove( thisServer )
                    self.updateServer( thisServer, 0, JobServer.SERVER_IDLE_STAT )
                if not job.Servers:
                    self.updateJob( job, JobServer.JOB_STOPPED_STAT )
                    JobServer.jobFinishedFlag = True
                self.insertLog( "the slaves, " + str( selectedServerAddrs ) + " are stopped successfully" )
            else:
                self.insertLog( "Failed to stop the slaves", 'inf' )
            MasterApp.LockThrd.release()
        else:
            for thisServer in servers[:]:
                self.updateServer( thisServer, 0, JobServer.SERVER_IDLE_STAT )
                job.Servers.remove( thisServer )
                msg = pickle.dumps( [STOP_CLIENT_MSGN, job.JobName, job.getServerType()] )
                thisServer.sendMsg( msg )
                self.insertLog( "the slave, " + thisServer.clientAddr[0] + " is stopped" )
            if not job.Servers:
                self.updateJob( job, JobServer.JOB_STOPPED_STAT )
                JobServer.jobFinishedFlag = True


        

    def makeClientsWP (self, job = None, servers = None):
        """makes the clients waited pack either given from GUI or by another method,
            this is also called whenever <Slaves WP> button is pressed, 
            job : the job to which servers are dedicated,
            servers : the servers that are to be waited pack"""
        if not job:
            runningServerAddrs = []
            for thisServer in MasterApp.Servers_List:
                if thisServer.ServerState == JobServer.SERVER_AUTOMATED_STAT or thisServer.ServerState == JobServer.SERVER_WAITJOB_STAT:
                    runningServerAddrs.append( thisServer.clientAddr[0] )
            selectedServerAddrs = MasterGUI.ListboxDialog( self, "select the slaves to be waited pack", runningServerAddrs, True ).get()
            MasterApp.LockThrd.acquire()
            if selectedServerAddrs:
                for thisServerAddr in selectedServerAddrs:
                    thisServer = self.mapClientAddr2Connection( thisServerAddr )
                    if thisServer.ServerState != JobServer.SERVER_AUTOMATED_STAT and thisServer.ServerState != JobServer.SERVER_WAITJOB_STAT:
                        continue
                    thisServer.WPFlag = True
                    self.updateServer( thisServer, None, JobServer.SERVER_WAITPACK_STAT )
                job = thisServer.ServerJob
                if self.checkJobServersStates( job, JobServer.SERVER_WAITPACK_STAT ):
                    self.updateJob( job, JobServer.JOB_WAITPACK_STAT )
                self.insertLog( "the slaves, " + str( selectedServerAddrs ) + " are waited pack successfully" )
            else:
                self.insertLog( "Failed to make the slaves waited pack", 'inf' )
            MasterApp.LockThrd.release()
        else:
            for thisServer in servers[:]:
                thisServer.WPFlag = True
                self.updateServer( thisServer, None, JobServer.SERVER_WAITPACK_STAT )
            
        



    def makeClientsAuto (self):
        """makes the clients given by GUI auto,
            this is called whenever <Slaves Auto> button is pressed"""
        serverAddrsList = []
        for thisServer in MasterApp.Servers_List:
            if thisServer.ServerState != JobServer.SERVER_AUTOMATED_STAT:
                serverAddrsList.append( thisServer.clientAddr[0] )
        selectedServerAddrs = MasterGUI.ListboxDialog( self, "select the slaves to be automated", serverAddrsList, True ).get()
        MasterApp.LockThrd.acquire()
        if selectedServerAddrs:
            for thisServerAddr in selectedServerAddrs:
                thisServer = self.mapClientAddr2Connection( thisServerAddr )
                if thisServer.ServerState == JobServer.SERVER_AUTOMATED_STAT:
                    continue
                thisServer.WPFlag = False
                if thisServer.ServerState == JobServer.SERVER_IDLE_STAT:
                    self.updateServer( thisServer, None, JobServer.SERVER_AUTOMATED_STAT )
                    if not self.manageServer( thisServer ):
                        self.updateServer( thisServer, None, JobServer.SERVER_IDLE_STAT )
                        self.insertLog( "there is no precedent job to get to the idle slave, " + thisServer.clientAddr[0], 'inf' )
                    else:
                        self.insertLog( "the slave, " + thisServer.clientAddr[0] + " is automated", 'inf' )                        
                else:
                    self.updateServer( thisServer, None, JobServer.SERVER_AUTOMATED_STAT )
                    self.updateJob( thisServer.ServerJob, JobServer.JOB_RUNNING_STAT )
                    self.insertLog( "the slave, " + thisServer.clientAddr[0] + " is automated", 'inf' )
        else:
            self.insertLog( "Failed to make the slaves automated", 'inf' )
        MasterApp.LockThrd.release()


            

    def makeClientsWJ (self):
        """makes the clients given by GUI waited job,
            this is called whenever <Slaves WJ> button is pressed"""
        serverAddrsList = []
        for thisServer in MasterApp.Servers_List:
            if thisServer.ServerState == JobServer.SERVER_AUTOMATED_STAT or thisServer.ServerState == JobServer.SERVER_WAITPACK_STAT:
                serverAddrsList.append( thisServer.clientAddr[0] )
        selectedServerAddrs = MasterGUI.ListboxDialog( self, "select the slaves to be waited job", serverAddrsList, True ).get()
        MasterApp.LockThrd.acquire()
        if selectedServerAddrs:
            for thisServerAddr in selectedServerAddrs:
                thisServer = self.mapClientAddr2Connection( thisServerAddr )
                if thisServer.ServerState != JobServer.SERVER_AUTOMATED_STAT and thisServer.ServerState != JobServer.SERVER_WAITPACK_STAT:
                    continue
                thisServer.WPFlag = False
                self.updateServer( thisServer, None, JobServer.SERVER_WAITJOB_STAT )
                self.updateJob( thisServer.ServerJob, JobServer.JOB_RUNNING_STAT )
            self.insertLog( "the slaves, " + str( selectedServerAddrs ) + " are waited job", 'inf' )
        else:
            self.insertLog( "failed to make the slaves waited job", 'inf' )
        MasterApp.LockThrd.release()
                    



    def checkJobServersStates (self, job, state):
        """checks if all the dedicated servers of the given job have the same state,
            job : the job that its servers need to be checked,
            state : the state that needs to be checked"""
        for thisServer in job.Servers:
            if thisServer.ServerState != state:
                return False
        return True
                

    
    def getUnusedPort (self):
        """ generates a random open port """
        usedPorts = []
        for jp in MasterApp.Jobs_List:
            usedPorts.append( jp.Port )
        while True:
            unusedPort = random.randint( 6001, 65535 )
            if unusedPort in usedPorts:
                continue
            else:
                s = socket.socket()
                if s.connect_ex( (MasterApp.HOST_NAME, unusedPort) ):
                    return unusedPort
    


    def exitApp (self):
        """exits MasterApp"""
        sys.exit( 0 )

    
