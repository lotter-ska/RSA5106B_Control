"""     AUTHOR: Braam Otto                         """
"""     ORGANISATION: MESA Solutions (Pty) Ltd.    """
"""     WEB: http://www.mesasolutions.co.za/       """
"""     CONTACT: braam@mesasolutions.co.za         """

import visa as vs
import numpy as np
import time

def GPIB_Init(resource_name):
    GPIB_Found = False
    RSA = None
    IDN_company = None
    IDN_model = None
    IDN_serial = None
    IDN_firmware = None
    RSA_OPT = None
    rm = vs.ResourceManager()
    for a in range(0,np.shape(rm.list_resources())[0]):
        print 'Searching for Instrument: ', resource_name
        print 'Found Instrument: ', rm.list_resources()[a], '\n'
        if rm.list_resources()[a] == resource_name:
            GPIB_Found = True
            RSA = vs.instrument(resource_name)
            del RSA.timeout    
            RSA_IDN = vs.instrument(resource_name).ask('*idn?')
            [IDN_company, IDN_model, IDN_serial, IDN_firmware]=RSA_IDN.split(',')
            RSA_OPT = vs.instrument(resource_name).ask('*opt?')
            RSA.write('*rst') # reset instrument to start from known state                            
    return GPIB_Found, RSA, IDN_company, IDN_model, IDN_serial, IDN_firmware, RSA_OPT

def GPIB_SetFreq(centre_freq, span, RSA):
#     busy=RSA.ask('*OPC?').encode('ascii','ignore')        
#     while busy.strip() != '1':    
# #     while RSA.ask('*OPC?') != '1':
#         time.sleep(1) # delays for 5 seconds
#         print 'FREQ SET SLEEPING...'
#     else:
#         print 'FREQ SET DELAY DONE'

#     RSA.timeout=3000

    RSA.write('abort') # stop acquisitions while measurement is configured
    RSA.ask('*OPC?')
        
    RSA.write('spectrum:frequency:center %e' % centre_freq)
    RSA.ask('*OPC?')
     
    RSA.write('spectrum:frequency:span %e' % span)
    RSA.ask('*OPC?')
    
#     while busy.strip() != '1':
#         time.sleep(1) # delays for 5 seconds
#         print 'FREQ SET SLEEPING...'
#     else:
#         print 'FREQ SET DELAY DONE'

#     RSA.timeout=3000

    RSA.write('CALCulate:MARKer1:DELete')
    RSA.write('calculate:marker1:add')
    RSA.write('calculate:spectrum:marker0:x %e' % centre_freq)       
    RSA.ask('*OPC?')

def GPIB_SetAcq(ref, att, acq_time, acq_bw, samples, RSA, preamp):
    print 'About to SET ACQ PARAMS...'
#     busy=RSA.ask('*OPC?').encode('ascii','ignore')
#     while busy.strip() != '1':
#         time.sleep(1) # delays for 5 seconds
#         print 'ACQ SET SLEEPING...'
#     else:
#         print 'ACQ SET DELAY DONE'
            
#     RSA.timeout=3000

#    RSA.write('SENSe:ACQuisition:MODE LENGth')
    RSA.write('SENSe:ACQuisition:MODE SAMPles')
    RSA.ask('*OPC?')
             
#     RSA.timeout=3000
    
    RSA.write('SENSe:ANALysis:LENGth:AUTO 0')
    RSA.ask('*OPC?')
    
#     RSA.timeout=3000
    print 'AUTO OFF...'
    print 'ACQ BW SET TO ', acq_bw    
    RSA.write('SENSE:ACQUISITION:BANDWIDTH %i' %acq_bw)
    RSA.ask('*OPC?')
    
#     RSA.timeout=3000
#    print 'ACQ BW 20MHz...'
    
    print 'SENSe:ACQUISITION:SAMPLES %i' %samples
    RSA.write('SENSe:ACQUISITION:SAMPLES %i' %samples)
    RSA.ask('*OPC?')
            
    RSA.write('SENSe:ANALysis:LENGth %i s' %acq_time)
    RSA.ask('*OPC?')
    
#     RSA.timeout=3000    
#    print 'ACQ ANALYSIS LENGTH/NUMBER of SAMPLES...'
#    print RSA.ask('SENSE:ANALYSIS:LENGTH:ACTUAL?')

#    RSA.write('SENSe:ANALysis:LENGth 3E+9ns')
#    RSA.timeout=500    
#    print RSA.ask('SENSE:ANALYSIS:LENGTH:ACTUAL?')    
#    RSA.write('TRACE1:SPECTRUM:COUNT 1')
#    RSA.timeout=500        
    RSA.write('INP:ATT:AUTO OFF')
    RSA.ask('*OPC?')
    
#     RSA.timeout=3000

    RSA.write('INP:ATT:MON:STAT OFF')
    RSA.ask('*OPC?')
    
#     RSA.timeout = 3000
#     while busy.strip() != '1':
#         time.sleep(1) # delays for 5 seconds
#         print 'ACQ SET SLEEPING...'
#     else:
#         print 'ACQ SET DELAY DONE'
     
#     RSA.timeout=3000
    
    RSA.write('INP:ATT %i' %np.int(att))
    RSA.ask('*OPC?')
                    
