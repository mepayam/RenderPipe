"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
#########################################################################
    JobServer handles the both job function and server side of RenderPipe. 
    Copyright (C) 2012 Hadi Saraf , Payam Memar

    JobServer is part of RenderPipe.

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




import sys
import time
import socket
import pickle
import threading
import tkinter

import HiStreamServer
import MasterConfig



# sets the host name as server
#
HOST_NAME = socket.gethostname()


# types of job engines (servers)
#
MAYA_NGN = 'Maya'
XSI_NGN = 'XSI'
_3DSMAX_NGN = '3DSMax'
NUKE_NGN = 'Nuke'


# messages for communication purposes, master/server
#
JOB_FINISHED_MSG = 1
SERVER_FINISHED_MSG = 2
PACK_SENT_MSG = 3
PRESENT_MSG = 4


# message strings for networking communications of server and clients
#
CLIENT_READY_MSGN = '11111111'
CLIENT_CLOSE_MSGN = '00000000'


# states of jobs
#
JOB_RUNNING_STAT = 'R'
JOB_QUEUED_STAT = 'Q'
JOB_FINISHED_STAT = 'F'
JOB_STOPPED_STAT = 'S'
JOB_WAITPACK_STAT = 'WP'


# states of servers
#
SERVER_AUTOMATED_STAT = 'A'
SERVER_IDLE_STAT = 'I'
SERVER_WAITJOB_STAT = 'WJ'
SERVER_WAITPACK_STAT = 'WP'



class Connection( HiStreamServer.RequestPack ):
    """class to handle the connections (servers)"""
    BUFFER_SIZE = MasterConfig.BUFFER_SIZE      
    def handle (self):
        while True:
            # Receive the message from all connections
            # Check the closing condition of the connection
            # If closed, then terminates handle() method and falls into the finish() method and calls closeCallback()
            #
            if not self.verifyConnection( self.recvMsg() ):
                return

      

class JobServer( HiStreamServer.MultiStreamServer ):
    """class for managing the jobs,
        one instance of this class is constructed for each job"""

    Lock = threading.Lock()
    
    def __init__ (self, jobName = None,
                  jobState = None, jobPrio = None, 
                  startFrame = None, endFrame = None, packSize = None, 
                  sourceFile = None, destPath = None, outName = None,
                  master = None, port = None, servers = None,
                  insertLogCallback = None, insertRLogCallback = None,
                  messageCallback = None):
        """gets the arguments and sets the data to construct the job"""
        
        HiStreamServer.MultiStreamServer.__init__( self, (HOST_NAME, port ),
                                                            Connection,
                                                                self.onConnect,
                                                                    self.onClose,
                                                                        self.onRecv )
        self.JobName = jobName              # JobName
        self.JobState = jobState            # JobState
        self.JobPrio = jobPrio              # JobPriority
        self.StartFrame = startFrame        # StartFrame
        self.EndFrame = endFrame            # EndFrame
        self.PackSize = packSize            # PackSize
        self.SourceFile = sourceFile        # SourceFile
        self.ProjectPath = destPath         # ProjectPath
        self.OutputName = outName           # OutputName
        self.Master = master                # Master
        self.Port = port                    # Port
        self.Servers = servers              # Servers
        
        self.jobFinishedFlag = False
        
        self.jobPackNum = 0

        self.insertLogCallback = insertLogCallback        # insertLogCallback
        self.insertRLogCallback = insertRLogCallback      # insertLogCallback
        
        self.messageCallback = messageCallback            # messageCallback

        #self.PACK_SIZE = MasterConfig.PACK_SIZE           # PACK_SIZE

        #self.Lock = threading.Lock()        # Lock
        
        self.Packs_list = []                # list of packs related to one job
        
        self.setPacksList()                 # sets the pack list

        

    def runServer (self):
        """ runs the thread server"""
        #threading.Thread( target = self.handleRequestAlways, args = () ).start()
        self.handleRequestAlways()



    def setPacksList (self):
        """ sets the packs to Packs_List, 
            [(s1, e1), (s2, e2), ... (sn, en)]"""
        end = self.StartFrame
        packSize = self.PackSize
        indx = 0
        while (end <= self.EndFrame):
            self.Packs_list.append( (end, end + self.PackSize - 1) )
            end += packSize
            indx += 1
        self.Packs_list[indx - 1] = (end - self.PackSize, self.EndFrame)
        self.Packs_list.reverse()
        


    def onRecv (self, connection, msg):
        """this is called whenever the server recieves a message,
            connection : the receiving connection,
            msg : the received message"""
        JobServer.Lock.acquire()     # locks the thread to prevent the data corruption
        message = pickle.loads( msg )
        if (message == CLIENT_READY_MSGN):
            self.managePack( connection )
        JobServer.Lock.release()     # releases the lock


        
    def managePack (self, client):
        """gathers the pack information and dispatches it,
            client : the client to which the packet is to be dispatched"""
        if self.Packs_list:
            if not self.messageCallback( PRESENT_MSG, client, self ):
                nextPack = self.Packs_list.pop()
                packStart = nextPack[0]
                packEnd = nextPack[1]
                packNum = self.dispatchRenderCmd( self.JobName, packStart, packEnd, self.SourceFile, self.ProjectPath, self.OutputName, client )
                self.messageCallback( PACK_SENT_MSG, client, self, packNum )
        else:
            self.jobFinishedFlag = True
            self.messageCallback( SERVER_FINISHED_MSG, client, self )
            #time.sleep( 1 )
            if not self.Servers:
                self.messageCallback( JOB_FINISHED_MSG, self )
                    
                    


    def closeClient (self, thisClient):
        """closes the client,
            thisClient : the client that is to be closed"""
        clientCloseMsg = pickle.dumps( CLIENT_CLOSE_MSGN )
        thisClient.sendMsg( clientCloseMsg )
        self.Servers.remove( thisClient )
        self.insertLogCallback( "The client " + str( thisClient.clientAddr[0] ) + " is been finished", 'inf', 1 )
            


    def dispatchRenderCmd (self, jobName, packStart, packEnd, sourcePath, destinationDir, outputName, thisClient ):
        """dispathed the packets to the clients,
            must be overriden for each server type, 
            arguments are self explanatory"""
        pass


    def onConnect (self, client):
        """this is called whenever a connection is established,
            client : the connected client"""
        #print( tkinter.END, "connection established from " + str( client.clientAddr[0] ) )
        pass

    def onClose (self, client):
        """this is called whenever a connection is closed,
            client : the closed client"""
        #print( tkinter.END, "connection closed by " + str( client.clientAddr[0] ) )
        pass
        


    def getServerType (self):
        """returns the server type,
            must be overriden for each server type"""
        pass


    def killServer (self):
        """exits the job server"""
        sys.exit( 0 )

