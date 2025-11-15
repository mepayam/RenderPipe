# address of master machine
# change this address to <IP address> or <computer name> of master machine
#
SERVER_ADDR = '192.168.0.1'

#--------------------------------------------

# port number of the connection on which master app connects
# change this port number to the port number of master app
#
MASTER_PORT = 6000

#--------------------------------------------

# buffer size of send/recv
# changing is not recommended
#
BUFFER_SIZE = 1024

#--------------------------------------------

# delay time to receive the render batch command
# changing is not recommended
#
WAIT_TILL_RECV_BATCH = 1

#--------------------------------------------

# delay time to start the render batch command
# changing is not recommended
#
WAIT_TILL_RUN_BATCH = 2

#--------------------------------------------

# process names of each job type
#
MAYA_BATCH = 'mayabatch.exe'
XSI_BATCH = 'xsibatch.exe'
_3DSMAX_BATCH = '3dsmaxcmd.exe'
NUKE_BATCH = 'nuke6.2.exe'

#--------------------------------------------

# command names of each job type
#
MAYA_BATCH_COMMAND = 'render.exe'
XSI_BATCH_COMMAND = 'xsibatch.bat'
_3DSMAX_BATCH_COMMAND = '3dsmaxcmd.exe'
NUKE_BATCH_COMMAND = 'nuke6.2.exe'

#--------------------------------------------

# root paths of the applications of each job type
# change it if the root path of the application installation is different on your machine
# r"<path>"   :  replace <path> by the changed one, ->no backslash(\) at the end<-
#
MAYA_ROOT_PATH = r"C:\Program Files\Autodesk\Maya 2011 Subscription Advantage Pack\bin"
XSI_ROOT_PATH = r"C:\Program Files\Autodesk\Softimage 2011 Subscription Advantage Pack\Application\bin"
_3DSMAX_ROOT_PATH = r"C:\Program Files\Autodesk\3ds Max 2011"
NUKE_ROOT_PATH = r"C:\Program Files\Nuke6.2v2"

#--------------------------------------------

# log files root path
# default log path is set to your user profile, you can override it with your path
# r"<path>"   :  replace <path> by the changed one, ->no backslash(\) at the end<-
#
LOG_ROOT_PATH = r""

