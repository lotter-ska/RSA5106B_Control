"""     AUTHOR: Braam Otto                         """
"""     ORGANISATION: MESA Solutions (Pty) Ltd.    """
"""     WEB: http://www.mesasolutions.co.za/       """
"""     CONTACT: braam@mesasolutions.co.za         """

import numpy as np
import wx
import os

class Params_GUI(wx.Frame):
    
    def __init__(self, *args, **kwargs):
        super(Params_GUI, self).__init__(*args, **kwargs)
        self.Bind(wx.EVT_CLOSE, self.OnClose)        
        self.InitUI()

    def InitUI(self):
        print 'Initialising Parameters Setup...'
        W=800
        H=300                        
        #self.path = 'F:\\RSA5106A_Data\\'
	
        parameters_filename=open('python_parameters.txt','r')
        try:        
            for line in parameters_filename:                                                  
                if line.find('DataFilename_base')==0:
                    start=line.find('\'')+1
                    stop=line[start:].find('\'')                    
                    self.database_filename=line[start:start+stop] 
                                          
#                    index = 0
#                    index_list = []
#                    while index < len(self.database_filename):                        
#                        index = self.database_filename.find('_', index)
#                        index_list.append(index)
#                        if index == -1:
#                            break
#                        print '_ found at', index
#                        index += 1
#                                        
#                    self.file_start_number=0                                         
#                    if len(index_list) > 2:                                                                                                                                
#                        try:                                                                                
#                            self.file_start_number = np.int(self.database_filename[index_list[-2]+1:])                                                        
#                            print "FILE START NUMBER:", np.int(self.database_filename[index_list[-2]+1:])
#                        except ValueError:
#                            print "Value Error"
#                            print "FILE START NUMBER:", 1
#                            self.file_start_number = 1 
#                            self.database_filename = self.database_filename + '_1'                                                                                        
#                    else:
#                        try:                                                                                
#                            self.file_start_number = np.int(self.database_filename[index_list[0]+1:])                                                        
#                            print "FILE START NUMBER:", np.int(self.database_filename[index_list[0]+1:])
#                        except ValueError:                        
#                            print "FILE START NUMBER:", 1 
#                            self.file_start_number = 1
#                            self.database_filename = self.database_filename + '_1'
                                         
                if line.find('subtitle')==0:
                    start=line.find('\'')+1
                    stop=line[start:].find('\'')
                    plot_title=line[start:start+stop]
                if line.find('polarisation')==0:
                    start=line.find('=')+1
                    stop=line[start:].find(';')-1
                    polarisation = line[start:start+stop].strip()
                if line.find('chamber_type')==0:
                    start=line.find('=')+1
                    stop=line[start:].find(';')-1
                    chamber_type = line[start:start+stop].strip()
                if line.find('AntGainFilenameNumber')==0:
                    start=line.find('=')+1
                    stop=-1
                    antenna_type = line[start:stop].strip()
                if line.find('LnaGainFilenameNumber')==0:
                    start=line.find('=')+1
                    stop=-1
                    LNA_type = line[start:stop].strip()
                if line.find('CableLossFilenameNumber')==0:
                    start=line.find('=')+1
                    stop=-1
                    cableloss_type = line[start:stop].strip()                                                
        finally:
            parameters_filename.close()
    
        panel_top = wx.Panel(self)
        wx.StaticText(panel_top, -1, 'Data Base File Name:', (0.05*W, 0.05*H))
        self.file_name_txt= wx.TextCtrl(panel_top, -1, size=(175, 20), pos=(0.215*W, 0.05*H))
        self.file_name_txt.SetValue(self.database_filename)        
        
        wx.StaticText(panel_top, -1, 'File Start Number:', (0.05*W, 0.15*H))
        self.start_number_txt= wx.TextCtrl(panel_top, -1, size=(175, 20), pos=(0.215*W, 0.15*H))
        self.start_number_txt.SetValue('1')
        
        wx.StaticText(panel_top, -1, 'Data Plot Title:', (0.05*W, 0.25*H))
        self.title_txt= wx.TextCtrl(panel_top, -1, size=(175, 20), pos=(0.215*W, 0.25*H))
        self.title_txt.SetValue(plot_title)
        
        self.post_pro = wx.CheckBox(panel_top, -1, '  Post Process Captured Data using IDL', (0.05*W, 0.675*H))
        self.post_pro.SetValue(False)
        
        wx.StaticText(panel_top, -1, 'Antenna Type:', (0.5*W, 0.05*H))
