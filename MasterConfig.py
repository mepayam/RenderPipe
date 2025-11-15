# the port number on which master connects
# change it to whatever open port if you need to run more than one master on this machine
#
MASTER_PORT = 6000

#--------------------------------------------

# the size of buffer to receive the messages
# changing is not recommended
# 
BUFFER_SIZE = 1024

#--------------------------------------------

# the minimm and maximum range of the scale slider (start/end frame)
#
MIN_FRAME = -100000
MAX_FRAME = 100000

#--------------------------------------------

# the connction request size of the server
# changing is not recommended
#
REQUEST_SIZE = 100

#--------------------------------------------

# the max number of job name characters
#
MAX_JOBNAME_CHARS_COUNT = 15

#--------------------------------------------

# the max number of the job progressbar dashes [======   ]
#
MAX_PROGRESS_DASH_COUNT = 12

#--------------------------------------------

# the number of spaces between the job name and the job state
#
JNAME_JSTATE_SPACES_COUNT = 10

#--------------------------------------------

# the number of spaces between the slave name and the slave state
#
SNAME_SSTATE_SPACES_COUNT = 10

#--------------------------------------------

# the time wait between the server and slave activation
# server activation...<wait>...slave activation
# changing is not recommended
#
WAITE_SERVER_SLAVE_ACTIVATION = 1

#--------------------------------------------

# the time delay between slaves connection establishments
# changing is not recommended
#
SLAVE_CONNECTION_DELAY = 1

#--------------------------------------------

# the colors of the GUI of the master controller
#
# the background and foreground colors of the slaves box
#
SLAVESBOX_BG_COLOR = "#333333"
SLAVESBOX_FG_COLOR = "#22CC33"

#--------------------------------------------

# the background and foreground colors of the jobs box
#
JOBSBOX_BG_COLOR = "#333333"
JOBSBOX_FG_COLOR = "#AAAACC"

#--------------------------------------------

# the background and foreground colors of the info box
#
INFOBOX_BG_COLOR = "#333333"
INFOBOX_FG_COLOR = "#EEEEEE"

#--------------------------------------------

# the background and foreground colors of the log box
#
LOGBOX_BG_COLOR = "#333333"
LOGBOX_FG_COLOR = "#EEEEEE"

#--------------------------------------------

# the labels background colors
#
LABELS_BG_COLOR = "#EEEEEE"
