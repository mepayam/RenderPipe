"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
#########################################################################
    RPipeMstr is the core master process of RenderPipe. 
    Copyright (C) 2012 Hadi Saraf , Payam Memar

    RPipeMstr is part of RenderPipe.

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


import Master

if "__main__" == __name__:
    print( "RenderPipe 1.1, master application, built May 08 2011.\nCopyright (C) 2011 Hadi Saraf.\n\n" )
    Master.Master()  # runs RPipeMstr
