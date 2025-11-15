"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
#########################################################################
    XSIClient handles the client side of jobs of type XSI. 
    Copyright (C) 2012 Hadi Saraf , Payam Memar

    XSIClient is part of RenderPipe.

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
import pickle
import time

import JobClient
import SlaveConfig


class XSIClient( JobClient.JobClient ):
    """class to handle the client side of jobs"""

    def clientManager (self):
        """checks the tasklist and runs render batch command"""
        while True:
            taskList = os.popen( 'tasklist' ).read() 
            try:
                taskList.index( SlaveConfig.XSI_BATCH )
                time.sleep( 2 )
            except ValueError as err:
                readyMsg = pickle.dumps( JobClient.CLIENT_READY_MSGN )
                self.sendMsg( readyMsg )
                time.sleep( SlaveConfig.WAIT_TILL_RECV_BATCH )
                while True:
                    if self.RCMD:
                        renderBatchPath = '"' + SlaveConfig.XSI_ROOT_PATH + "\\" + SlaveConfig.XSI_BATCH_COMMAND + '"' + self.RCMD
                        self.runBatch( renderBatchPath )
                        break
                    time.sleep( SlaveConfig.WAIT_TILL_RUN_BATCH )


