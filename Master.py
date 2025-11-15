"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
#########################################################################
    Master is the master module of RenderPipe. 
    Copyright (C) 2012 Hadi Saraf , Payam Memar

    Master is part of RenderPipe.

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


import MasterGUI
import MasterApp


class Master( MasterApp.MasterApp, MasterGUI.MasterGUI ):
    """ this is the mix-in class of MasterApp and MasterGUI """
    pass
