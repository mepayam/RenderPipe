"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
#########################################################################
    MayaServer handles the server side of jobs of type Maya. 
    Copyright (C) 2012 Hadi Saraf , Payam Memar

    MayaServer is part of RenderPipe.

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
        

class MayaServer( JobServer.JobServer ):
    """class for handling the jobs of type Maya"""
    
    def getServerType (self):
        """returns the type of job"""
        return JobServer.MAYA_NGN

    
    def dispatchRenderCmd (self, jobName, packStart, packEnd, sourcePath, projectDir, outputName, thisClient ):
        """dispatches the packets to clients"""
        renderCmd = ' -mr:art ' +\
                        '-s ' + str( packStart ) + ' -e ' + str( packEnd ) +\
                        ' -proj ' + projectDir + ' -im ' + outputName + ' ' + sourcePath

        renderCmd = renderCmd.replace( '/', '\\' )
        
        renderCmd = pickle.dumps( renderCmd )
        thisClient.sendMsg( renderCmd )
        self.insertRLogCallback( jobName + "  ->  " + thisClient.clientAddr[0] + "     --     " + str( packStart ) + "-" + str( packEnd ) + "  ->  " + projectDir + "    --    " + "Maya", True )
        return int( (packStart - self.StartFrame) / (self.EndFrame - self.StartFrame) * int( MasterConfig.MAX_PROGRESS_DASH_COUNT ) )
