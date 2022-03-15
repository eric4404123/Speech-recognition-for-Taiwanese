import math
import numpy as np

# method 1: absSum
def calVolume(waveData, frameSize, overLap, difftimes):
    for i in range(difftimes):
        waveData = np.diff(waveData)
    wlen = len(waveData)
    #print(wlen)
    step = frameSize - overLap
    frameNum = int(math.ceil(wlen*1.0/step))
    #print(frameNum)
    volume = np.zeros((frameNum,1))
    for i in range(frameNum):
        curFrame = waveData[np.arange(i*step,min(i*step+frameSize,wlen))]
        curFrame = curFrame - np.median(curFrame) # zero-justified
        volume[i] = np.sum(np.abs(curFrame))
    #print(len(volume))
    return volume

# method 2: 10 times log10 of square sum
def calVolumeDB(waveData, frameSize, overLap, difftimes):
    wlen = len(waveData)
    for i in range(difftimes):
        waveData = np.diff(waveData)
    step = frameSize - overLap
    frameNum = int(math.ceil(wlen*1.0/step))
    wlen = len(waveData)
    volume = np.zeros((frameNum,1))
    for i in range(frameNum):
        if i*step>=wlen :
            curFrame = 0
        else:
            curFrame = waveData[np.arange(i*step,min(i*step+frameSize,wlen))]
            curFrame = curFrame - np.mean(curFrame) # zero-justified
        n = np.sum(curFrame*curFrame)
        if n==0 :
            volume[i] = 0
        else:
            volume[i] = 10*np.log10(n)

    return volume