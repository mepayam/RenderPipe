"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
#########################################################################
    HiStreamServer handles the core server side connections (TCP) of RenderPipe. 
    Copyright (C) 2012 Hadi Saraf , Payam Memar

    HiStreamServer is part of RenderPipe.

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
import threading
import time


def handleError (err, emsg, addr = None):
    """writes errors"""
    print ('-' * 50)
    print ('-- Exception happend --')
    print (emsg)
    print (err)
    print (addr)
    print ('-' * 50)


def showLog (log):
    """Shows logs"""
    print ('-' * 40)
    print (log)
    print ('-' * 40)
    
        

class StreamServer:
    """Class server for handling single request, no threading support, 
        one instance of this class must be created for one server
    """

    # global attributes of server
    #
    addrFamily = socket.AF_INET
    sockType = socket.SOCK_STREAM
    requestQSize = 5
    

    def __init__ (self, serverAddr, connection, connectCallback, closeCallback, recvCallback):
        """Construcotr, get infos from user to create a server."""
        # Get the callback functions
        self.connection = connection
        self.connectCallback = connectCallback
        self.closeCallback = closeCallback
        self.recvCallback = recvCallback
        self.serverAddr = serverAddr
        # Create the server socket
        self.serverSock = socket.socket( self.addrFamily, self.sockType )
        # Bind ad listen the server socket
        self.serverBind()
        self.serverListen()
        

    def serverBind (self):
        """binds the server socket"""
        self.serverSock.bind( self.serverAddr )
        self.serverAddr = self.serverSock.getsockname()


    def serverListen (self):
        """listens for incoming connections"""
        self.serverSock.listen( self.requestQSize )


    def handleRequestAlways (self):
        """calls handleRequest method to handle the requests forever"""
        while True:
            self.handleRequest()


    def handleRequest (self):
        """handles the requests and creates a RequestPack for each request"""
        try:
            # Call to accept the incoming connection
            clientSock, clientAddr = self.serverAccept()
            
        except socket.error as err:
            emsg = '-- While accpeting the request --'
            handleError( err, emsg, clientAddr )
            errf = open( "c:\\err_log.txt", "w" )
            errf.write( err )
            errf.close()
            return

        # Prompt the request to user and call to make the RequestPack object
        self.promptRequest( clientAddr )
        self.makeRequestPack( clientSock, clientAddr )


    def closeRequest (self, clientSock, clientAddr):
        """closes the request that needs to be closed"""
        clientSock.close()
        #showLog( '<' + clientAddr[0] + '>' + ' closed now' )
        

    def promptRequest (self, clientAddr):
        """"prompts the user for the request"""
        #showLog( 'A connection request from <' + clientAddr[0] + '>' )
        pass


    def makeRequestPack (self, clientSock, clientAddr):
        """creates a request pack object"""
        try:
            # Instantiate a request pack
            self.connection ( clientSock,
                              clientAddr,
                              self,
                              self.connectCallback,
                              self.closeCallback,
                              self.recvCallback)
            # Close the request after finishing the job
            self.closeRequest( clientSock, clientAddr )
        except Exception as err:
            emsg = '-- While packing the request --'
            handleError( err, emsg )
            self.closeRequest( clientSock, clientAddr )


    def serverAccept (self):
        """Accept the incoming connection"""
        return self.serverSock.accept()
    


        

class RequestPack:
    """an instance of this class is made whenever a server becames established"""
    # Global features of requests
    REQPACKS = []   # Request Packs list
    BUFFER_SIZE = 1024
    
    Lock = threading.Lock()
    
    def __init__ (self,
                  sock,
                  addr,
                  server,
                  connectCallback,
                  closeCallback,
                  recvCallback):
        """Constructor, Get all data from caller method and handles itself
            by calling three methods, 
                - setup
                - handle
                - finish
        """

        # Append the request pack to REQPACKS and set data
        self.connectCallback = connectCallback
        self.closeCallback = closeCallback
        self.recvCallback = recvCallback
        self.server = server
        self.clientSock = sock
        self.clientAddr = addr

        self.exitFlag = False

        try:
            # Call to handlers methods
            RequestPack.Lock.acquire()
            self.setup()
            RequestPack.Lock.release()

            self.handle()

            RequestPack.Lock.acquire()
            self.finish()          # Finish after setup() and handle() methods do the job
            RequestPack.Lock.release()
        except Exception as err:
            try:
                self.finish()   # Finish after setup() and handle() methods do the job
                                #       incorrectly (disconnection, exit...)
                #showLog( '<' + self.clientAddr[0] + '> disconnected' )
            finally:    # Finally terminate 
                return
                
                
    def setup (self):
        """initiates the established connection"""
        RequestPack.REQPACKS.append( self )
        try:
            self.connectCallback( self )
        except TypeError as err:
            handleError( err, '-- While setting the request up--', self.clientAddr )
            pass


    def handle (self):
        """handles the main functionality of connection, 
            always overriden"""
        pass
    
    
    def finish (self, callClose = True):
        """finishes the closed connection"""
        RequestPack.REQPACKS.remove( self )
        try:
            if callClose:
                self.closeCallback( self )
        except TypeError as err:
            handleError( err, '-- While finishing the request --', self.clientAddr )
            pass

                
    def sendMsg (self, msg):
        """sends the messages"""
        totalSent = 0
        msgLen = len( msg )
        while totalSent < msgLen:
            sent =  self.clientSock.send( msg[totalSent:] )
            if sent == 0:
                self.finish()
                raise (RuntimeError, "socket connection broken")
            totalSent = totalSent + sent


    def recvMsg (self):
        """receives the messages"""
        msg = self.clientSock.recv( self.BUFFER_SIZE )
        if self.verifyConnection( msg ):
            try:
                self.recvCallback( self, msg )
                return msg
            except TypeError as err:
                handleError( err, '-- While recving the request --', self.clientAddr )
                return msg
                        

    def verifyConnection (self, msg):
        """checks if connection is closed or not,
            msg : the received message"""
        if not msg:
            return False
        return True


    def connectCallback (self, connection):
        """called whenever a connection is made,
            connection : the made connection"""
        pass


    def closeCallback (self, connection):
        """called whenever a connection is closed,
            connection : the closed connection"""
        pass


    def recvCallback (self, connection, msg):
        """called whenever a connection receives a message,
            connection : the receiving connection,
            msg : the received message"""
        pass





class ServerThreadingMixIn:
    """this class makes the server concurrent"""
    def makeRequestPackThread (self, clientSock, clientAddr):
        """the thread of makeRequestPack() method of StreamServer class"""
        try:
            self.connection ( clientSock,
                              clientAddr,
                              self,
                              self.connectCallback,
                              self.closeCallback,
                              self.recvCallback)
            self.closeRequest( clientSock, clientAddr )
        except Exception as err:
            emsg = '-- While packing the request --'
            handleError( err, emsg, clientAddr )
            self.closeRequest( clientSock, clientAddr )


    def makeRequestPack (self, clientSock, clientAddr):
        """starts a new thread for every request"""
        rPackThr = threading.Thread( target = self.makeRequestPackThread,
                                    args = (clientSock, clientAddr) )
        rPackThr.start()        

        



class MultiStreamServer( ServerThreadingMixIn, StreamServer ):
    """this class handles multiple connection"""
    pass

