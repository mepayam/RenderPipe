"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
#########################################################################
    _3DSMaxServer handles the jobs of type 3DSMax. 
    Copyright (C) 2012 Hadi Saraf , Payam Memar

    _3DSMaxServer is part of RenderPipe.

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



import pickle

import JobServer
import MasterConfig
        

class _3DSMaxServer( JobServer.JobServer ):
    """class for handling the jobs of type 3DSMax"""

    def getServerType (self):
        """returns the type of job"""
        return JobServer._3DSMAX_NGN

    
    def dispatchRenderCmd (self, jobName, packStart, packEnd, sourcePath, projectDir, outputName, thisClient ):
        """dispatches the packets to clients"""
        renderCmd = ' -start=' + str( packStart ) + ' -end=' + str( packEnd ) +\
                        ' -outputName ' + projectDir + '/' + outputName + ' ' + sourcePath
        
        renderCmd = renderCmd.replace( '/', '\\' )
            
        renderCmd = pickle.dumps( renderCmd )
        thisClient.sendMsg( renderCmd )
        self.insertRLogCallback( jobName + "  ->  " + thisClient.clientAddr[0] + "     --     " + str( packStart ) + "-" + str( packEnd ) + "  ->  " + projectDir + "    --    " + "3DSMax", True )
        return int( (packStart - self.StartFrame) / (self.EndFrame - self.StartFrame) * int( MasterConfig.MAX_PROGRESS_DASH_COUNT ) )