#    RSA.write('SENSE:ANALYSIS:LENGTH %e' %np.int(acq_time) + 's')        
#     RSA.timeout=3000
#    print preamp

    if preamp==True:
        print "PRE-AMPLIFIER SELECTED>>>"
        RSA.write('INPUT:RF:GAIN:STATE ON')
        RSA.ask('*OPC?')
    else:
        print "PRE-AMPLIFIER NOT SELECTED>>>"
        RSA.write('INPUT:RF:GAIN:STATE OFF')
        RSA.ask('*OPC?')
    
#     RSA.timeout=3000
    print "SETTING REFERENCE LEVEL>>>"
    RSA.write('INPUT:RLEVEL %i' %np.int(ref))
    RSA.ask('*OPC?')
    
#     RSA.timeout=3000
#     RSA.write('INITiate:IMMediate')
#     RSA.ask('*OPC?')
    
#     RSA.timeout=3000

    RSA.write('SENSe:USETtings')
    RSA.ask('*OPC?')
    
#     RSA.timeout=3000                   

def GPIB_Acquire(RSA, centre_freq, span, acq_time, total_count, acq_bw, base_filename):

    RSA.write('initiate:CONtinuous OFF') # start acquisitions
    print "Single Mode"
    RSA.ask('*OPC?')
    
#     busy=RSA.ask('*OPC?').encode('ascii','ignore')
#     print busy
#     raw_input("prompt")
#     while busy.strip() != '1':
#         time.sleep(1) # delays for 5 seconds
#         print 'ACQ SLEEPING...'
#     else:
#         print 'ACQ DELAY DONE'
        
#     RSA.write('FETCh:SPECtrum:TRACe1?')
#     RSA.ask('*OPC?')
# #     time.sleep(1) 
# # #     RSA.timout=500           
#     RSA.read_raw()
#     RSA.ask('*OPC?')
    
#     data = RSA.read_values(vs.single)        
#     time.sleep(1)
    
#     while busy.strip() != '1':
#         time.sleep(1) # delays for 5 seconds
#         print 'TRACE SLEEPING...'
#     else:
#         print 'TRACE DELAY DONE'
    
#     time.sleep(1)
        
#     while busy.strip() != '1': # query to check if acquisitions started
#         time.sleep(1)
#         print 'Acquisition Started...'
#     else:
#         print 'Error: Acquisition NOT started...'
    
    RSA.write('INITiate:IMMediate')
    print "Initiate Immediate"
    RSA.ask('*OPC?')
    
#     time.sleep(1)
#     while busy.strip() != '1':
#         time.sleep(1) # delays for 5 seconds
#         print 'Initiating...'
#     else:
#         print 'Initiating DONE'
        
        
#     RSA.write('[SENSe]:IQVTime:CLEar:RESults')
#     print "Clear Results"
#     RSA.ask('*OPC?')
    
    
#     time.sleep(1)
#     while busy.strip() != '1':
#         time.sleep(1) # delays for 5 seconds
#         print 'Clear Results...'
#     else:
#         print 'Clear Results DONE'
#     RSA.timeout=500
#     time.sleep(1)
    
    RSA.write('FETCh:IQVTime:RESult?')
    print "Retrieve IQ Data"
    RSA.ask('*OPC?')
    
#     while busy.strip() != '1':
#         time.sleep(1) # delays for 5 seconds
#         print 'Fetch Results...'
#     else:
#         print 'Fetch Results DONE'
#     time.sleep(1)
    
#     while busy.strip() != '1':
#         time.sleep(1) # delays for 5 seconds
#         print 'TRACE SLEEPING...'
#     else:
#         print 'TRACE DELAY DONE'
        
    RSA.write('MMEMORY:STORE:IQ "Z:\\'+base_filename+np.str(total_count)+'.tiq"')
    print "Store Data to Disk"
    RSA.ask('*OPC?')
    
#     RSA.write('MMEMORY:STORE:IQ "C:\\'+base_filename+np.str(total_count)+'.tiq"')    
    
#     while busy.strip() != '1':
#         time.sleep(1) # delays for 5 seconds
#         print 'IQ FILE TRANSFER SLEEPING...'
#     else:
#         print 'IQ FILE TRANSFER DELAY DONE'
         
#    RSA.write('MMEMory:STORe:IQ:CSV "Processed_Data'+np.str(total_count)+'.csv"')    
#    print centre_freq
#    
#    while busy.strip() != '1':
#        time.sleep(0.5) # delays for 5 seconds
#        print 'PROCESSED FILE TRANSFER SLEEPING...'
#    else:
#        print 'PROCESSED FILE TRANSFER DELAY DONE'
    
#     freq=np.linspace(centre_freq-acq_bw/2,centre_freq+acq_bw/2,len(data))
    
#    GPIB_Display(freq, data)
    
#     return freq, data        

def GPIB_Display(freq, data):
    print "Available in Next Version..."
#    plt.figure(figsize=(17,12))
#    plt.plot(freq/1e6, data,'k')
#    max_freq=np.array(freq)[data==np.max(data)][0]
#    max_ampl=np.max(data)
#    plt.text(max_freq/1e6, max_ampl+0.5, np.str(max_freq/1e6)+ ' MHz    ' + np.str(np.round(max_ampl,2)) + ' dBuV/m',rotation=90, horizontalalignment='center', verticalalignment='bottom', fontsize=12) 
#    plt.grid(True)
#    plt.title('RSA 5106A Data Capture',fontsize=24)
#    plt.ylabel('Power [dBm]')
#    plt.xlabel('Frequency [MHz]')
#    plt.axis([freq[0]/1e6, freq[-1]/1e6, np.min(data), 0])
#    plt.show()        
