"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
#########################################################################
    MasterGUI handles the user interface of RenderPipe. 
    Copyright (C) 2012 Hadi Saraf , Payam Memar

    MasterGUI is part of RenderPipe.

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
import sys
import socket
import time
import tkinter
import tkinter.filedialog
import tkinter.messagebox
import tkinter.simpledialog
import subprocess
import threading
import pickle
import random

import HiStreamServer
import MasterConfig
import JobServer

from MasterApp import *



class EntryDialog( tkinter.simpledialog.Dialog ):
    """class for Prompting an entry dialogbox"""
    def __init__ (self, master, message):
        self.input = None
        self.message = message
        tkinter.simpledialog.Dialog.__init__( self, master )
    def body (self, root):
        tkinter.Label( self, text = self.message ).pack( side = tkinter.TOP, expand = 1, fill = tkinter.BOTH )
        self.inputData = tkinter.Entry( self )
        self.inputData.pack( side = tkinter.TOP, expand = 1, fill = tkinter.BOTH )
    def apply (self):
        self.input = self.inputData.get()
        if not self.input:
            self.input = None
    def get (self):
        return self.input

            


class ListboxDialog( tkinter.simpledialog.Dialog ):
    """class for prompting listbox dialogbox"""
    def __init__ (self, master, message, itemsList = [], multiSelect = False):
        self.multiSelect = multiSelect
        self.itemsList = itemsList
        self.input = None
        self.message = message
        tkinter.simpledialog.Dialog.__init__( self, master )
    def body (self, root):
        tkinter.Label( self, text = self.message ).pack( side = tkinter.TOP, expand = 1, fill = tkinter.BOTH )
        if not self.multiSelect:
            self.listbox = tkinter.Listbox( self )
        else:
            self.listbox = tkinter.Listbox( self, selectmode = tkinter.EXTENDED )            
        for thisItem in self.itemsList:
            self.listbox.insert( tkinter.END, thisItem )
        self.listbox.pack( side = tkinter.TOP, expand = 1, fill = tkinter.BOTH )
    def apply (self):
        if self.listbox.curselection():
            if not self.multiSelect:
                self.input = self.listbox.get( self.listbox.curselection() )
            else:
                indeces = self.listbox.curselection()
                self.input = []
                for index in indeces:
                    self.input.append( self.listbox.get( index ) )
        else:
            self.input = None
    def get (self):
        return self.input
            



class EntryListboxDialog( tkinter.simpledialog.Dialog ):
    """class for prompting entry-listbox dialogbox"""
    def __init__ (self, master, message, itemsList = [], entryLabel = "", multiSelect = False):
        self.multiSelect = multiSelect
        self.itemsList = itemsList
        self.entryLabel = entryLabel
        self.input = None
        self.message = message
        tkinter.simpledialog.Dialog.__init__( self, master )
    def body (self, root):
        tkinter.Label( self, text = self.message ).pack( side = tkinter.TOP, expand = 1, fill = tkinter.BOTH )
        if not self.multiSelect:
            self.listbox = tkinter.Listbox( self )
        else:
            self.listbox = tkinter.Listbox( self, selectmode = tkinter.EXTENDED )
            entryLabel = tkinter.Label( self, text = self.entryLabel )
            self.entryData = tkinter.Entry( self )
        for thisItem in self.itemsList:
            self.listbox.insert( tkinter.END, thisItem )
        self.listbox.pack( side = tkinter.TOP, expand = 1, fill = tkinter.BOTH )
        entryLabel.pack( side = tkinter.TOP, expand = 1, fill = tkinter.BOTH )
        self.entryData.pack( side = tkinter.TOP, expand = 1, fill = tkinter.BOTH )
    def apply (self):
        if self.listbox.curselection():
            if not self.multiSelect:
                self.input = self.listbox.get( self.listbox.curselection() )
            else:
                indeces = self.listbox.curselection()
                input1 = []
                for index in indeces:
                    input1.append( self.listbox.get( index ) )
        else:
            input1 = None
        if self.entryData.get():
            input2 = self.entryData.get()
        else:
            input2 = None
        self.input = (input1, input2)
    def get (self):
        return self.input
    



