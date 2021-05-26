from psychopy import visual, event, parallel
import itertools
import random

#-------------------------------------------------------------------------------
# USER PARAMETERS
#-------------------------------------------------------------------------------

# STIMULATION
#------------------
grayDuration = 1            # Duration (seconds) of the gray
gratingDuration = 1         # Duration (seconds) of the grating
gratingTexture = 'sin'      # Texture ('sin' or 'sqr') 
gratingSize = [60,60]       # Size (degs) of the grating patch

spFreqs = [0.05]            # (list) Spatial Freqs that will be used for gratings
oris = [0, 45, 90, 135]     # (list) Orientations that will be used for gratings

# EXPERIMENTAL SETUP
#------------------
screenNumber = 0            # Screen number as detected by psychopy
windowSize = [1920,1080]    # Dimensions (pixels) of the stimulation window

# COMMUNICATION
#------------------
useParallel = False         # (True, False) Sends a TTL signal to pin 1 of the parallel port during stimulation
parallAddress = 0xd100      # Address of the parallel port (if useParallel==True)


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------


# Define window, backgroud and grating objects 
stimWin = visual.Window(windowSize,
            screen = screenNumber,
            fullscr = True,
            monitor="testMonitor",
            units="deg")

grating = visual.GratingStim(stimWin, 
            pos=[0,0],
            size=gratingSize,
            tex=gratingTexture,
            mask='raisedCos',
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

# Make the mouse invisible
event.Mouse(visible=False)

if useParallel:
    # Open communication with the parallel port
    pPort = parallel.ParallelPort(address=parallAddress)
    pPort.setData(int('00000000',2))
    print('Parallel port initialized')

# Measure the actual framerate of the screen
print('Measuring actual monitor framerate...'),
frameRate = stimWin.getActualFrameRate(nIdentical=50, nMaxFrames=1000, nWarmUpFrames=50, threshold=1)
if frameRate == None:
    print(' Unable to measure a consistent framerate for this monitor.')
    quit()
else:
    print(' Measured framerate: %f' %(frameRate))


#----------------------------------------------
# DEFINING THE STIMULI
#----------------------------------------------
preStimFrames = int(round(grayDuration*frameRate))
stimFrames = int(round(gratingDuration*frameRate))

# Create a list of stimuli from which to sample randomly
stimuli = list(itertools.product(spFreqs,oris))

#----------------------------------------------
# MAIN LOOP
#----------------------------------------------
keepGoing = True

while keepGoing:
    # Break the stimulation loop if the experimenter presses "q" or "esc"
    if len(event.getKeys(keyList=('escape','q'))) > 0:
        event.clearEvents('keyboard')
        stimWin.close()
        keepGoing = False
        break
        
    # PRE-STIMULUS  
    if useParallel:
        pPort.setData(int('00000001',2))
    for frameN in range(preStimFrames):
        background.draw()
        stimWin.flip()
    
    # Pick a random stimulus from the stimuli list
    thisStimulus = random.choice(stimuli)
    # Update stimulus parameters with the current trial
    grating.sf = thisStimulus[0]
    grating.ori = thisStimulus[1]
    grating.setPhase(random.random())
    
    # STIMULUS
    if useParallel:
        pPort.setData(int('10000010',2))
    for frameN in range(stimFrames):
        grating.draw()
        stimWin.flip()

stimWin.close()