#        self.antenna=['GLPDA', 'KLPDA 1', 'KLPDA 3', 'EMCO 3115 (Small Horn)', 'EMCO 3106-B (Large Horn)', 'EMCO 3141 (BiConLog)', 'None']
        
        antenna_file = open('hardware_antenna.txt','r')
        self.antenna=[]
        for line in antenna_file:
            if line != "No_Antenna":
                tmp = line[line.find('_')+1:]
                self.antenna.append(tmp[tmp.find('_')+1:])
            else:
                self.antenna.append("No Antenna")
        antenna_file.close()
               
        self.antenna_cb=wx.ComboBox(panel_top, -1, value=self.antenna[np.int(antenna_type)-1], pos=(0.7*W, 0.045*H), size=(180, -1), choices=self.antenna, style=wx.CB_READONLY)
        
        wx.StaticText(panel_top, -1, 'Antenna Polarisation:', (0.5*W, 0.15*H))
        self.pol=['Vertical','Horizontal']
        self.pol_cb=wx.ComboBox(panel_top, -1, value=self.pol[np.int(polarisation)], pos=(0.7*W, 0.145*H), size=(180, -1), choices=self.pol, style=wx.CB_READONLY)
        
        wx.StaticText(panel_top, -1, 'LNA Gain File:', (0.5*W, 0.35*H))
#        self.lna=['LNA 1', 'LNA 2', 'LNA 1+2', 'None']

        lna_file = open('hardware_lna.txt','r')
        self.lna=[]
        for line in lna_file:            
            self.lna.append(line)
        lna_file.close()
            
        self.lna_cb=wx.ComboBox(panel_top, -1, value=self.lna[np.int(LNA_type)-1], pos=(0.7*W, 0.3375*H), size=(180, -1), choices=self.lna, style=wx.CB_READONLY)
        
        wx.StaticText(panel_top, -1, 'Rx Cable Loss:', (0.5*W, 0.25*H))
#        self.cable=['Houwteq 1a', 'Houwteq 1b', 'Houwteq 1c', 'Houwteq 1a_1b', 'Houwteq 2a', 'Houwteq 2b', 'Houwteq 2c', 'Houwteq 2a_2b_2c',
#                    'Houwteq 3a', 'Houwteq 3b', 'Houwteq 3c', 'Houwteq 3a_3b_3c', 'Houwteq 4a', 'Houwteq 4b',
#                    'Pinelands 5a_5b', 'Pinelands 6a_6b', 'Pinelands 6a_6b_6c', 'Pinelands 7a', 'None']

        cable_file = open('hardware_cable.txt','r')
        self.cable=[]
        for line in cable_file:            
            if line != "No_Cable":
                tmp = line[line.find('_')+1:]
                self.cable.append(tmp)
            else:
                self.cable.append("No Cable")
        cable_file.close()
        
        self.cable_cb=wx.ComboBox(panel_top, -1, value=self.cable[np.int(cableloss_type)-1], pos=(0.7*W, 0.2375*H), size=(180, -1), choices=self.cable, style=wx.CB_READONLY)
        
        wx.StaticText(panel_top, -1, 'Chamber Type:', (0.5*W, 0.45*H))
        self.chamber=['Anechoic Chamber', 'Reverb Chamber']
        self.chamber_cb=wx.ComboBox(panel_top, -1, value=self.chamber[np.int(chamber_type)], pos=(0.7*W, 0.4375*H), size=(180, -1), choices=self.chamber, style=wx.CB_READONLY)
        
        self.freq_setup_btn = wx.Button(panel_top, 4, 'Parameter Setup', pos=(0.5*W, 0.65*H))
        self.Bind(wx.EVT_BUTTON, self.ParamSetup, id=4)
        
        self.SetSize((W, H))
        self.SetTitle('PARAMETER SETUP: (RSA5106B Automated Control Software - Ver 0.5.1)')
        self.Centre()
        self.Show(True)        
        
    def ParamSetup(self,event):
        confirm=True
        if self.file_name_txt.GetValue() == self.database_filename:
            confirm=False
            dlg = wx.MessageDialog(self,
            "The chosen data base file name was already used. Overwrite?",
            "Overwrite Data", wx.OK|wx.CANCEL|wx.ICON_WARNING)
            result = dlg.ShowModal()
            
            dlg.Destroy()
            if result == wx.ID_OK:
                confirm=True
                                                
        if confirm==True:
            
            file_read=open('python_parameters.txt','r')            
            file_write=open('python_parameters_tmp.txt','w')                        
            
            file_pp=open('post_process.txt','w')            
            try:
                if self.post_pro.IsChecked() == True:
                    file_pp.write('True')
                else:
                    file_pp.write('False')                                
            finally:
                file_pp.close()
            
            self.database_filename= self.file_name_txt.GetValue()
            if self.database_filename[-1]=='_':
                print "File Format Correct"
            else:
                print "File Format Appended"
                self.database_filename = self.database_filename + '_'
                