class MasterGUI( tkinter.Tk ):
    """class to handle the user interface"""
    def __init__ (self):
        """initiates the user interface"""
        tkinter.Tk.__init__( self, className = 'nazca' )
        # create the data of the user input
        #
        self.jobNameData = tkinter.StringVar()
        self.jobStartFrmData = tkinter.StringVar()
        self.jobEndFrmData = tkinter.StringVar()
        self.jobPackSizeData = tkinter.StringVar()
        self.jobSrcFileData = tkinter.StringVar()
        self.jobDestPathData = tkinter.StringVar()
        self.jobOutNameData = tkinter.StringVar()
        self.engineTypeData = tkinter.StringVar()

        self.jobNameData.set( "renderJob_1" )
        self.jobStartFrmData.set( 1 )
        self.jobEndFrmData.set( 100 )
        self.jobPackSizeData.set( 5 )
        self.jobSrcFileData.set( "write the source path or double click to browse" )
        self.jobDestPathData.set( "write the destination directory or double click to browse" )
        self.jobOutNameData.set( "frame" )
        self.engineTypeData.set( JobServer.MAYA_NGN )

        # initiate the master GUI
        #
        self.createMasterGUI()

        
    def createMasterGUI (self):
        "creates the master user interface"

        menuBar = tkinter.Menu( self )

        fileBar = tkinter.Menu( menuBar )
        fileBar.add_command( label = "Import", command = self.importJob )
        fileBar.add_command( label = "Export", command = self.exportJob )
        fileBar.add_separator()
        fileBar.add_command( label = "Exit", command = self.exitProc )

        editBar = tkinter.Menu( menuBar )
        editBar.add_command( label = "Reorder Jobs", command = self.reorderJobs )
        editBar.add_command( label = "Reorder Slaves", command = self.reorderServers )        
        editBar.add_separator()
        editBar.add_command( label = "Clear Finished Jobs", command = self.clearFinishedJobs )
        editBar.add_command( label = "Clear Stopped Jobs", command = self.clearStoppedJobs )
        editBar.add_command( label = "Clear selected Job", command = self.clearSelectedJobs )        
        editBar.add_separator()
        editBar.add_command( label = "Clear Info Box", command = self.clearInfobox )
        editBar.add_command( label = "Clear Log Box", command = self.clearLogbox )
        editBar.add_command( label = "Clear Render Log Box", command = self.clearRLogbox )
        editBar.add_command( label = "Clear All Logs", command = self.clearAllLogs )
        editBar.add_separator()
        editBar.add_command( label = "Fresh All", command = self.freshAll )
        

        toolsBar = tkinter.Menu( menuBar )
        toolsBar.add_command( label = "Start Job", command = self.runJob )
        toolsBar.add_command( label = "Queue Job", command = self.queueJob )
        toolsBar.add_command( label = "Add Slaves", command = self.activateAddedClients )
        toolsBar.add_separator()
        toolsBar.add_command( label = "Stop Jobs", command = self.stopJobs )
        toolsBar.add_command( label = "Make Jobs WP", command = self.makeJobsWP )        
        toolsBar.add_command( label = "Make Jobs Que", command = self.makeJobsQue )        
        toolsBar.add_command( label = "Change Priority", command = self.changePriority )
        toolsBar.add_separator()
        toolsBar.add_command( label = "Stop Slaves", command = self.stopClients )
        toolsBar.add_command( label = "Make Slaves WJ", command = self.makeClientsWJ )
        toolsBar.add_command( label = "Make Slaves WP", command = self.makeClientsWP )
        toolsBar.add_command( label = "Make Slaves Auto", command = self.makeClientsAuto )


        
        enginesBar = tkinter.Menu( menuBar )
        enginesBar.add_radiobutton( label = "Maya", variable = self.engineTypeData, value = JobServer.MAYA_NGN, command = self.setMayaGUI )
        enginesBar.add_radiobutton( label = "XSI", variable = self.engineTypeData, value = JobServer.XSI_NGN, command = self.setXSIGUI )
        enginesBar.add_radiobutton( label = "3DSMax", variable = self.engineTypeData, value = JobServer._3DSMAX_NGN, command = self.set3DSMaxGUI )
        enginesBar.add_radiobutton( label = "Nuke", variable = self.engineTypeData, value = JobServer.NUKE_NGN, command = self.setNukeGUI )
        

        helpBar = tkinter.Menu( menuBar )
        helpBar.add_command( label = "Help", command = self.showHelp )
        helpBar.add_command( label = "Goto HSaraf", command = self.gotoFxhues )        
        helpBar.add_command( label = "About", command = self.showAbout )
        
        
        menuBar.add_cascade( label = "File", menu = fileBar )
        menuBar.add_cascade( label = "Edit", menu = editBar )        
        menuBar.add_cascade( label = "Tools", menu = toolsBar )
        menuBar.add_cascade( label = "Engines", menu = enginesBar )        
        menuBar.add_cascade( label = "Help", menu = helpBar )
        self["menu"] = menuBar
        
        
        
        
        # mainFrame
        #
        mainFrame = tkinter.Frame( self )
        mainFrame.pack( side = tkinter.TOP, expand = 1, fill = tkinter.BOTH )
        


        
        topFrame = tkinter.Frame( mainFrame )
        topFrame.pack( side = tkinter.TOP, expand = 0, fill = tkinter.BOTH )

        

        # frame to bundle the <slaves list, jobs list and info box>
        #
        inFrame = tkinter.Frame( topFrame )
        inFrame.pack( side = tkinter.LEFT, expand = 0, fill = tkinter.Y, anchor = tkinter.S )



        logoFrame = tkinter.Frame( inFrame )
        logoFrame.pack( side = tkinter.TOP, expand = 1, fill = tkinter.BOTH, anchor = tkinter.N )


        self.controlPanelLabel = tkinter.Label( logoFrame, text = "Control Panel",
                                               bg = MasterConfig.LABELS_BG_COLOR,
                                               font = ("Helvetica", 8, "bold"), relief = tkinter.RIDGE )
        self.controlPanelLabel.pack( side = tkinter.TOP, anchor = tkinter.N )
        self.image = tkinter.PhotoImage( file = "logo.gif" )
        self.figure = tkinter.Canvas( logoFrame )
        self.logo = self.figure.create_image( -27, 135, image = self.image, anchor = tkinter.W )
        self.figure.pack( expand = 1, fill = tkinter.BOTH )
        


        inputFrame = tkinter.Frame( inFrame )
        inputFrame.pack( side = tkinter.TOP, expand = 1, fill = tkinter.BOTH, anchor = tkinter.S )
        
        # frame to bundle the input <job name> entry
        #
        tkinter.Label( inputFrame, text = "Job Name",
                       bg = MasterConfig.LABELS_BG_COLOR,
                       font = ("Helvetica", 8, "bold"), relief = tkinter.RIDGE ).pack( side = tkinter.TOP, anchor = tkinter.W )
        self.jobNameEntry = tkinter.Entry( inputFrame, textvariable = self.jobNameData )
        self.jobNameEntry.pack( expand = 1, fill = tkinter.X )

        # frame to bundle the input <job start frame, job end frame>
        #
        # <job start frame> scale
        #
        tkinter.Label( inputFrame, text = "Start Frame",
                       bg = MasterConfig.LABELS_BG_COLOR,
                       font = ("Helvetica", 8, "bold"), relief = tkinter.RIDGE ).pack( side = tkinter.TOP, anchor = tkinter.W )
        tkinter.Spinbox( inputFrame,
                        textvariable = self.jobStartFrmData,
                         from_ = MasterConfig.MIN_FRAME, to = MasterConfig.MAX_FRAME ).pack( side = tkinter.TOP, expand = 1, fill = tkinter.X )
        # <job end frame> scale
        #
        tkinter.Label( inputFrame, text = "End Frame",
                       bg = MasterConfig.LABELS_BG_COLOR,
                       font = ("Helvetica", 8, "bold"), relief = tkinter.RIDGE ).pack( side = tkinter.TOP, anchor = tkinter.W )
        tkinter.Spinbox( inputFrame,
                        textvariable = self.jobEndFrmData,
                         from_ = MasterConfig.MIN_FRAME, to = MasterConfig.MAX_FRAME ).pack( side = tkinter.TOP, expand = 1, fill = tkinter.X )
        # <job end frame> scale
        #
        tkinter.Label( inputFrame, text = "Pack Size",
                       bg = MasterConfig.LABELS_BG_COLOR,
                       font = ("Helvetica", 8, "bold"), relief = tkinter.RIDGE ).pack( side = tkinter.TOP, anchor = tkinter.W )
        tkinter.Spinbox( inputFrame,
                        textvariable = self.jobPackSizeData,
                         from_ = MasterConfig.MIN_FRAME, to = MasterConfig.MAX_FRAME ).pack( side = tkinter.TOP, expand = 1, fill = tkinter.X )

        # <job source file> entry
        #
        tkinter.Label( inputFrame, text = "Soure Path",
                       bg = MasterConfig.LABELS_BG_COLOR,
                       font = ("Helvetica", 8, "bold"), relief = tkinter.RIDGE ).pack( side = tkinter.TOP, anchor = tkinter.W )
        self.jobSrcFileEntry = tkinter.Entry( inputFrame, textvariable = self.jobSrcFileData )
        self.jobSrcFileEntry.bind( "<Double-Button-1>", self.getSourceFile )
        self.jobSrcFileEntry.pack( side = tkinter.TOP, expand = 1, fill = tkinter.X )
        # <job destination path> entry
        #
        self.jobDestPathLabel = tkinter.Label( inputFrame, text = "Destination Directory",
                           bg = MasterConfig.LABELS_BG_COLOR, 
                           font = ("Helvetica", 8, "bold"), relief = tkinter.RIDGE )
        self.jobDestPathLabel.pack( side = tkinter.TOP, anchor = tkinter.W )
        self.jobDestPathEntry = tkinter.Entry( inputFrame, textvariable = self.jobDestPathData )
        self.jobDestPathEntry.bind( "<Double-Button-1>", self.getDestPath )
        self.jobDestPathEntry.pack( side = tkinter.TOP, expand = 1, fill = tkinter.X )
        # <job output name> entry
        #
        self.jobOutNameLabel = tkinter.Label( inputFrame, text = "Output Name",
                                   bg = MasterConfig.LABELS_BG_COLOR,
                                   font = ("Helvetica", 8, "bold"), relief = tkinter.RIDGE )
        self.jobOutNameLabel.pack( side = tkinter.TOP, anchor = tkinter.W )
        self.jobOutNameEntry = tkinter.Entry( inputFrame, textvariable = self.jobOutNameData )
        self.jobOutNameEntry.pack( side = tkinter.TOP, expand = 1, fill = tkinter.X )

        # frame to bundle the inputs
        #
        
        inputFrame1 = tkinter.Frame( inputFrame )
        inputFrame1.pack( side = tkinter.TOP, expand = 1, fill = tkinter.BOTH )
        tkinter.Button( inputFrame1, text = "Start Job",
                        font = ("Helvetica", 8, "bold"), relief = tkinter.RIDGE, 
                        command = self.runJob ).pack( side = tkinter.LEFT, expand = 1, fill = tkinter.X )
        tkinter.Button( inputFrame1, text = "Queue Job",
                        font = ("Helvetica", 8, "bold"), relief = tkinter.RIDGE, 
                        command = self.queueJob ).pack( side = tkinter.LEFT, expand = 1, fill = tkinter.X )
        tkinter.Button( inputFrame1, text = "Add Slaves",
                        font = ("Helvetica", 8, "bold"), relief = tkinter.RIDGE, 
                        command = self.activateAddedClients ).pack( side = tkinter.LEFT, expand = 1, fill = tkinter.X )

        inputFrame2 = tkinter.Frame( inputFrame )
        inputFrame2.pack( side = tkinter.TOP, expand = 1, fill = tkinter.BOTH )        
        tkinter.Button( inputFrame2, text = "  Stop Jobs  ",
                        font = ("Helvetica", 8, "bold"), relief = tkinter.RIDGE, 
                        command = self.stopJobs ).pack( side = tkinter.LEFT, expand = 1, fill = tkinter.X )
        tkinter.Button( inputFrame2, text = "  Jobs WP  ",
                        font = ("Helvetica", 8, "bold"), relief = tkinter.RIDGE, 
                        command = self.makeJobsWP ).pack( side = tkinter.LEFT, expand = 1, fill = tkinter.X )
        tkinter.Button( inputFrame2, text = "Jobs Queue",
                        font = ("Helvetica", 8, "bold"), relief = tkinter.RIDGE, 
                        command = self.makeJobsQue ).pack( side = tkinter.LEFT, expand = 1, fill = tkinter.X )
        tkinter.Button( inputFrame2, text = "Chaneg Prio",
                        font = ("Helvetica", 8, "bold"), relief = tkinter.RIDGE, 
                        command = self.changePriority ).pack( side = tkinter.LEFT, expand = 1, fill = tkinter.X )

        inputFrame3 = tkinter.Frame( inputFrame )
        inputFrame3.pack( side = tkinter.TOP, expand = 1, fill = tkinter.BOTH )                
        tkinter.Button( inputFrame3, text = "Stop Slaves",
                        font = ("Helvetica", 8, "bold"), relief = tkinter.RIDGE, 
                        command = self.stopClients ).pack( side = tkinter.LEFT, expand = 1, fill = tkinter.X )
        tkinter.Button( inputFrame3, text = "Slaves WJ",
                        font = ("Helvetica", 8, "bold"), relief = tkinter.RIDGE, 
                        command = self.makeClientsWJ ).pack( side = tkinter.LEFT, expand = 1, fill = tkinter.X )
        tkinter.Button( inputFrame3, text = "Slaves WP",
                        font = ("Helvetica", 8, "bold"), relief = tkinter.RIDGE, 
                        command = self.makeClientsWP ).pack( side = tkinter.LEFT, expand = 1, fill = tkinter.X )
        tkinter.Button( inputFrame3, text = "Slaves Auto",
                        font = ("Helvetica", 8, "bold"), relief = tkinter.RIDGE, 
                        command = self.makeClientsAuto ).pack( side = tkinter.LEFT, expand = 1, fill = tkinter.X )

        """
        inputFrame4 = tkinter.Frame( inputFrame )
        inputFrame4.pack( side = tkinter.TOP, expand = 1, fill = tkinter.BOTH )        
        tkinter.Button( inputFrame4, text = "Add Slave(s)",
                        font = ("Helvetica", 8, "bold"), relief = tkinter.RIDGE, 
                        command = self.activateAddedClients ).pack( side = tkinter.LEFT, expand = 1, fill = tkinter.X )
        """



        outFrame = tkinter.Frame( topFrame )
        outFrame.pack( side = tkinter.LEFT, expand = 1, fill = tkinter.BOTH )



        listFrame = tkinter.Frame( outFrame )
        listFrame.pack( side = tkinter.TOP, expand = 1, fill = tkinter.BOTH )


        infoFrame = tkinter.Frame( listFrame )
        infoFrame.pack( side = tkinter.LEFT, expand = 1, fill = tkinter.BOTH )

        
        # <info> text with its scrollBar
        #
        tkinter.Label( infoFrame, text = "Info Box",
                       bg = MasterConfig.LABELS_BG_COLOR,
                       font = ("Helvetica", 8, "bold"), relief = tkinter.RIDGE ).pack( side = tkinter.TOP )
        self.infoBox = tkinter.Text( infoFrame, bg = MasterConfig.INFOBOX_BG_COLOR, fg  = MasterConfig.INFOBOX_FG_COLOR )
        IBScrollBar = tkinter.Scrollbar( self.infoBox, orient = tkinter.VERTICAL )
        IBScrollBar.pack( side = tkinter.RIGHT, fill = tkinter.Y )
        IBScrollBar["command"] = self.infoBox.yview
        self.infoBox["yscrollcommand"] = IBScrollBar.set
        self.infoBox.pack( side = tkinter.TOP, expand = 1, fill = tkinter.BOTH )


        jobSlaveFrame = tkinter.Frame( listFrame )
        jobSlaveFrame.pack( side = tkinter.LEFT, expand = 1, fill = tkinter.BOTH )
        
        
        # <jobs> listBox with its scrollBar
        #
        tkinter.Label( jobSlaveFrame, text = "Jobs\tSlaves",
                       bg = MasterConfig.LABELS_BG_COLOR,
                       font = ("Helvetica", 8, "bold"), relief = tkinter.RIDGE ).pack( side = tkinter.TOP )
        self.jobsBox = tkinter.Listbox( jobSlaveFrame,
                                        selectmode = tkinter.EXTENDED,
                                        bg = MasterConfig.JOBSBOX_BG_COLOR, fg = MasterConfig.JOBSBOX_FG_COLOR,
                                        relief = tkinter.SUNKEN,
                                        font = ("Helvetica", 10, "bold") )
        self.jobsBox.bind( "<Double-Button-1>", self.writeJobInfo )
        JBScrollBar = tkinter.Scrollbar( self.jobsBox, orient = tkinter.VERTICAL )
        JBScrollBar.pack( side = tkinter.RIGHT, fill = tkinter.Y )
        JBScrollBar["command"] = self.jobsBox.yview
        self.jobsBox["yscrollcommand"] = JBScrollBar.set       
        self.jobsBox.pack( side = tkinter.LEFT, expand = 1, fill = tkinter.BOTH )
        
        # <slaves> listBox with its scrollBar
        #
        self.slavesBox = tkinter.Listbox( jobSlaveFrame,
                                          selectmode = tkinter.EXTENDED,
                                          bg = MasterConfig.SLAVESBOX_BG_COLOR, fg = MasterConfig.SLAVESBOX_FG_COLOR,
                                          relief = tkinter.SUNKEN,
                                          font = ("Helvetica", 10, "bold") )
        self.slavesBox.bind( "<Double-Button-1>", self.writeSlaveInfo )
        SBScrollBar = tkinter.Scrollbar( self.slavesBox, orient = tkinter.VERTICAL )
        SBScrollBar.pack( side = tkinter.RIGHT, fill = tkinter.Y )
        SBScrollBar["command"] = self.jobsBox.yview
        self.slavesBox["yscrollcommand"] = SBScrollBar.set
        self.slavesBox.pack( side = tkinter.LEFT, expand = 1, fill = tkinter.BOTH )


       
        # frame to bundle the <log box> with its scrollBar
        #
        logFrame = tkinter.Frame( outFrame)
        logFrame.pack( side = tkinter.TOP, expand = 1, fill = tkinter.BOTH)
        
        tkinter.Label( logFrame, text = "Log Box",
                       bg = MasterConfig.LABELS_BG_COLOR,
                       font = ("Helvetica", 8, "bold"), relief = tkinter.RIDGE ).pack( side = tkinter.TOP )
        self.logBox = tkinter.Text( logFrame, bg = MasterConfig.LOGBOX_BG_COLOR, fg = MasterConfig.LOGBOX_FG_COLOR )
        self.logBox.pack( expand = 1, fill = tkinter.BOTH )
        LBScrollBar = tkinter.Scrollbar( self.logBox, orient = tkinter.VERTICAL )
        LBScrollBar.pack( side = tkinter.RIGHT, fill = tkinter.Y)
        LBScrollBar["command"] = self.logBox.yview
        self.logBox["yscrollcommand"] = LBScrollBar.set



        
        renderLogFrame = tkinter.Frame( mainFrame)
        renderLogFrame.pack( side = tkinter.BOTTOM, expand = 1, fill = tkinter.BOTH )

        tkinter.Label( renderLogFrame,
                       text = "Render Log Box",
                       bg = MasterConfig.LABELS_BG_COLOR,
                       font = ("Helvetica", 8, "bold"), relief = tkinter.RIDGE ).pack( side = tkinter.TOP )
        self.rLogBox = tkinter.Text( renderLogFrame,
                                     bg = MasterConfig.LOGBOX_BG_COLOR, fg = MasterConfig.LOGBOX_FG_COLOR )
        self.rLogBox.pack( expand = 1, fill = tkinter.BOTH )
        RLBScrollBar = tkinter.Scrollbar( self.rLogBox, orient = tkinter.VERTICAL )
        RLBScrollBar.pack( side = tkinter.RIGHT, fill = tkinter.Y)
        RLBScrollBar["command"] = self.rLogBox.yview
        self.rLogBox["yscrollcommand"] = RLBScrollBar.set        
                


    def setMayaGUI (self):
        """sets Maya user interface"""
        
        self.controlPanelLabel.config( text = 'Maya', font = ("Helvetica", 9) )

        self.jobDestPathData.set( "write the destination directory or double click to browse" )
        self.jobDestPathLabel.config( state = tkinter.NORMAL )
        self.jobDestPathEntry.config( state = tkinter.NORMAL )

        self.jobOutNameData.set( "frame" )
        self.jobOutNameLabel.config( state = tkinter.NORMAL )
        self.jobOutNameEntry.config( state = tkinter.NORMAL )



    def setXSIGUI (self):
        """sets XSI user interface"""
        self.controlPanelLabel.config( text = 'XSI', font = ("Helvetica", 9) )

        self.jobDestPathData.set( "write the destination directory or double click to browse" )
        self.jobDestPathLabel.config( state = tkinter.NORMAL )
        self.jobDestPathEntry.config( state = tkinter.NORMAL )

        self.jobOutNameData.set( "the output name is given from the xsi script file" )
        self.jobOutNameLabel.config( state = tkinter.DISABLED )
        self.jobOutNameEntry.config( state = tkinter.DISABLED )



    def set3DSMaxGUI (self):
        """sets 3DSMax user interface"""
        self.controlPanelLabel.config( text = '3DSMax', font = ("Helvetica", 9) )

        self.jobDestPathData.set( "write the destination directory or double click to browse" )
        self.jobDestPathLabel.config( state = tkinter.NORMAL )
        self.jobDestPathEntry.config( state = tkinter.NORMAL )

        self.jobOutNameData.set( "frame.ext" )
        self.jobOutNameLabel.config( state = tkinter.NORMAL )
        self.jobOutNameEntry.config( state = tkinter.NORMAL )
        

        
    def setNukeGUI (self):
        """sets Nuke user interface"""
        self.controlPanelLabel.config( text = 'Nuke', font = ("Helvetica", 9) )

        self.jobDestPathData.set( "the destination path is given from the nuke script file" )
        self.jobDestPathLabel.config( state = tkinter.DISABLED )
        self.jobDestPathEntry.config( state = tkinter.DISABLED )

        self.jobOutNameData.set( "the output name is given from the nuke script file" )
        self.jobOutNameLabel.config( state = tkinter.DISABLED )
        self.jobOutNameEntry.config( state = tkinter.DISABLED )
        

            

    def checkIfDataIsValid (self, jPack):
        """checks the validation of job data before starting,
            jPack : the bundles job data to verify"""
        if not jPack.jobName:
            self.insertLog( "the name of job is not given", 'war' )    
            return False
        elif len( jPack.jobName ) > MasterConfig.MAX_JOBNAME_CHARS_COUNT:
            self.insertLog( "the max number of the job name characters is " + str( MasterConfig.MAX_JOBNAME_CHARS_COUNT ), 'war' )
            return False            
        if self.mapJobName2Job( jPack.jobName ) in MasterApp.Jobs_List:    
            self.insertLog( "another job is already ran with this name " + jPack.jobName, 'war' )
            return False
        if not jPack.jobStartFrm:
            self.insertLog( "the start frame is not given", 'war' )    
            return False
        else:
            try:
                jPack.jobStartFrm = int( jPack.jobStartFrm )
            except ValueError as err:
                self.insertLog( "invalid start frame entered" )
                return False
        if not jPack.jobEndFrm:
            self.insertLog( "the end frame is not given", 'war' )    
            return False
        else:
            try:
                jPack.jobEndFrm = int( jPack.jobEndFrm )
            except ValueError as err:
                self.insertLog( "invalid end frame entered" )
                return False
        if jPack.jobStartFrm > jPack.jobEndFrm:
            self.insertLog( "the start frame is greater than the end frame", 'war' )   
            return False
        if not jPack.jobPackSize:
            self.insertLog( "the pack size is not given", 'war' )    
            return False
        else:
            try:
                jPack.jobPackSize = int( jPack.jobPackSize )
                if jPack.jobPackSize < 1:
                    self.insertLog( "the pack size must be greater than zero", 'war' )
                    return False
            except ValueError as err:
                self.insertLog( "invalid pack size entered" )
                return False
        if not jPack.jobSrcFile:
            self.insertLog( "the source file path is not given", 'war' )
            return False
        else:
            if not os.path.exists( jPack.jobSrcFile ):
                self.insertLog( "the source file does not exist", 'war' )
                return False
        if self.engineTypeData.get() != JobServer.NUKE_NGN:
            if not jPack.jobDestPath:
                self.insertLog( "the destination directory is not given", 'war' )
                return False
            elif not os.path.exists( jPack.jobDestPath ):
                self.insertLog( "the destination path does not exist", 'war' )
                return False
            if self.engineTypeData.get() != JobServer.XSI_NGN:
                if not jPack.jobOutName:
                    self.insertLog( "the output name is not given", 'war' )
                    return False
        return True


        


    def getSourceFile (self, event):
        """gets the source path of the job"""
        srcPath = tkinter.filedialog.askopenfilename( filetypes = [("maya binary", ".mb"), 
                                                                   ("maya ascii", ".ma"), 
                                                                   ("xsi", ".scn"), 
                                                                   ("3dsmax", ".max"), 
                                                                   ("nuke", ".nk"), 
                                                                   ("all files", "*.*")] )
        if not srcPath:
            return
        self.jobSrcFileData.set( srcPath )
        # set the destination path
        #
        if self.engineTypeData.get() == JobServer.MAYA_NGN:
            l = srcPath.split( '/' )
            n = len( l )
            if (n < 4):
                self.insertLog( "project incorreclty set", 'err' )
                self.jobDestPathData.set( srcPath )
                return
            l.pop()
            l.pop()
            s = ''
            for p in l:
                s += p + '/'
            self.jobDestPathData.set( s[:-1] )
        elif self.engineTypeData.get() == JobServer.XSI_NGN:
            l = srcPath.split( '/' )
            n = len( l )
            if (n < 4):
                self.insertLog( "project incorreclty set", 'err' )
                self.jobDestPathData.set( srcPath )
                return
            l.pop()
            l.pop()
            s = ''
            for p in l:
                s += p + '/'
            s += "Render_Pictures"
            self.jobDestPathData.set( s )
        elif self.engineTypeData.get() == JobServer._3DSMAX_NGN:
            l = srcPath.split( '/' )
            n = len( l )
            if (n < 4):
                self.insertLog( "project incorreclty set", 'err' )
                self.jobDestPathData.set( srcPath )
                return
            l.pop()
            l.pop()
            s = ''
            for p in l:
                s += p + '/'
            s += "renderOutput"
            self.jobDestPathData.set( s )
        else:
            self.jobDestPathData.set( srcPath )
            
        


    def getDestPath (self, event):
        """gets the destination directory of the job"""
        destPath = tkinter.filedialog.askdirectory()
        if not destPath:
            return
        self.jobDestPathData.set( destPath )        



    def writeJobInfo (self, event):
        """writes the information of selected job in infoBox"""
        if self.jobsBox.curselection() == ():
            self.insertLog( "no job is selected" )
            return
        thisJobName = self.getSelectedJobs()[0]
        thisJob = self.mapJobName2Job( thisJobName )
        self.insertInfo( "Job Name : " + thisJob.JobName + "\n")
        self.insertInfo( "Job Engine : " + thisJob.getServerType() + "\n" )        
        if thisJob.JobState == JobServer.JOB_RUNNING_STAT:
            jobStat = "Running"
        elif thisJob.JobState == JobServer.JOB_FINISHED_STAT:
            jobStat = "Finished"
        elif thisJob.JobState == JobServer.JOB_QUEUED_STAT:
            jobStat = "Queued"
        elif thisJob.JobState == JobServer.JOB_STOPPED_STAT:
            jobStat = "Stopped"
        elif thisJob.JobState == JobServer.JOB_WAITPACK_STAT:
            jobStat = "WaitPack"
        else:
            jobStat = "unknown"
        self.insertInfo( "Job State : " + jobStat + "\n" )
        self.insertInfo( "Job Prriority : " + str( thisJob.JobPrio ) + "\n" )
        self.insertInfo( "Start Frame : " + str( thisJob.StartFrame ) + "\n")
        self.insertInfo( "End Frame : " + str( thisJob.EndFrame ) + "\n")
        self.insertInfo( "Pack Size : " + str( thisJob.PackSize ) + "\n")
        self.insertInfo( "Source File : " + thisJob.SourceFile + "\n")
        self.insertInfo( "Destination Path : " + thisJob.ProjectPath + "\n")
        self.insertInfo( "Output Name : " + thisJob.OutputName + "\n")
        self.insertInfo( "Master Name : " + thisJob.Master + " / " + socket.gethostbyname( thisJob.Master ) + "\n" )
        self.insertInfo( "Slaves : " )
        for srvr in thisJob.Servers:
            self.insertInfo( srvr.clientAddr[0] + ", " )
        self.insertInfo( "\nConnection Port : " + str( thisJob.Port ) + "\n")
        self.insertInfo( '-' * 30 + "\n")
        # sets the items on the control panel
        #
        self.jobNameData.set( thisJob.JobName )
        self.jobStartFrmData.set( thisJob.StartFrame )
        self.jobEndFrmData.set( thisJob.EndFrame )
        self.jobPackSizeData.set( thisJob.PackSize )
        self.jobSrcFileData.set( thisJob.SourceFile )
        self.jobDestPathData.set( thisJob.ProjectPath )
        self.jobOutNameData.set( thisJob.OutputName )

        
        
    def writeSlaveInfo (self, event):
        """ writes the information of selected slave in infoBox """
        if self.slavesBox.curselection() == ():
            self.insertLog( "no slave is selected" )
            return
        thisSlave = self.getSelectedSlaves()[0]
        thisConnection = self.mapClientAddr2Connection( thisSlave )
        self.insertInfo( "Server Address: " + thisConnection.clientAddr[0] + "\n" )
        if thisConnection.ServerJob:
            jobName = thisConnection.ServerJob.JobName
        else:
            jobName = "none"
        self.insertInfo( "Server Job: " + jobName + "\n" )            
        if thisConnection.ServerState == JobServer.SERVER_IDLE_STAT:
            serverState = "Idle"
        elif thisConnection.ServerState == JobServer.SERVER_AUTOMATED_STAT:
            serverState = "Auto"
        elif thisConnection.ServerState == JobServer.SERVER_WAITJOB_STAT:
            serverState = "WaitJob"
        elif thisConnection.ServerState == JobServer.SERVER_WAITPACK_STAT:
            serverState = "WaitPack"
        else:
            serverState = "unknown"
        self.insertInfo( "Server State: " + serverState + "\n" )
        self.insertInfo( "Server Port : " + str( thisConnection.clientAddr[1] ) + "\n" )
        self.insertInfo( '-' * 30 + "\n")


        
        
    def insertInfo (self, info):
        "inserts the information into the infoBox"
        self.infoBox.insert( tkinter.END, info )
        self.infoBox.yview_moveto( 1.0 )
        

    def insertLog (self, log, mod = 'inf', timeFlag = False):
        """inserts the logs into logBox,
           log : the text log given to be written,
           mod : the type of log,
           timeFlag : the time flag to append time&date"""
        if not timeFlag:
            if mod == 'inf':   #check if the mod is info
                log = "inf: " + log + "\n"
            elif mod == 'war':   #check if the mod is warning
                log = "war: " + log + "\n"            
            elif mod == 'err':   #check if the mod is error
                log = "err: " + log + "\n"
        else:
            if mod == 'inf':   #check if the mod is info
                log = "inf: " + log + " -- " + time.ctime() + "\n"
            elif mod == 'war':   #check if the mod is warning
                log = "war: " + log + " -- " + time.ctime() + "\n"            
            elif mod == 'err':   #check if the mod is error
                log = "err: " + log + " -- " + time.ctime() + "\n"
        self.logBox.insert( tkinter.END, log )
        self.logBox.yview_moveto( 1.0 )



    def insertRLog (self, log, timeFlag = False):
        """inserts the render logs into rLogBox, 
            log : the text log given to be written,
            timneFlag : the time flag to append time&date"""
        if timeFlag:
            self.rLogBox.insert( tkinter.END, log + "   --   " + time.ctime() + "\n" )
        else:
            self.rLogBox.insert( tkinter.END, log + "\n" )
        self.rLogBox.yview_moveto( 1.0 )



    def appendJob (self, job):
        """appends the job to jobBox,
        job : the job that is to be appended"""
        maxDashCount = MasterConfig.MAX_PROGRESS_DASH_COUNT
        spacesCount = MasterConfig.JNAME_JSTATE_SPACES_COUNT
        jobName = job.JobName
        jobState = job.JobState
        jobPrio = str( job.JobPrio )
        packNum = job.jobPackNum
        serverType = job.getServerType()
        jobStr = jobName + " " * spacesCount + "   [" +  packNum * "=" + (maxDashCount - packNum) * "  " + "]   " + jobState + " " + jobPrio + "   " + serverType
        self.jobsBox.insert( tkinter.END, jobStr )
        

    def removeJob (self, jobName):
        """removes the job from jobBox,
        jobName : the job name that is to be removed"""
        spacesCount = MasterConfig.JNAME_JSTATE_SPACES_COUNT
        indx = 0
        for jb in self.jobsBox.get( 0, tkinter.END ):
            if jb.partition( spacesCount * ' ' )[0] == jobName:
                self.jobsBox.delete( indx )
                return indx
            indx += 1

            
        
    def appendServer (self, server):
        """appends the slave to slaveBox,
            server : the server that is to be appended"""
        spacesCount = MasterConfig.SNAME_SSTATE_SPACES_COUNT
        serverAddr = server.clientAddr[0]
        serverJob = server.ServerJob
        serverJobName = ""
        if serverJob:
            serverJobName = serverJob.JobName
        serverState = server.ServerState
        self.slavesBox.insert( tkinter.END, serverAddr + " " * spacesCount + serverJobName + "     " + serverState )
        



    def removeServer (self, serverAddr):
        """removes the slave from the slaveBox,
        serverAddr : the server name that is to be removed"""
        spacesCount = MasterConfig.SNAME_SSTATE_SPACES_COUNT
        indx = 0
        for srvr in self.slavesBox.get( 0, tkinter.END ):
            if srvr.partition( spacesCount * ' ' )[0] == serverAddr:
                self.slavesBox.delete( indx )
                break
            indx += 1



    def getSelectedSlaves (self):
        "returns the selected slaves from salvesBox"
        spacesCount = MasterConfig.SNAME_SSTATE_SPACES_COUNT
        slvSelectionList = []
        indxList = self.slavesBox.curselection()
        for indx in indxList:
            totalSlaveName = self.slavesBox.get( indx )
            slaveName = totalSlaveName.partition( ' ' * spacesCount )[0]
            slvSelectionList.append( slaveName )
        return slvSelectionList
    


    def getSelectedJobs (self):
        "returns the selected jobs from jobsBox"
        spacesCount = MasterConfig.JNAME_JSTATE_SPACES_COUNT
        jobsSelectionList = []
        indxList = self.jobsBox.curselection()
        for indx in indxList:
            totalJobName = self.jobsBox.get( indx )
            jobName = totalJobName.partition( '  ' )[0]
            jobsSelectionList.append( jobName )
        return jobsSelectionList



    def mapClientAddr2Job (self, clientAddr):
        """maps the client address to its dedicated job object,
            clientAddr : the address of client to mapped"""
        return self.mapClientAddr2Connection( clientAddr ).ServerJob

    
    def mapJobName2Job (self, jobName):
        """maps the job name to its corresponding job object,
            jobName : the name of job to be mapped"""
        for thisJob in MasterApp.Jobs_List:
            if jobName == thisJob.JobName:
                return thisJob
        return None
        

    def mapClientAddr2Connection (self, clientAddr):
        """maps the client address to its corresponding connection job,
            clientAddr : the address of the client to be mapped"""
        for thisConnection in MasterApp.Servers_List:
            if thisConnection.clientAddr[0] == clientAddr:
                return thisConnection
        return None



    def checkIfJobExists (self, jobName):
        """checks if the given job name exists in jobs box,
            jobName : the name of the job to be checked"""
        if jobName in self.jobsBox.get( 0, tkinter.END ):
            return True
        return False



    def write (self, s):
        """writes s in logbox"""
        self.logBox.insert( tkinter.END, s )



    def reorderJobs (self):
        """reorders the jobs listes on jobs box,
            the order is, F S Q WP R"""
        MasterApp.LockThrd.acquire()
        runningJobs = []
        waitedPackJobs = []
        queuedJobs = []
        stoppedJobs = []
        finishedJobs = []
        orderedJobs = []
        for thisJob in MasterApp.Jobs_List:
            if thisJob.JobState == JobServer.JOB_RUNNING_STAT:
                runningJobs.append( thisJob )
            if thisJob.JobState == JobServer.JOB_WAITPACK_STAT:
                waitedPackJobs.append( thisJob )
            elif thisJob.JobState == JobServer.JOB_QUEUED_STAT:
                queuedJobs.append( thisJob )
            elif thisJob.JobState == JobServer.JOB_STOPPED_STAT:
                stoppedJobs.append( thisJob )
            elif thisJob.JobState == JobServer.JOB_FINISHED_STAT:
                finishedJobs.append( thisJob )
        orderedJobs = finishedJobs + stoppedJobs + queuedJobs + waitedPackJobs + runningJobs
        self.jobsBox.delete( 0, tkinter.END )
        for thisJob in orderedJobs:
            self.appendJob( thisJob )
        MasterApp.LockThrd.release()
        
                

    def reorderServers (self):
        """reorders the servers listed on slaves box,
            the order is, I A WJ WP"""
        MasterApp.LockThrd.acquire()
        idleServers = []
        autoServers = []
        WJServers = []
        WPServers = []
        orderedServers = []
        for thisServer in MasterApp.Servers_List:
            if thisServer.ServerState == JobServer.SERVER_IDLE_STAT:
                idleServers.append( thisServer )
            elif thisServer.ServerState == JobServer.SERVER_AUTOMATED_STAT:
                autoServers.append( thisServer )
            elif thisServer.ServerState == JobServer.SERVER_WAITJOB_STAT:
                WJServers.append( thisServer )
            if thisServer.ServerState == JobServer.SERVER_WAITPACK_STAT:
                WPServers.append( thisServer )
        orderedServers = idleServers + autoServers + WJServers + WPServers
        self.slavesBox.delete( 0, tkinter.END )
        for thisServer in orderedServers:
            self.appendServer( thisServer )
        MasterApp.LockThrd.release()
        


    def clearFinishedJobs (self):
        """clears all finished jobs from jobs box"""
        MasterApp.LockThrd.acquire()
        for thisJob in MasterApp.Jobs_List[:]:
            if thisJob.JobState == JobServer.JOB_FINISHED_STAT:
                self.removeJob( thisJob.JobName )
                MasterApp.Jobs_List.remove( thisJob )
        MasterApp.LockThrd.release()
                    

    

    def clearStoppedJobs (self):
        """clears all stopped jobs from jobs box"""
        MasterApp.LockThrd.acquire()
        for thisJob in MasterApp.Jobs_List[:]:
            if thisJob.JobState == JobServer.JOB_STOPPED_STAT:
                self.removeJob( thisJob.JobName )
                MasterApp.Jobs_List.remove( thisJob )
        MasterApp.LockThrd.release()



    def clearSelectedJobs (self):
        """clears the selected jobs from jobs box"""
        thisJobNames = self.getSelectedJobs()
        if not thisJobNames:
            self.insertLog( "no job is selected to be cleared", 'inf' )
            return
        MasterApp.LockThrd.acquire()
        for thisJobName in thisJobNames:
            thisJob = self.mapJobName2Job( thisJobName )
            if thisJob.JobState == JobServer.JOB_RUNNING_STAT or thisJob.JobState == JobServer.JOB_QUEUED_STAT or thisJob.JobState == JobServer.JOB_WAITPACK_STAT:
                self.insertLog( "the job, <" + thisJobName + "> is in " + thisJob.JobState + " status and can't be cleared", 'war' )
                continue
            self.removeJob( thisJob.JobName )
            MasterApp.Jobs_List.remove( thisJob )
        MasterApp.LockThrd.release()
        



    def clearInfobox (self):
        """clears info box"""
        self.infoBox.delete( '1.0', tkinter.END )


    def clearLogbox (self):
        """clears log box"""
        self.logBox.delete( '1.0', tkinter.END )
    

    def clearRLogbox (self):
        """clears render log box"""
        self.rLogBox.delete( '1.0', tkinter.END )


    def clearAllLogs (self):
        """clears all the logs"""
        self.clearInfobox()
        self.clearLogbox()
        self.clearRLogbox()


    def freshAll (self):
        """does all the clear and reorder tasks"""
        self.clearFinishedJobs()
        #self.clearStoppedJobs()
        self.clearAllLogs()
        self.reorderJobs()
        self.reorderServers()


    def exitProc (self):
        """exits GUI"""
        self.destroy()
        self.exitApp()


    def runGUI (self):
        """starts the user interface"""
        self.wm_iconbitmap( 'icon.ico' )
        self.wm_title( "RenderPipe" )
        self.wm_minsize( 1024, 768 )
        self.wm_state( 'zoomed' )
        self.mainloop()

        
        
    def importJob (self):
        """imports the job from file (.rp)"""
        srcPath = tkinter.filedialog.askopenfilename( filetypes = [("rpipe file", ".rp")] )
        if (srcPath == ''):
            return
        try:
            impFile = open( srcPath, 'r' )

            engineType = impFile.readline()
            jobName = impFile.readline()
            jobStartFrame = impFile.readline()
            jobEndFrame = impFile.readline()
            jobPackSize = impFile.readline()
            jobSrcFile = impFile.readline()
            jobDestPath = impFile.readline()
            jobOutName = impFile.readline()

            if engineType[:-1] == JobServer.MAYA_NGN:
                self.engineTypeData.set( JobServer.MAYA_NGN )
                self.setMayaGUI()
            elif engineType[:-1] == JobServer.XSI_NGN:
                self.engineTypeData.set( JobServer.XSI_NGN )
                self.setXSIGUI()
            elif engineType[:-1] == JobServer._3DSMAX_NGN:
                self.engineTypeData.set( JobServer._3DSMAX_NGN )
                self.set3DSMaxGUI()
            elif engineType[:-1] == JobServer.NUKE_NGN:
                self.engineTypeData.set( JobServer.NUKE_NGN )
                self.setNukeGUI()
            self.jobNameData.set( jobName[:-1] )
            self.jobStartFrmData.set( jobStartFrame[:-1] )
            self.jobEndFrmData.set( jobEndFrame[:-1] )
            self.jobPackSizeData.set( jobPackSize[:-1] )
            self.jobSrcFileData.set( jobSrcFile[:-1] )
            self.jobDestPathData.set( jobDestPath[:-1] )
            self.jobOutNameData.set( jobOutName[:-1] )
            # make this job queued
            #
            if tkinter.messagebox.askyesno( "RPipe", "do you want to make this job queued" ):
                self.queueJob( jobName[:-1],
                               jobStartFrame[:-1], jobEndFrame[:-1], jobPackSize[:-1],
                               jobSrcFile[:-1], jobDestPath[:-1], jobOutName[:-1] )
        except IOError as err:
            self.insertLog( "importing failed -> " + str( err ), 'err' )
        finally:
            impFile.close()
            self.insertLog( "importing done from " + srcPath, 'inf' )
        
        

    def exportJob (self):
        """exports the job to file (.rp)"""
        srcPath = tkinter.filedialog.asksaveasfilename( filetypes = [("rpipe file", ".rp")] )
        if (srcPath == ''):
            return
        try:
            expFile = open( srcPath, 'w' )

            expFile.write( str( self.engineTypeData.get() ) + "\n" )
            expFile.write( str( self.jobNameData.get() ) + "\n" )
            expFile.write( str( self.jobStartFrmData.get() ) + "\n" )
            expFile.write( str( self.jobEndFrmData.get() ) + "\n" )
            expFile.write( str( self.jobPackSizeData.get() ) + "\n" )
            expFile.write( str( self.jobSrcFileData.get() ) + "\n" )
            expFile.write( str( self.jobDestPathData.get() ) + "\n" )
            expFile.write( str( self.jobOutNameData.get() ) + "\n" )
        except IOError as err:
            self.insertLog( "exporting failed -> " + str( err ), 'err' )
        finally:
            expFile.close()
            self.insertLog( "exporting done to " + srcPath, 'inf' )
            

    def showHelp (self):
        """opens the online help"""
        os.system( "explorer http://www.hsaraf.com/RenderPipe/doc.html" )
        pass

    def showAbout (self):
        """opens the about"""
        tkinter.messagebox.showinfo( "About", "RenderPipe 1.1\n\n\nCopyright (C) 2010 2011 Hadi Saraf\nRPipe is released under GNU General Public License\n" )

    def gotoFxhues (self):
        """opens the web site"""
        os.system( "explorer http://www.hsaraf.com/" )
        
