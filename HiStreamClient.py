"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
#########################################################################
    HiStreamClient handles the core client side connections (TCP) of RenderPipe. 
    Copyright (C) 2012 Hadi Saraf , Payam Memar

    HiStreamClient is part of RenderPipe.

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


import socket
import time


REPEATED_CONNECTION_DELAY = 2
REPEATED_RECV_DELAY = 1


def handleError (err, emsg, addr = None):
    """writes errors"""
    print ('-' * 50)
    print ('-- Exception happend --')
    print (emsg)
    print (err)
    print (addr)
    print ('-' * 50)


class StreamClient:

    """ base class to handle the client side of the connection """
    # global attributes of client
    #
    ADDR_FAMILY = socket.AF_INET
    SOCK_TYPE = socket.SOCK_STREAM
    BUFFER_SIZE = 1024
    HOST_NAME = socket.gethostname()
    

    def __init__ (self, serverAddr):
        """ initiates server address and builds new socket """
        self.serverAddr = serverAddr
        self.buildNewSock()


    def buildNewSock (self):
        """ builds new socket """
        self.clientSock = socket.socket( StreamClient.ADDR_FAMILY, StreamClient.SOCK_TYPE )


    def connectOnce (self):
        """ connects just one time,
            if it connects then calls connectCallback and recvMsgPermanent methods"""
        try:
            self.clientSock.connect( self.serverAddr )
            self.connectCallback( self )
            self.recvMsgPermanent()
        except socket.error as err:
            pass
            #emsg = '-- While connecting --'
            #handleError( err, emsg, self.serverAddr )


    def connectPermanent (self):
        """ connects repeatedly """
        while True:
            self.connectOnce()
        time.sleep( REPEATED_CONNECTION_DELAY )
        
    
    def recvMsgPermanent (self):
        """ recieves messages permanently """
        while True:
            try:
                msg = self.clientSock.recv( StreamClient.BUFFER_SIZE )
                if self.verifyConnection( msg ):
                    self.recvCallback( self, msg )
                else:
                    self.closeCallback( self )
                    self.buildNewSock()
                    return
            except socket.error as err:
                self.closeCallback( self )
                self.buildNewSock()
                return
            except Exception as err:
                self.closeCallback( self )
                #handleError( err, "while excecuting the recvCallback()" )
                self.buildNewSock()
                return
            time.sleep( REPEATED_RECV_DELAY )
                    

    def sendMsg (self, msg):
        """ sends the messages, 
            msg : the message that are to be sent"""
        totalSent = 0
        #msg = bytes( msg, "ascii" )
        msgLen = len( msg )
        while totalSent < msgLen:
            sent =  self.clientSock.send( msg[totalSent:] )
            if sent == 0:
                self.finish()
                raise (RuntimeError, "socket connection broken while sending")
            totalSent = totalSent + sent


    def closeConnection (self):
        """ closes the connection """
        self.clientSock.close()
        self.closeCallback()


    def connectCallback (self, connection):
        """ this is called whenever a connection is established, 
            connection : the established connection"""
        pass


    def closeCallback (self, connection):
        """ this is called whenever a connection is closed,
            connection : the closed connection"""
        pass


    def recvCallback (self, connection, msg):
        """ this is called whenever a connection revieves a message,
            msg : the received message"""
        pass


    def verifyConnection (self, msg):
        """ verifies if the connection is closed or not """
        if not msg:
            return False
        return True


