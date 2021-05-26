# driftingGratings3 for visual stimulation
#-----------------------------------------------------------------------------
# stimuli are defined in a csv that needs to be specified in the code here below
# every stimulus condition is repeated for a number of times specified in the 
# variable "iteration" that can be changed here below. Trials are presented in a
# pseudorandom way (every stimulus is presented in a randomized order before 
# skipping to the next iteration).
#
# -NO TCP COMMUNICATION IS USED
# -For every stimulus, a corresponding code specified in the CSV file is sent to
#     the parallel port
# -Trials are divided in pre-stimulus and stimulus 

#-------------------------------------------------------------
#--- USER PARAMETERS ----- YOU CAN CHANGE THEM ---------------
#-------------------------------------------------------------

iterations = 15 # Number of trials per stimulus condition

oriOffset = 0 # (NOT FULLY TESTED!) Orientation offset to compensate for headbar angle. 
              # Angles are added CLOCKWISE as seen on the monitor

conditionsFile = r'C:\\Users\\2FOTNEW\\Documents\\stimulationProtocols\\DSG_fasting_SF-TF_short.csv' # fullpath to the CVS stimulus file

# Pupillometry parameters
blackFrames = 3600
blackCode = 2
grayFrames = 1800
whiteFrames = 1200
whiteCode = 3

#-------------------------------------------------------------
#--- DO NOT EDIT PAST THIS POINT -----------------------------
#-------------------------------------------------------------


from psychopy import core, visual, event, parallel, data
import pandas
import json
import random, socket, select
import time

cond = data.importConditions(conditionsFile)

#Define window, backgroud and grating objects 
stimWin = visual.Window([1920,1080],
            screen = 1,
            fullscr = True,
            monitor="stimMonitor",
            units="deg")
 
grating = visual.GratingStim(stimWin, 
            pos=[0,0],
            size=[60,60],
            tex='sin',
            mask= 'raisedCos',
            maskParams={'fringeWidth': 0.2},
            #maskParams={'sd':10},
            sf=[0.5],
            ori=0,
            phase=0,
            contrast=0.9,
            colorSpace = 'rgb',
            color=[1,1,1],
            autoDraw = False)

background = visual.ShapeStim(stimWin,
            pos=[0,0],
            units='norm',
            vertices=((1,1),(-1,1),(-1,-1),(1,-1)),
            closeShape= True,
            lineWidth=0,
            fillColor=[0,0,0],
            fillColorSpace='rgb',
            autoDraw = False)

#make the mouse invisible
event.Mouse(visible=False)

#Open communication with the parallel port
pPort = parallel.ParallelPort(address=0xd100)
pPort.setData(int('00000000',2))
print('Parallel port initialized')

#Measure the actual framerate of the screen
print('Measuring actual monitor framerate...', end='')
frameRate = stimWin.getActualFrameRate(nIdentical=50, nMaxFrames=1000, nWarmUpFrames=50, threshold=1)
if frameRate == None:
    print(' Unable to measure a consistent framerate for this monitor.')
    quit()
else:
    print(' Measured framerate: {}'.format(frameRate))

#Initialize the main trial handler
trialsHand = data.TrialHandler(cond,iterations,method='random')

time.sleep(10) # Time for the mouse to adapt to new mean luminosity

pPort.setData(int('10000000',2)) # trigger start of acquisition

print('2P acquisition started! Start the eye camera recording before...')
for i in range(10,0,-1):
    print(i)
    time.sleep(1)

print('***START OF PUPILLOMETRY***')
#Black for pupillometry
print('Now presenting: BLACK')
background.fillColor = [-1.0, -1.0, -1.0]
pPort.setData(blackCode)
for i in range(blackFrames):
    background.draw()
    stimWin.flip()
#Gray for pupillometry
print('Now presenting: GRAY')
background.fillColor = [0, 0, 0]   
pPort.setData(1)
for i in range(grayFrames):
    background.draw()
    stimWin.flip()
#White for pupillometry
print('Now presenting: WHITE')
background.fillColor = [1.0, 1.0, 1.0]
pPort.setData(whiteCode)
for i in range(whiteFrames):
    background.draw()
    stimWin.flip()
#Gray for pupillometry
print('Now presenting: GRAY')
background.fillColor = [0, 0, 0]
pPort.setData(1)
for i in range(grayFrames):
    background.draw()
    stimWin.flip()
#End of pupillometry
pPort.setData(0)
time.sleep(1)

#------------------------------------------------------------------------
#--- STIMULATION LOOP
#------------------------------------------------------------------------
print('***START OF STIMULATION LOOP***')

for thisTrial in trialsHand:  
    # Break the stimulation loop if the experimenter presses "q" or "esc"
    if len(event.getKeys(keyList=('escape','q'))) > 0:
        event.clearEvents('keyboard')
        stimWin.close()
        pPort.setData(0)
        break
        
    # PRE-STIMULUS  
    pPort.setData(1)   
    for frameN in range(thisTrial['preStimulusFrames']):
        background.draw()
        stimWin.flip()
    #pPort.setData(0)
        
    # Update stimulus parameters with the current trial
    grating.sf = thisTrial['spatialFreq']
    grating.ori = thisTrial['orientation'] + oriOffset
    temporalFreq = thisTrial['temporalFreq']
    code = thisTrial['code']

    print('Curr Stim(%i/%i): sf:%g\tori:%g\ttf:%g\tcode:%g' %(trialsHand.thisN,trialsHand.nTotal,thisTrial['spatialFreq'],thisTrial['orientation'],temporalFreq,code))
    
    # STIMULUS
    pPort.setData(int(code))        #Send code for the stimulation
    for frameN in range(thisTrial['stimulusFrames']):
        grating.setPhase(1/float(frameRate)*temporalFreq, '+')
        grating.draw()
        stimWin.flip()
    #pPort.setData(0)
    
pPort.setData(0)    
print('Overall, %i frames were dropped.' % stimWin.nDroppedFrames)    
stimWin.close()