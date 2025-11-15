"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
#########################################################################
    ClientProc runs the client side of jobs. 
    Copyright (C) 2012 Hadi Saraf , Payam Memar

    ClientProc is part of RenderPipe.

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

import JobClient

import MayaClient
import XSIClient
import _3DSMaxClient
import NukeClient

import SlaveConfig


if __name__ == '__main__':
    args = sys.argv
    
    if len( args ) < 4:
        print( "error, wrong arguments given\nexting..\n" )
        sys.exit( 1 )
    
    JobName = str( args[1] )
    JobType = str( args[2] )
    Port = int( args[3] )
    ServerName = SlaveConfig.SERVER_ADDR

    if JobType == JobClient.MAYA_NGN:
        MayaClient.MayaClient( JobName, ServerName, Port )
    elif JobType == JobClient.XSI_NGN:
        XSIClient.XSIClient( JobName, ServerName, Port )
    elif JobType == JobClient._3DSMAX_NGN:
        _3DSMaxClient._3DSMaxClient( JobName, ServerName, Port )
    elif JobType == JobClient.NUKE_NGN:
        NukeClient.NukeClient( JobName, ServerName, Port )
    else:
        print( "error, wrong arguments given\nexting..\n" )
        sys.exit( 1 )

    sys.exit( 0 )
