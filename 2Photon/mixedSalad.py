from psychopy import core, visual, event
from scipy import signal
import numpy as np

#-----------------------------------------------------------------------
#--- USER PARAMETERS ---------------------------------------------------
#-----------------------------------------------------------------------

latencyToDropFrames = 2         # ms. max delay allowed before warning for dropped frames
monitorFramerate = 60.0         # Has to be a float
relativeOrientation = 45        # Difference in gratings orientation to create the plaid
temporalFreq = 3                # Hz. Cycles per second (changes in phase)
circularFreq = 0.015            # Rotations per second (changes in orientation)
SF = (0.05, 0.3)                # (min, max) spatial frequencies range to display
sfChangeFreq = 0.15             # Hz. Cycles of spatial frequencies per second (Triangle function)
contrastFreq = 0.09             # Hz. Cycles of contrast per second. (Sine function) NOTE! the stimulus 
                                # is visible at contrast 1 and -1 so the apparent frequency of modulation 
                                # is double of the selected frequency
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------

# Initialize stim window and 2 gratings

stimWin = visual.Window([1920,1080],
            screen = 0,
            color = [0,0,0],
            allowGUI = False,
            fullscr = True,
            monitor="testMonitor",
            units="deg")

grating1 = visual.GratingStim(stimWin, 
            pos=[0,0],
            size=[200,200],
            tex='sin',
            mask=None,
            #maskParams={'fringeWidth': 1},
            #maskParams={'sd':10},
            sf=[1],
            ori=0,
            phase=0,
            opacity = 1,
            contrast=0.9,
            colorSpace = 'rgb',
            color=[1,1,1],
            autoDraw = True)
 
grating2 = visual.GratingStim(stimWin, 
            pos=[0,0],
            size=[200,200],
            tex='sin',
            mask=None,
            #maskParams={'fringeWidth': 1},
            #maskParams={'sd':10},
            sf=[1],
            ori=relativeOrientation,
            phase=0,
            opacity = 0.5,
            contrast=0.9,
            colorSpace = 'rgb',
            color=[1,1,1],
            autoDraw = True)

# calculations for ori
oriIncrement = 360/monitorFramerate * circularFreq

# calculations for SF
l = [i for i in np.arange(0, np.pi*2 , 2 * np.pi / monitorFramerate * sfChangeFreq)]
sawtooth = signal.sawtooth(l, width=0.5)
indSF = 0

# calculations for contrast
l = [i for i in np.arange(0, np.pi*2 , 2 * np.pi / monitorFramerate * contrastFreq)]
contrastSineWave = np.sin(l)*0.9
indContrast = 0

# make the mouse invisible
event.Mouse(visible=False)

# Detect and count dropped frames
stimWin.recordFrameIntervals = True
stimWin.refreshThreshold  = (1/monitorFramerate) + latencyToDropFrames


#-----------------------------------------------------------------------
#--- MAIN STIMULATON LOOP
#-----------------------------------------------------------------------

while True:  
    
    # Break the stimulation loop if the experimenter presses "q" or "esc"
    if len(event.getKeys(keyList=('escape','q'))) > 0:
        event.clearEvents('keyboard')
        break
    
    # Change orientation
    grating1.ori = (grating1.ori + oriIncrement) % 360
    grating2.ori = (grating2.ori + oriIncrement) % 360
    
    # Change phase
    grating1.setPhase(1/monitorFramerate*temporalFreq, '+')
    grating2.setPhase(1/monitorFramerate*temporalFreq, '+')
    
    # Change spatial frequency
    newSF = np.interp(sawtooth[indSF],[-1,1],[SF[0],SF[1]])
    grating1.sf = newSF
    grating2.sf = newSF
   
    indSF = (indSF+1) % len(sawtooth)
    
    # Change the contrast
    grating1.contrast = contrastSineWave[indContrast]
    grating2.contrast = contrastSineWave[indContrast]
    
    indContrast = (indContrast+1) % len(contrastSineWave)
    
    # Update the stimulus on screen
    stimWin.flip()
    

print('Overall, %i frames were dropped.' % stimWin.nDroppedFrames)
stimWin.close()