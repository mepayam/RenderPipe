"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
#########################################################################
    RPipeSlv is the slave module of RenderPipe. 
    Copyright (C) 2012 Hadi Saraf , Payam Memar

    RPipeSlv is part of RenderPipe.

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

__version__ = 1.1


import SlaveApp


if "__main__" == __name__:
    print( "RenderPipe 1.1, slave application, built May 08 2011.\nCopyright (C) 2011 Hadi Saraf.\n\n" )
    SlaveApp.SlaveApp().connectPermanent()    # runs the slave
