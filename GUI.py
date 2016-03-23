"""     AUTHORS: Braam Otto  & LKOCK                          """
"""     ORGANISATION: SKA SA and MESA Solutions (Pty) Ltd.    """
"""     WEB: http://www.mesasolutions.co.za/                  """
"""     CONTACT: braam@mesasolutions.co.za                    """

import wx
import RSA5106A_Control_Functions as RSA_Control
import numpy as np
import threading
from threading import Thread
import time
import subprocess
import Parameters_GUI as Params_GUI
import os 

class RSA_GUI(wx.Frame):
    
    def __init__(self, *args, **kwargs):
        super(RSA_GUI, self).__init__(*args, **kwargs)
        self.InitUI()                    
        
    def InitUI(self):        
        self.testing = False
        
        print 'Initialising...'
        
        #self.path = 'F:\\RSA5106B_Data\\'
        
        W=1024
        H=768
        self.comms_est = False        
        
        self.count = 0
        
        menubar = wx.MenuBar()

        ''' MENUS '''
        fileMenu = wx.Menu()
        nfmi = wx.MenuItem(fileMenu, wx.ID_NEW, '&New\tCtrl+N')        
        fileMenu.AppendItem(nfmi)
        self.Bind(wx.EVT_MENU, self.NewFile, nfmi)
        
        fileMenu.Append(wx.ID_OPEN, '&Open\tCtrl+O')
        fileMenu.Enable(wx.ID_OPEN, False)
        fileMenu.Append(wx.ID_SAVE, '&Save\tCtrl+S')
        fileMenu.Enable(wx.ID_SAVE, False)
        fileMenu.AppendSeparator()
        
        imp = wx.Menu()
        imp.Append(1, 'Import captured data')
        imp.Append(2, 'Import settings')        
        imp.Enable(1, False)
        imp.Enable(2, False)
        
        fileMenu.AppendMenu(wx.ID_ANY, 'I&mport', imp)        

        qmi = wx.MenuItem(fileMenu, wx.ID_EXIT, '&Quit\tCtrl+Q')
        fileMenu.AppendItem(qmi)
        self.Bind(wx.EVT_MENU, self.OnQuit, qmi)
        
        runMenu = wx.Menu()
        icmi = wx.MenuItem(runMenu, wx.ID_ANY, '&Initiate GPIB Comms')
        runMenu.AppendItem(icmi)
        self.Bind(wx.EVT_MENU, self.InitiateComms, icmi) 
        
        runMenu.Append(3,'S&ingle Span')        
        runMenu.Append(4,'&Frequency Sweep')
        runMenu.Enable(3, False)        
        runMenu.Enable(4, False)

        helpMenu = wx.Menu()
        htu = wx.MenuItem(helpMenu, wx.ID_ANY, '&How to Use RSA5106B Control')
        helpMenu.AppendItem(htu)
        self.Bind(wx.EVT_MENU, self.HowTo, htu)
        
        ami = wx.MenuItem(helpMenu, wx.ID_ANY, '&About')
        helpMenu.AppendItem(ami)
        self.Bind(wx.EVT_MENU, self.OnAbout, ami)        
        
        menubar.Append(fileMenu, '&File')
        menubar.Append(runMenu, '&Run')
        menubar.Append(helpMenu, '&Help')
        self.SetMenuBar(menubar)                
        
        ''' FREQUENCY SETUP '''
        panel_top = wx.Panel(self)
        
        ''' PROGRESS GAUGES '''
        wx.StaticText(panel_top, -1, 'Percentage Complete:', ((0.575*W, 0.76*H)))
        self.gauge_current = wx.Gauge(panel_top, -1, 100, size=(250, 25), pos=(0.72*W, 0.75*H)) 
        self.gauge_current.SetValue(0)
        ''' <<< >>> '''
               
        wx.StaticText(panel_top, -1, 'Start Frequency:', (0.05*W, 0.05*H))
        self.start_freq_txt= wx.TextCtrl(panel_top, -1, size=(80, 20), pos=(0.15*W, 0.05*H))
        self.start_freq_txt.SetValue('70.0')
        self.start_freq_txt.Enable(False)
        
        self.freqs=['kHz', 'MHz', 'GHz']
        self.start_cb=wx.ComboBox(panel_top, -1, value=self.freqs[1], pos=(0.24*W, 0.05*H), size=(52, -1), choices=self.freqs, style=wx.CB_READONLY)
        self.start_cb.Enable(False)
        
        if self.start_cb.GetValue()=='kHz':
            self.start_unit = 1e3
        if self.start_cb.GetValue()=='MHz':
            self.start_unit = 1e6
        if self.start_cb.GetValue()=='GHz':
            self.start_unit = 1e9
        
        wx.StaticText(panel_top, -1, 'Stop Frequency:', (0.3*W, 0.05*H))
        self.stop_freq_txt= wx.TextCtrl(panel_top, -1, size=(80, 20), pos=(0.4*W, 0.05*H))
        self.stop_freq_txt.SetValue('100.0')
        self.stop_freq_txt.Enable(False)
        
        self.stop_cb=wx.ComboBox(panel_top, -1, value=self.freqs[1], pos=(0.49*W, 0.05*H), size=(52, -1), choices=self.freqs, style=wx.CB_READONLY)
        self.stop_cb.Enable(False)
        
        if self.stop_cb.GetValue()=='kHz':
            self.stop_unit = 1e3
        if self.stop_cb.GetValue()=='MHz':
            self.stop_unit = 1e6
        if self.stop_cb.GetValue()=='GHz':
            self.stop_unit = 1e9
            
        wx.StaticText(panel_top, -1, 'Frequency Span:', (0.55*W, 0.05*H))
        self.span_freq_txt= wx.TextCtrl(panel_top, -1, size=(80, 20), pos=(0.65*W, 0.05*H))
        self.span_freq_txt.Enable(False)
        
        ''' SPAN CALCULATION '''
        self.start = np.float(self.start_freq_txt.GetValue())*self.start_unit
        self.stop = np.float(self.stop_freq_txt.GetValue())*self.stop_unit
        self.span = self.stop-self.start
                
        ''' <<< >>> '''
        self.span_freq_txt.SetValue(np.str(self.span/1e6))
        self.span_cb=wx.ComboBox(panel_top, -1, value=self.freqs[1], pos=(0.74*W, 0.05*H), size=(52, -1), choices=self.freqs, style=wx.CB_READONLY)
        self.span_cb.Enable(False)
        
        self.freq_setup_btn = wx.Button(panel_top, -1, 'Frequency Setup', pos=(0.84*W, 0.045*H))
        self.freq_setup_btn.Disable()                
        self.Bind(wx.EVT_BUTTON, self.FreqSetup, id=-1)
        
        ''' ACQUISITION SETUP '''              
        wx.StaticText(panel_top, -1, 'RF Attenuation:', (0.05*W, 0.15*H))
        self.att_txt= wx.TextCtrl(panel_top, -1, size=(80, 20), pos=(0.15*W, 0.15*H))
        self.att_txt.SetValue('0.0')
        self.att_txt.Enable(False)
                
        wx.StaticText(panel_top, -1, '[dB]', (0.235*W, 0.15*H))
        self.att = np.float(self.att_txt.GetValue())
        
        wx.StaticText(panel_top, -1, 'Acquisition Length:', (0.29*W, 0.15*H))
        self.acq_length_txt= wx.TextCtrl(panel_top, -1, size=(80, 20), pos=(0.4*W, 0.15*H))
        self.acq_length_txt.SetValue('343.596')
        self.acq_length_txt.Enable(False)
        
        times=['s', 'ms', 'us']
        self.acq_length_cb=wx.ComboBox(panel_top, -1, value=times[0], pos=(0.49*W, 0.15*H), size=(52, -1), choices=times, style=wx.CB_READONLY)
        self.acq_length_cb.Enable(False)
        
        if self.acq_length_cb.GetValue()=='s':
            self.acq_length_unit = 1.0
        if self.acq_length_cb.GetValue()=='ms':
            self.acq_length_unit = 1e-3
        if self.acq_length_cb.GetValue()=='us':
            self.acq_length_unit = 1e-6
        self.acq_length = np.float(self.acq_length_txt.GetValue())*self.acq_length_unit
        
        wx.StaticText(panel_top, -1, 'Acquisition BW:', (0.55*W, 0.15*H))
        self.acq_bw_cb=wx.ComboBox(panel_top, -1, value=self.freqs[1], pos=(0.74*W, 0.15*H), size=(52, -1), choices=self.freqs, style=wx.CB_READONLY)        
        self.acq_bw_cb.Enable(False)
        
        self.acq_bw_options=['0.3125','0.625','1.25', '2.50', '5.00', '10.0', '20.0', '40.0', '80.0', '165.0']
        self.acq_bw_cb1=wx.ComboBox(panel_top, -1, value=self.acq_bw_options[2], pos=(0.65*W, 0.15*H), size=(75, -1), choices=self.acq_bw_options, style=wx.CB_READONLY)
        self.acq_bw_cb1.Bind(wx.EVT_COMBOBOX, self.onAcqBWCombo)
        self.acq_bw_cb1.Enable(False)
                
        if self.acq_bw_cb.GetValue()=='kHz':
            self.acq_bw_unit = 1e3
        if self.acq_bw_cb.GetValue()=='MHz':
            self.acq_bw_unit = 1e6
        if self.acq_bw_cb.GetValue()=='GHz':
            self.acq_bw_unit = 1e9        
        self.acq_bw = np.float(self.acq_bw_options[self.acq_bw_cb1.GetSelection()])*self.acq_bw_unit        

        self.acq_setup_btn = wx.Button(panel_top, 0, 'Acquisition Setup', pos=(0.84*W, 0.145*H))
        self.acq_setup_btn.Disable()                
        self.Bind(wx.EVT_BUTTON, self.AcqSetup, id=0)
        
        ''' MESSAGE INTERFACE ''' 
        self.message_txt= wx.TextCtrl(panel_top, -1, size=(700, 300), pos=(0.15*W, 0.25*H), style = wx.TE_MULTILINE)
        self.message_txt.AppendText('Using the RSA5106B Automated Control Software:\n')
        self.message_txt.AppendText('----------------------------------------------------------\n')
        self.message_txt.AppendText('1) Initiate GPIB Comms\n')
        self.message_txt.AppendText('2) Parameters Setup\n')
        self.message_txt.AppendText('3) Frequency Setup\n')
        self.message_txt.AppendText('4) Acquisition Setup\n')
        self.message_txt.AppendText('5) Acquire Data\n')
        self.message_txt.AppendText('6) Post Processing (optional) is automatic when selected in (2) Parameter Setup\n')
        self.message_txt.AppendText('----------------------------------------------------------\n')
        self.message_txt.AppendText('\n')
        self.message_txt.AppendText('Welcome>>>\n')
        self.message_txt.AppendText('Please Initiate Communication with GPIB Device>>>\n')
        
        ''' INITIATE COMMS ''' 
        self.comms_btn = wx.Button(panel_top, 1, 'Initiate GPIB Comms', pos=(0.05*W, 0.75*H))                
        self.Bind(wx.EVT_BUTTON, self.InitiateComms, id=1)
        self.comms_btn.SetFocus()        
        
        ''' ACQUIRE DATA ''' 
        self.data_btn = wx.Button(panel_top, 2, 'Acquire Data', pos=(0.2*W, 0.75*H))
        self.data_btn.Disable()                
        self.Bind(wx.EVT_BUTTON, self.AcquireData, id=2)
        
        ''' DISPLAY DATA ''' 
        self.disp_data_btn = wx.Button(panel_top, 3, 'Display Data', pos=(0.3*W, 0.75*H))
        self.disp_data_btn.Disable()                
        self.Bind(wx.EVT_BUTTON, self.DisplayData, id=3)
        
        ''' PRE-AMPLIFIER '''
        self.pre_amp_check = wx.CheckBox(panel_top, -1, ' Internal Pre-Amplifier', (0.05*W, 0.675*H))
        self.pre_amp_check.SetValue(True)
        self.pre_amp_check.Enable(False)
        
        wx.StaticText(panel_top, -1, 'Ref Level:', (0.6*W, 0.675*H))
        self.ref_level_txt= wx.TextCtrl(panel_top, -1, size=(80, 20), pos=(0.675*W, 0.675*H))
        self.ref_level_txt.SetValue('-30.0')
        self.ref_level_txt.Enable(False)
        wx.StaticText(panel_top, -1, '[dBm]', (0.775*W, 0.675*H))                
        
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText('NO CONNECTION TO GPIB INSTRUMENT>>>ESTABLISH CONNECTION>>>')
        self.SetSize((W, H))
        self.SetTitle('RSA5106B Automated Control Software - Ver 0.5.1')
        self.Centre()        
        ico = wx.Icon('favicon.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)
        self.Show(True)                
    
    def FreqSetup(self, event):         
        self.message_txt.AppendText('Frequency Setup...\n')
        freq_test_error=False
        if len(self.start_freq_txt.GetValue())==0:
            print 'Please enter a valid Start Frequency'
            dial = wx.MessageDialog(None, 'Enter START FREQUENCY to continue', 'Error', wx.OK | wx.ICON_ERROR)
            dial.ShowModal()
            freq_test_error=True                    
        
        if len(self.stop_freq_txt.GetValue())==0:
            print 'Please enter a valid Stop Frequency'
            dial = wx.MessageDialog(None, 'Enter STOP FREQUENCY to continue', 'Error', wx.OK | wx.ICON_ERROR)
            dial.ShowModal()
            freq_test_error=True                    
        
        if len(self.span_freq_txt.GetValue())==0:
            print 'Please enter a valid Frequency Span'
            dial = wx.MessageDialog(None, 'Enter FREQUENCY SPAN to continue', 'Error', wx.OK | wx.ICON_ERROR)
            dial.ShowModal()
            freq_test_error=True                    
        
        ###############################################################################################
        file_read=open('python_parameters.txt','r')
        try:
            for line in file_read:
                if line.find('AntGainFilenameNumber')==0:
                    start=line.find('=')+1
                    stop=-1
                    antenna_type = line[start:stop].strip()
                if line.find('DataFilename_base')==0:
                    start=line.find('\'')+1
                    stop=line[start:].find('\'')                    
                    self.database_filename=line[start:start+stop]            
        finally:
            file_read.close()
        
        if self.testing == True:
            Database_Path = 'D:\\Linux_HDD\\Work_Related\\eclipse_workspace\\XPS2_Backup\\RSA5106B_Control_13Nov2013\\src\\'
        else:            
#             Database_Path = 'D:\\Dropbox\\Dropbox\\eclipse_workspace\\RSA5106B_Control_13Nov2013\\Ver_0_4_1\\'
            Database_Path = 'C:\\RFI Archive\\'
            
        antenna_options = {0 : Database_Path+'Equipment_Database\Passive_Antennas\Antenna_MESA_GLPDA.csv',
                           1 : Database_Path+'Equipment_Database\Passive_Antennas\Antenna_MESA_KLPDA1.csv',
                           2 : Database_Path+'Equipment_Database\Passive_Antennas\Antenna_MESA_KLPDA3.csv',
                           3 : Database_Path+'Equipment_Database\Passive_Antennas\Antenna_Houwteq_EMCO3115_FRH_Small.csv',
                           4 : Database_Path+'Equipment_Database\Passive_Antennas\Antenna_Houwteq_EMCO3106B_FRH_Large.csv',
                           5 : Database_Path+'Equipment_Database\Passive_Antennas\Antenna_Houwteq_EMCO3141_BiConiLog_FLPDA.csv',
                           6 : Database_Path+'Equipment_Database\Passive_Antennas\No_Antenna.csv'}
        
        antenna_file = open(antenna_options[np.int(antenna_type)-1],'r')
        num_entries = len(antenna_file.readlines())
        antenna_file.close()
        print 'Number of entries in Antenna File: ', num_entries
        count=0
        start_freq_req=0
        stop_freq_req=0
        antenna_file = open(antenna_options[np.int(antenna_type)-1],'r')
        for line in antenna_file:
            count=count+1            
            if count==3:
                start_freq_req = line.strip().split(',')[0]
            if count== num_entries:
                stop_freq_req = line.strip().split(',')[0]
        
        if self.start_cb.GetValue()=='kHz':
            self.start_unit = 1e3
        if self.start_cb.GetValue()=='MHz':
            self.start_unit = 1e6
        if self.start_cb.GetValue()=='GHz':
            self.start_unit = 1e9
        
        if self.stop_cb.GetValue()=='kHz':
            self.stop_unit = 1e3
        if self.stop_cb.GetValue()=='MHz':
            self.stop_unit = 1e6
        if self.stop_cb.GetValue()=='GHz':
            self.stop_unit = 1e9
            
       # print 'Antenna Start Freq: ', np.float(start_freq_req), ' Antenna Stop Freq: ', np.float(stop_freq_req), '\n'
                
        if np.float(self.start_freq_txt.GetValue())*self.start_unit < np.float(start_freq_req):
            freq_test_error=True
            dlg = wx.MessageDialog(self,
            "The requested frequency range is outside of the antenna specification as defined in: "+
            antenna_options[np.int(antenna_type)-1],
            "Invalid Frequency Range Detected", wx.OK|wx.CANCEL|wx.ICON_WARNING)
            result = dlg.ShowModal()
            
            dlg.Destroy()
            if result == wx.ID_OK:
                confirm=True
            
            self.start_freq_txt.SetValue(np.str(np.float(start_freq_req)/self.start_unit))            
            self.stop_freq_txt.SetValue(np.str(np.float(stop_freq_req)/self.stop_unit))
            print 'Adjusted Start Frequency: ', self.start_freq_txt.GetValue(), self.start_cb.GetValue()
            self.message_txt.AppendText('Adjusted Start Frequency>>>\t'+self.start_freq_txt.GetValue()+self.start_cb.GetValue()+'\n')
            print 'Adjusted Stop Frequency: ', self.stop_freq_txt.GetValue(), self.stop_cb.GetValue()
            self.message_txt.AppendText('Adjusted Stop Frequency>>>\t'+self.stop_freq_txt.GetValue()+self.stop_cb.GetValue()+'\n')
            
            self.start = np.float(self.start_freq_txt.GetValue())*self.start_unit
            self.stop = np.float(self.stop_freq_txt.GetValue())*self.stop_unit
            self.span = self.stop-self.start
            self.span_freq_txt.SetValue(np.str(self.span/1e6))
            print 'Adjusted Frequency Span: ', self.span_freq_txt.GetValue(), self.span_cb.GetValue()            
            self.message_txt.AppendText('Frequency Span>>>\t'+self.span_freq_txt.GetValue()+self.span_cb.GetValue()+'\n')
            self.message_txt.AppendText('>>>\n')
            
        if freq_test_error==False:                        
            self.start = np.float(self.start_freq_txt.GetValue())*self.start_unit
            self.stop = np.float(self.stop_freq_txt.GetValue())*self.stop_unit
            self.span = self.stop-self.start
#            self.centre_freq = self.start+self.span/2

            print 'Start Frequency: ', self.start_freq_txt.GetValue(), self.start_cb.GetValue()
            self.message_txt.AppendText('Start Frequency>>>\t\t'+self.start_freq_txt.GetValue()+self.start_cb.GetValue()+'\n')
            ''' <<< >>> '''
            self.span_freq_txt.SetValue(np.str(self.span/1e6))
            print 'Adjusted Frequency Span: ', self.span_freq_txt.GetValue(), self.span_cb.GetValue()
            print 'Stop Frequency: ', self.stop_freq_txt.GetValue(), self.stop_cb.GetValue()+'\n'  
            self.message_txt.AppendText('Adjusted Frequency Span>>>\t'+self.span_freq_txt.GetValue()+self.span_cb.GetValue()+'\n')
            self.message_txt.AppendText('Stop Frequency>>>\t\t'+self.stop_freq_txt.GetValue()+self.stop_cb.GetValue()+'\n')
            self.message_txt.AppendText('>>>\n')
            
            self.message_txt.AppendText('Device ready for acquisition setup>>>\n')
            self.message_txt.AppendText('>>>\n')
            self.acq_setup_btn.Enable()
            
            self.att_txt.Enable(True)
            self.acq_length_txt.Enable(True)
            self.acq_length_cb.Enable(True)
            self.acq_bw_cb1.Enable(True)
#            self.acq_bw_cb.Enable(True)

            self.pre_amp_check.Enable(True)
            self.ref_level_txt.Enable(True)
##zzzzz
    def onAcqBWCombo(self, event):
        """ NEW 8GB RAM VALUES """
        if self.acq_bw_cb1.GetValue()=='0.3125':
            self.acq_length_txt.SetValue('1374.0')
        if self.acq_bw_cb1.GetValue()=='0.625':
            self.acq_length_txt.SetValue('687.193')
        if self.acq_bw_cb1.GetValue()=='1.25':
            self.acq_length_txt.SetValue('343.596')
        if self.acq_bw_cb1.GetValue()=='2.50':
            self.acq_length_txt.SetValue('171.798')
        if self.acq_bw_cb1.GetValue()=='5.00':
            self.acq_length_txt.SetValue('152.710')
        if self.acq_bw_cb1.GetValue()=='10.0':
            self.acq_length_txt.SetValue('76.355')
        if self.acq_bw_cb1.GetValue()=='20.0':
            self.acq_length_txt.SetValue('38.177')
        if self.acq_bw_cb1.GetValue()=='40.0':
            self.acq_length_txt.SetValue('19.1')
        if self.acq_bw_cb1.GetValue()=='80.0':
            self.acq_length_txt.SetValue('10.7')
        if self.acq_bw_cb1.GetValue()=='165.0':
            self.acq_length_txt.SetValue('5.4')

        
        """ OLD 4GB RAM VALUES """

##        '0.3125','0.625','1.25', '2.50', '5.00', '10.0', '20.0', '40', '80', '165'
##        if self.acq_bw_cb1.GetValue()=='0.3125':
##         self.acq_length_txt.SetValue('343.6')
##        if self.acq_bw_cb1.GetValue()=='0.625':
##         self.acq_length_txt.SetValue('171.8')
##        if self.acq_bw_cb1.GetValue()=='1.25':
##         self.acq_length_txt.SetValue('85.9')
##        if self.acq_bw_cb1.GetValue()=='2.50':
##         self.acq_length_txt.SetValue('42.9')
##        if self.acq_bw_cb1.GetValue()=='5.00':
##         self.acq_length_txt.SetValue('38.2')
##        if self.acq_bw_cb1.GetValue()=='10.0':
##         self.acq_length_txt.SetValue('19.1')
##        if self.acq_bw_cb1.GetValue()=='20.0':
##         self.acq_length_txt.SetValue('9.5')
##        if self.acq_bw_cb1.GetValue()=='25.0':
##         self.acq_length_txt.SetValue('4.8')
##        if self.acq_bw_cb1.GetValue()=='30.0':
##         self.acq_length_txt.SetValue('7.2')
##        if self.acq_bw_cb1.GetValue()=='60.0':
##         self.acq_length_txt.SetValue('3.6')
##        if self.acq_bw_cb1.GetValue()=='110.0':
##         self.acq_length_txt.SetValue('1.8')

                            
    def AcqSetup(self, event):
        if self.acq_length_cb.GetValue()=='s':
            self.acq_length_unit = 1.0
        if self.acq_length_cb.GetValue()=='ms':
            self.acq_length_unit = 1e-3
        if self.acq_length_cb.GetValue()=='us':
            self.acq_length_unit = 1e-6
        self.acq_length = np.float(self.acq_length_txt.GetValue())*self.acq_length_unit
        
        acq_test_error=False
        self.message_txt.AppendText('Acquisition Setup...\n')
        if len(self.acq_length_txt.GetValue())==0:
            print 'Please enter a Acquisition Length'
            dial = wx.MessageDialog(None, 'Enter ACQUISITION LENGTH to continue', 'Error', wx.OK | wx.ICON_ERROR)
            dial.ShowModal()
            acq_test_error=True
        else:
            print 'Acquisition Length: ', self.acq_length_txt.GetValue(), self.acq_length_cb.GetValue()
            self.message_txt.AppendText('Acquisition Length: '+self.acq_length_txt.GetValue()+self.acq_length_cb.GetValue()+'\n')             
        
#        if len(self.acq_bw_txt.GetValue())==0:
#            print 'Please enter a Acquisition BW'
#            dial = wx.MessageDialog(None, 'Enter ACQUISITION BW to continue', 'Error', wx.OK | wx.ICON_ERROR)
#            dial.ShowModal()
#            acq_test_error=True
#        else:
#            print 'Acquisition BW: ', self.acq_bw_txt.GetValue(), self.acq_bw_cb.GetValue()                
#            self.message_txt.AppendText('Acquisition BW: '+self.acq_bw_txt.GetValue()+self.acq_bw_cb.GetValue()+'\n')

            print 'Acquisition BW: ', self.acq_bw_options[self.acq_bw_cb1.GetSelection()]
            self.message_txt.AppendText('Acquisition BW: '+self.acq_bw_options[self.acq_bw_cb1.GetSelection()]+self.acq_bw_cb.GetValue()+'\n')
            self.message_txt.AppendText('>>>\n')
                
        if acq_test_error==False:
            if self.acq_bw_cb.GetValue()=='kHz':
                self.acq_bw_unit = 1e3
            if self.acq_bw_cb.GetValue()=='MHz':
                self.acq_bw_unit = 1e6
            if self.acq_bw_cb.GetValue()=='GHz':
                self.acq_bw_unit = 1e9
#            self.acq_bw = np.float(self.acq_bw_txt.GetValue())*self.acq_bw_unit
            self.acq_bw = np.float(self.acq_bw_options[self.acq_bw_cb1.GetSelection()])*self.acq_bw_unit
                                    
            self.num_steps = np.ceil(self.span/self.acq_bw)                        
            self.message_txt.AppendText('Number Acquisition Steps>>>\t'+np.str(self.num_steps)+'\n')
                                  
            centre_freq=self.start+self.acq_bw/2
            if self.testing == True:
                print "TESTING>>> No GPIB Control Freq. Set"
            else:                        
                RSA_Control.GPIB_SetFreq(centre_freq, self.acq_bw, self.RSA)
            
            self.message_txt.AppendText('Stopping acquisitions while instrument is configured>>>\n')  
#            self.message_txt.AppendText('Marker added to centre frequency>>>\n')
##            zzzzz
            if self.acq_bw_cb1.GetValue()=='0.3125':
                self.samples = self.acq_length/2600e-9
            if self.acq_bw_cb1.GetValue()=='0.625':
                self.samples = self.acq_length/1300e-9
            if self.acq_bw_cb1.GetValue()=='1.25':
                self.samples = self.acq_length/640e-9
            if self.acq_bw_cb1.GetValue()=='2.50':
                self.samples = self.acq_length/320e-9
            if self.acq_bw_cb1.GetValue()=='5.00':
                self.samples = self.acq_length/160e-9
            if self.acq_bw_cb1.GetValue()=='10.0':
                self.samples = self.acq_length/80e-9
            if self.acq_bw_cb1.GetValue()=='20.0':
                self.samples = self.acq_length/40e-9
            if self.acq_bw_cb1.GetValue()=='40.0':
                self.samples = self.acq_length/20e-9
            if self.acq_bw_cb1.GetValue()=='80.0':
                self.samples = self.acq_length/10e-9
            if self.acq_bw_cb1.GetValue()=='165.0':
                self.samples = self.acq_length/5e-9
            
            
            self.att = np.float(self.att_txt.GetValue())
            self.ref = np.float(self.ref_level_txt.GetValue())
            
            if self.testing == True:
                print "TESTING>>> No GPIB Control Acq. Set"
            else:                
                RSA_Control.GPIB_SetAcq(self.ref, self.att, self.acq_length, self.acq_bw, self.samples, self.RSA, self.pre_amp_check.GetValue())
            
            ###############################################################################################
            file_start=open('file_start.txt','r')     
            self.start_number = file_start.read()
            file_start.close()
            
            file_read=open('python_parameters.txt','r')
            file_write=open('python_parameters_tmp.txt','w')
            try:
                for line in file_read:
                    if line.find('DataFilename_start_num')==0:
                        stop=line.find('=')+1                    
                        file_write.write(line[0:stop]+' '+np.str(self.start_number)+'\n')
                    elif line.find('DataFilename_end_num')==0:
                        stop=line.find('=')+1                    
                        file_write.write(line[0:stop]+' '+np.str(np.int(self.start_number)+np.int(self.num_steps)-1)+'\n')
                    else:
                        file_write.write(line)            
            finally:
                file_write.close()
                file_read.close()
                os.remove('python_parameters.txt')
                os.rename('python_parameters_tmp.txt', 'python_parameters.txt')
            
            self.message_txt.AppendText('Device ready for data acquisition>>>\n')
            self.message_txt.AppendText('>>>\n')
            self.data_btn.Enable()            
            
    def InitiateComms(self, event):        
        print 'Establishing GPIB Communication...'
        self.message_txt.AppendText('Establishing GPIB Communication...\n')
        self.resource_name='GPIB0::1::INSTR'
        
        [GPIB_Found, self.RSA, IDN_company, IDN_model, IDN_serial, IDN_firmware, RSA_OPT] = RSA_Control.GPIB_Init(self.resource_name)        
        if GPIB_Found == True:
            self.message_txt.AppendText('GPIB Instrument Found:\n')
            self.message_txt.AppendText('Company>>>\t\t'+IDN_company+'\n')
            self.message_txt.AppendText('Model>>>\t\t'+IDN_model+'\n')
            self.message_txt.AppendText('Serial>>>\t\t'+IDN_serial+'\n')
            self.message_txt.AppendText('Firmware>>>\t\t'+IDN_firmware+'\n')            
            self.message_txt.AppendText('Installed Options>>>\t'+RSA_OPT+'\n')
            self.message_txt.AppendText('>>>\n')
            self.message_txt.AppendText('Please SETUP PARAMETERS>>>\n')
            self.message_txt.AppendText('>>>\n')            
            self.comms_est = True                        
            self.freq_setup_btn.Enable()
            self.statusbar.SetStatusText('CONNECTION TO GPIB INSTRUMENT ESTABLISHED>>>'+self.resource_name+'>>>IDLE>>>')                                   
            Params_GUI.Params_GUI(None)            
            
            self.start_freq_txt.Enable(True)
            self.start_cb.Enable(True)
            self.stop_freq_txt.Enable(True)
            self.stop_cb.Enable(True)            
                                                                  
        elif self.testing == True:
            print 'CODE TESTING MODE ENABLED>>>'
            dlg = wx.MessageDialog(self,"Code Testing Mode Enabled","CODE TESTING MODE", wx.OK|wx.ICON_INFORMATION)
            result = dlg.ShowModal()
            self.comms_est = True                        
            self.freq_setup_btn.Enable()                                               
            Params_GUI.Params_GUI(None)           
            
            self.start_freq_txt.Enable(True)
            self.start_cb.Enable(True)
            self.stop_freq_txt.Enable(True)
            self.stop_cb.Enable(True)
        else:
            self.message_txt.AppendText('No GPIB Instrument Found!\n')
            dlg = wx.MessageDialog(self,"No GPIB Instrument Found!","Communication Error", wx.OK|wx.ICON_ERROR)
            result = dlg.ShowModal()
            self.comms_est = False                             
                                                                                     
            
    def AcquireData(self, event):
        if self.comms_est==True:
            start(update_current, self, 0, np.int(self.num_steps))                                                
            start(get_data, self)                                                                 
        else:            
            self.message_txt.AppendText('No GPIB Instrument Found!\n')
            self.message_txt.AppendText('>>>\n')
            dlg = wx.MessageDialog(self,"No GPIB Instrument Found!","Communication Error", wx.OK|wx.ICON_ERROR)
            result = dlg.ShowModal()            
    
    def DisplayData(self, event):
        if self.comms_est==True:
            print 'Displaying Data...NEXT VERSION'
            self.message_txt.AppendText('Displaying Data...NEXT VERSION\n')
            self.message_txt.AppendText('>>>\n')
#             self.ask = RSA_Control.GPIB_Display(self.freq, self.data)
        else:            
            self.message_txt.AppendText('No GPIB Instrument Found!\n')
            self.message_txt.AppendText('>>>\n')
            dlg = wx.MessageDialog(self,"No GPIB Instrument Found!","Communication Error", wx.OK|wx.ICON_ERROR)
            result = dlg.ShowModal()
            
    def NewFile(self, event):
        print 'Clearing All'
        self.gauge_current.SetValue(0)
        
        self.message_txt.SetValue('')
        self.message_txt.AppendText('Using the RSA5106B Automated Control Software:\n')
        self.message_txt.AppendText('----------------------------------------------------------\n')
        self.message_txt.AppendText('1) Initiate GPIB Comms\n')
        self.message_txt.AppendText('2) Parameters Setup\n')
        self.message_txt.AppendText('3) Frequency Setup\n')
        self.message_txt.AppendText('4) Acquisition Setup\n')
        self.message_txt.AppendText('5) Acquire Data\n')
        self.message_txt.AppendText('6) Post Processing (optional) is automatic when selected in (2) Parameter Setup\n')
        self.message_txt.AppendText('----------------------------------------------------------\n')
        self.message_txt.AppendText('\n')
        self.message_txt.AppendText('Welcome>>>\n')
        self.message_txt.AppendText('Please Initiate Communication with GPIB Device>>>\n')
        
        self.start_freq_txt.SetValue('70.0')
        self.start_cb.SetValue(self.freqs[1])
        self.stop_freq_txt.SetValue('100.0')
        self.stop_cb.SetValue(self.freqs[1])
        self.span_freq_txt.SetValue('30.0')
        self.span_cb.SetValue(self.freqs[1])
        
        self.acq_bw_cb1.SetValue('1.25')
        self.acq_length_txt.SetValue('343.596')
        self.freq_setup_btn.Disable()
        self.acq_setup_btn.Disable()
        self.data_btn.Disable()
        self.disp_data_btn.Disable()
        self.statusbar.SetStatusText('NO CONNECTION TO GPIB INSTRUMENT>>>ESTABLISH CONNECTION>>>')
        
        self.start_freq_txt.Enable(False)
        self.start_cb.Enable(False)
        self.stop_freq_txt.Enable(False)
        self.stop_cb.Enable(False)
        
        self.att_txt.Enable(False)
        self.acq_length_txt.Enable(False)
        self.acq_length_cb.Enable(False)
        self.acq_bw_cb1.Enable(False)
        self.acq_bw_cb.Enable(False)
        
        self.ref_level_txt.Enable(False)
        self.ref_level_txt.SetValue('-30.0')
        self.pre_amp_check.SetValue(True)
        self.pre_amp_check.Enable(False) 
    
    def HowTo(self, e):
        self.message_txt.SetValue('')
        self.message_txt.AppendText('Using the RSA5106B Automated Control Software:\n')
        self.message_txt.AppendText('----------------------------------------------------------\n')
        self.message_txt.AppendText('1) Initiate GPIB Comms\n')
        self.message_txt.AppendText('2) Parameters Setup\n')
        self.message_txt.AppendText('3) Frequency Setup\n')
        self.message_txt.AppendText('4) Acquisition Setup\n')
        self.message_txt.AppendText('5) Acquire Data\n')
        self.message_txt.AppendText('6) Post Processing (optional) is automatic when selected in (2) Parameter Setup\n')
        self.message_txt.AppendText('----------------------------------------------------------\n')
        self.message_txt.AppendText('\n')
        
    def OnAbout(self, e):        
        description = """ This software automates measurements using the Tektronix RSA5106B Real-Time Spectrum Analyser """
        licence = """ """        
        info = wx.AboutDialogInfo()
        info.SetIcon(wx.Icon('MESA_favicon.ico', wx.BITMAP_TYPE_ICO))
        info.SetName('RSA5106B Automated Control Software')
        info.SetVersion('- Ver 0.5.1')
        info.SetDescription(description)
        info.SetCopyright('None')        
        info.SetWebSite('http://www.mesasolutions.co.za/')
#        info.SetLicence(licence)
        info.AddDeveloper('Braam Otto (MESA Solutions) - RSA5106B Control Software')
        info.AddDeveloper('L Kock (SKA-SA) - RSA5106B Control Software')
        info.AddDeveloper('Richard Lord (SKA-SA) - IDL Scripting')
#        info.AddDocWriter('Jan Bodnar')
#        info.AddArtist('The Tango crew')
#        info.AddTranslator('Jan Bodnar')
        wx.AboutBox(info)
            
    def OnQuit(self, event):
        dlg = wx.MessageDialog(self,
            "Do you really want to close this application?",
            "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()
            self.Close()

def start_IDL(self):
    file_pp=open('post_process.txt','r')     
    if file_pp.read() == 'True':
        """ Simon Laptop """    
#        file_name = 'python_batch_processing.sav'
#        IDL=subprocess.Popen('C:\Program Files\IDL63\\bin\\bin.x86_64\\idlrt.exe -rt='+file_name)    
#        IDL.wait()
#        file_name = 'python_stitch_spectra.sav'
#        IDL=subprocess.Popen('C:\Program Files\IDL63\\bin\\bin.x86_64\\idlrt.exe -rt='+file_name)

        """ Braam Laptop """
#        file_name = 'python_batch_processing.sav'
#        self.message_txt.AppendText('Post Processing Integration>>> IDL>>> Batch Processing (This is done in parallel thread)>>>\n')        
#        IDL=subprocess.Popen('C:\RSI\IDL63\\bin\\bin.x86_64\\idlrt.exe -rt='+file_name)        
#        IDL.wait()
        
#        file_name = 'python_stitch_spectra.sav'
#        self.message_txt.AppendText('Post Processing Integration>>> IDL>>> Stitching...')
#        self.message_txt.AppendText('Please wait for IDL VM windows to close>>>')
#        IDL=subprocess.Popen('C:\RSI\IDL63\\bin\\bin.x86_64\\idlrt.exe -rt='+file_name)                

        """ New DELL """
#        IDL_Path = 'C:\\RFI Archive\\Source Code\\IDL Scripts\\'
#        file_name = IDL_Path+'python_batch_processing.sav'
        
        file_name = 'python_batch_processing.sav'
        self.message_txt.AppendText('Post Processing Integration>>> IDL>>> Batch Processing (This is done in parallel thread)>>>\n')
        print 'C:\Program Files\RSI\IDL63\\bin\\bin.x86_64\\idlrt.exe -rt='+file_name
        IDL=subprocess.Popen('C:\Program Files\RSI\IDL63\\bin\\bin.x86_64\\idlrt.exe -rt='+file_name)        
        IDL.wait()
            
#        file_name = IDL_Path+'python_stitch_spectra.sav'

#        file_name = 'python_stitch_spectra.sav'
#        self.message_txt.AppendText('Post Processing Integration>>> IDL>>> Stitching...\n')
#        self.message_txt.AppendText('Please wait for IDL VM windows to close>>>\n')
#        IDL=subprocess.Popen('C:\Program Files\RSI\IDL63\\bin\\bin.x86_64\\idlrt.exe -rt='+file_name)                

#    else:
#        self.message_txt.AppendText('Data Capture Complete>>>')
#        self.message_txt.AppendText('>>>')

    
def get_data(self):
    start(start_IDL, self)    
    self.statusbar.SetStatusText("DATA ACQUISITION IN PROGRESS>>>")        
    for n in range(0,np.int(self.num_steps)):        
        self.centre_freq=self.start+self.acq_bw/2
        wx.CallAfter(self.message_txt.AppendText,'Acquiring Data '+np.str(n+1)+' of '+np.str(np.int(self.num_steps))+'...\n')         
        print "Current <Start><Centre><Stop> Frequency: <",self.start/1e6,"MHz><", self.centre_freq/1e6,"MHz><", self.start/1e6+self.acq_bw/1e6,"MHz>"
        RSA_Control.GPIB_SetFreq(self.centre_freq, self.acq_bw, self.RSA)
        time.sleep(2)           
#         [self.freq, self.data] = RSA_Control.GPIB_Acquire(self.RSA, self.centre_freq, self.span, self.acq_length, np.int(self.start_number)+n, self.acq_bw, self.database_filename)
        RSA_Control.GPIB_Acquire(self.RSA, self.centre_freq, self.span, self.acq_length, np.int(self.start_number)+n, self.acq_bw, self.database_filename)                                                            
        wx.CallAfter(self.message_txt.AppendText,'Data acquired>>>\n')        
        self.start = self.centre_freq + self.acq_bw/2
#        self.message_txt.AppendText('Data ready to be displayed>>>\n')
#        self.message_txt.AppendText('>>>\n')        
        update_current(self, n+0.5, np.int(self.num_steps)+0.5)
        time.sleep(0.1)                
#    self.disp_data_btn.Enable()
    self.disp_data_btn.Disable()
    self.statusbar.SetStatusText("DATA ACQUISITION DONE>>>")
    update_current(self, 100.0, 100.0)
        
def update_current(self, n, total): # put your logic here      
    self.gauge_current.SetValue(np.float(n)/np.float(total)*100.0)
    time.sleep(0.1)    
                
def start(func, *args): # helper method to run a function in another thread
    thread = threading.Thread(target=func, args=args)
    thread.setDaemon(True)
    thread.start()
            
def main():  
    rsa = wx.App()
    RSA_GUI(None)
    rsa.MainLoop()    

if __name__ == '__main__':
    main()
