"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
#########################################################################
    JobClient handles the both job function and client side of RenderPipe. 
    Copyright (C) 2012 Hadi Saraf , Payam Memar

    JobClient is part of RenderPipe.

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
import os
import pickle
import socket
import tkinter
import subprocess
import threading
import time

import HiStreamClient
import SlaveConfig


# message strings for networking communications of server and clients
#
CLIENT_READY_MSGN = '11111111'
CLIENT_CLOSE_MSGN = '00000000'


# types of job engines (servers)
#
MAYA_NGN = 'Maya'
XSI_NGN = 'XSI'
_3DSMAX_NGN = '3DSMax'
NUKE_NGN = 'Nuke'


class JobClient( HiStreamClient.StreamClient ):
    """ class to manage run the commands from the job manager """
    

    def __init__ (self, jobName, serverName, port):
        """ initiate the connection """
        self.JobName = jobName
        HiStreamClient.StreamClient.__init__( self, (serverName, port) )
        self.RCMD = None
        self.connectOnce()


    def connectCallback (self, connection):
        """ this is called whenever a connection is established, 
            runs the client manager, 
            connection : the established connection"""
        self.runClientManager()


    def recvCallback (self, connection, msg):
        """ this is called whenever a connection recieves a messagae, 
            sets the RCMD flag to render command,
            connection : the receiving connection,
            msg : the received message"""
        message = pickle.loads( msg )
        if message == CLIENT_CLOSE_MSGN:
            sys.exit( 0 )
        renderCmd = message
        self.RCMD = renderCmd


    def closeCallback (self, connection):
        """closes the client,
            connection : the client side of connection object"""
        sys.exit( 0 )   # successful termination


    def runClientManager (self):
        """runs the thread of the clientManager"""
        threading.Thread( target = self.clientManager, args = () ).start()


    def clientManager (self):
        """ the core function of client side, 
            must be overriden for each client (job) type """
        pass



    def runBatch (self, renderCmd):
        """ runs the batch process, 
            renderCmd : the string command of batch render"""
        try:
            renderProc = os.popen( renderCmd, 'r' )
            logPath = ""
            if SlaveConfig.LOG_ROOT_PATH:
                logPath = SlaveConfig.LOG_ROOT_PATH + "\\" + self.JobName + ".txt"
            else:
                logPath = os.environ.get( "RPIPE_TEMP_PATH" ) + self.JobName + ".txt"
            try:
                logFile = open( logPath, 'a+' )
            except IOError as err:
                print( "error on writing log  --  " + str( err ) )
            else:
                logFile.write( renderProc.read() )
                logFile.close()
            self.RCMD = None
        except Exception as err:
            print( "an unexpected error occured while runnung the batch render  --  " + str( err ) )

