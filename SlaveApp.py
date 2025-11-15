"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
#########################################################################
    SlaveApp handles the core slave function of RenderPipe. 
    Copyright (C) 2012 Hadi Saraf , Payam Memar

    SlaveApp is part of RenderPipe.

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
import subprocess
import time

import HiStreamClient
import SlaveConfig

import JobClient


# message strings for networking\ 
# communication of master/slave connections
#
EXIT_SLAVE_MSGN =       '01010101'
START_CLIENT_MSGN =     '10011001'
STOP_CLIENT_MSGN =      '01100110'
STPWP_CLIENT_MSGN =     '00110011'
FINISH_CLIENT_MSGN =    '11001100'



class SlaveApp( HiStreamClient.StreamClient ):
    """class to handle the slave side of connections,
        inherited from HiStreamClient.StreamClient"""
    def __init__ (self):
        """ initiate the connection """
        HiStreamClient.StreamClient.__init__( self, (SlaveConfig.SERVER_ADDR, SlaveConfig.MASTER_PORT) )
        
    def connectCallback (self, connection):
        """ this is called whenever a connection is established,
            connection : the established conection object"""
        print( "the slave connection is established" )

    def closeCallback (self, connection):
        """ this is called whenever a connection is closed,
            connection : the closed connection"""
        print( "the slave connection is closed" )

    def recvCallback (self, connection, msg):
        """ this is called whenever a connection recieves a message, 
            connection : the receiving connection,
            msg : the received message"""
        cmd = pickle.loads( msg )
        if cmd[0] == START_CLIENT_MSGN:
            print( "Running the client.." )
            self.runClient( cmd[1], cmd[2], cmd[3] )
        elif cmd[0] == STOP_CLIENT_MSGN:
            print( "Closing the client.." )
            self.closeClient( cmd[1], cmd[2], True )
        elif cmd[0] == STPWP_CLIENT_MSGN:
            print( "Closing the client.." )
            self.closeClient( cmd[1], cmd[2], False )
        elif cmd[0] == FINISH_CLIENT_MSGN:
            print( "Finishing the client.." )
            self.closeClient( cmd[1], cmd[2], False)
        elif cmd[0] == EXIT_SLAVE_MSGN:
            print( "Exiting the slave.." )
            sys.exit( 0 )



    def runClient (self, jobName, serverType, port):
        """starts the client task based on job type,
            jobName : the name of job that has to be start,
            serverType : the type of the server (job) to start,
            port : the port number on which job must start"""
        try:
            clientCmd = "ClientProc.exe " + str( jobName ) + " " + str( serverType ) + " " + str( port )
            self.clientProc = subprocess.Popen( clientCmd )   # opens the process of the client
        except Exception as err:
            print( "an error occured while opening the client process -> " + str( err ) )
        else:
            print( "the job, " + jobName + " of type " + serverType + " started on port, " + str( port ) )



    def closeClient (self, jobName, serverType, killBatchFlag):
        """closed the clietn side and the batch render process if needed,
            jobName : the name of job to be closed,
            serverType : the type of server (job),
            killBatchFlag : the flag that tells if batch render process has to be closed or not"""
        if self.clientProc:
            self.clientProc.kill()      # kills the client process
            if killBatchFlag:
                taskListFile = os.popen( "tasklist" )
                taskList = taskListFile.read()
                if serverType == JobClient.MAYA_NGN:
                    if SlaveConfig.MAYA_BATCH in taskList:
                        os.system( "taskkill /T /F /IM " + SlaveConfig.MAYA_BATCH )       # kill the mayabatch.exe process
                elif serverType == JobClient.XSI_NGN:
                    if SlaveConfig.XSI_BATCH in taskList:
                        os.system( "taskkill /T /F /IM " + SlaveConfig.XSI_BATCH )        # kill the mayabatch.exe process
                elif serverType == JobClient._3DSMAX_NGN:
                    if SlaveConfig._3DSMAX_BATCH in taskList:
                        os.system( "taskkill /T /F /IM " + SlaveConfig._3DSMAX_BATCH )        # kill the mayabatch.exe process
                elif serverType == JobClient.NUKE_NGN:
                    if SlaveConfig.NUKE_BATCH in taskList:
                        os.system( "taskkill /T /F /IM " + SlaveConfig.NUKE_BATCH )    # kill the mayabatch.exe process
                #os.close( taskListFile )
            print( "the client has been closed" )
        self.clientProc = None





