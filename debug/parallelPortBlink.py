from psychopy import event, parallel
import time

#-------------------------------------------------------------------------------
# USER PARAMETERS
#-------------------------------------------------------------------------------

parallAddress = 0xd100      # Address of the parallel port (if useParallel==True)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------


# Open communication with the parallel port
pPort = parallel.ParallelPort(address=parallAddress)
pPort.setData(int('00000000',2))
print('Parallel port initialized')

while True:
    if len(event.getKeys(keyList=('escape','q'))) > 0:
        event.clearEvents('keyboard')
        pPort.setData(int('00000000',2))
        print('Execution stopped by the user.')
        quit()
    pPort.setData(int('00001000',2))
    time.sleep(1)
    pPort.setData(int('00000000',2))
    time.sleep(1)