#            index = 0
#            index_list = []
#            while index < len(self.database_filename):                        
#                index = self.database_filename.find('_', index)
#                index_list.append(index)
#                if index == -1:
#                    break
#                print '_ found at', index
#                index += 1
#                        
#            self.file_start_number=0                                         
#            if len(index_list) > 2:                                                                                                                                            
#                try:                                                                                
#                    self.file_start_number = np.int(self.database_filename[index_list[-2]+1:])                                                        
#                    print "FILE START NUMBER:", np.int(self.database_filename[index_list[-2]+1:])
#                except ValueError:
#                    print "Value Error"
#                    print "FILE START NUMBER:", 1
#                    self.file_start_number = 1 
#                    self.database_filename = self.database_filename + '_1'                                                                                        
#            else:                
#                try:                                                                                
#                    self.file_start_number = np.int(self.database_filename[index_list[0]+1:])                                                        
#                    print "FILE START NUMBER:", np.int(self.database_filename[index_list[0]+1:])
#                except ValueError:                        
#                    print "FILE START NUMBER:", 1 
#                    self.file_start_number = 1
#                    self.database_filename = self.database_filename + '_1'
                            
            file_start=open('file_start.txt','w')
            file_start.write(self.start_number_txt.GetValue())
#            file_start.write(np.str(self.file_start_number))
            file_start.close()
            
            try:
                for line in file_read:
                    if line.find('DataFilename_base')==0:
                        stop=line.find('\'')+1
                        file_write.write(line[0:stop]+self.database_filename+'\'\n')
                    elif line.find('subtitle')==0:
                        stop=line.find('\'')+1
                        file_write.write(line[0:stop]+self.title_txt.GetValue()+'\'\t\t ;Description of measurement\'\n')
                    elif line.find('polarisation')==0:
                        stop=line.find('=')+1                    
                        file_write.write(line[0:stop]+' '+np.str(self.pol_cb.GetSelection())+' \t\t\t\t\t\t\t ;0=V polarisation, 1=H polarisation\n')                        
                    elif line.find('chamber_type')==0:
                        stop=line.find('=')+1
                        file_write.write(line[0:stop]+' '+np.str(self.chamber_cb.GetSelection())+' \t\t\t\t\t\t\t ;0=Anechoic Chamber, 1=Reverb Chamber\n')                        
                    elif line.find('AntGainFilenameNumber')==0:
                        stop=line.find('=')+1                    
                        file_write.write(line[0:stop]+' '+np.str(self.antenna_cb.GetSelection()+1)+'\n')
                    elif line.find('LnaGainFilenameNumber')==0:
                        stop=line.find('=')+1
                        file_write.write(line[0:stop]+' '+np.str(self.lna_cb.GetSelection()+1)+'\n')
                    elif line.find('CableLossFilenameNumber')==0:
                        stop=line.find('=')+1
                        file_write.write(line[0:stop]+' '+np.str(self.cable_cb.GetSelection()+1)+'\n')
                    else:
                        file_write.write(line)
            finally:
                file_write.close()
                file_read.close()
                os.remove('python_parameters.txt')
                os.rename('python_parameters_tmp.txt', 'python_parameters.txt')                
                self.Destroy()
                self.Close()
                
    def OnClose(self, event):        
        print "Paramters Saved to File..."
                 
        file_read=open('python_parameters.txt','r')
        try:
            for line in file_read:
                if line.find('AntGainFilenameNumber')==0:
                    start=line.find('=')+1
                    stop=-1
                    antenna_type = line[start:stop].strip()
                if line.find('LnaGainFilenameNumber')==0:
                    start=line.find('=')+1
                    stop=-1
                    LNA_type = line[start:stop].strip()
                if line.find('CableLossFilenameNumber')==0:
                    start=line.find('=')+1
                    stop=-1
                    cableloss_type = line[start:stop].strip()
        finally:
            file_read.close()
        
            print 'Antenna Type: ', antenna_type
            print 'LNA Type: ', LNA_type
            print 'Cable Loss: ', cableloss_type
            self.Destroy()
                                                  
def main():  
    params = wx.App()
    Params_GUI(None)
    params.MainLoop()    

if __name__ == '__main__':
    main()
