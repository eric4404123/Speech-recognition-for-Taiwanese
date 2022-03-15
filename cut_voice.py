import wave
import numpy as np
#import matplotlib.pyplot as plt
import Volume as vp
#from sympy import limit, Symbol, sin, oo, diff
from pydub import AudioSegment
from pydub.utils import make_chunks
from label_wav_dir import label_wav

from os import walk,mkdir,remove
from os.path import join
from os import listdir
from os.path import isfile, isdir, join
import os

def longwav_recog(wav):
    thiswav = wav

    # 指定要列出所有檔案的目錄
    mypath = "documents"

    f = mypath + "/" + thiswav
    if f.split(".")[-1] == "wav":
        sound = AudioSegment.from_wav(f)
        sound = sound.set_frame_rate(16000)
        output_path="16KWav/"
        if not isdir(output_path):
            mkdir(output_path)#做一個資料夾
            """
        filePath=join(output_path, root.split("\\")[-1])
        if not isdir(filePath):
            mkdir(filePath)
            """
        sound.export(join(output_path,thiswav), format="wav")
    thiswav_16K = "16KWav/" + thiswav

    def findIndex(vol,thres):
        l = len(vol)
        index = []
        for i in range(l-1):
            if((vol[i]-thres)*(vol[i+1]-thres)<0):
                index.append(i)
        return index

    fw = wave.open(thiswav_16K,'r')
    params = fw.getparams()
    nchannels, sampwidth, framerate, nframes = params[:4]
    print(params)
    #只能用單聲道
    strData = fw.readframes(nframes)
    waveData = np.fromstring(strData, dtype=np.int16)
    waveData = waveData*1.0/max(abs(waveData))
    fw.close()

    frameSize = 256
    overLap = 128

    vol = vp.calVolumeDB(waveData, frameSize, overLap, 0)

    #對waveData微分 計算vol
    vol_diff4 = vp.calVolumeDB(waveData, frameSize, overLap, 4)
    vol_sum = vol + vol_diff4

    diff_threshold1 = -10
    diff_threshold2 = max(vol_diff4)*0.05 + min(vol_diff4)*5.0
    diff_threshold3 = min(vol_diff4)*10.0

    time = np.arange(0,nframes) * (1.0/framerate)
    frame = np.arange(0,len(vol)) * (nframes*1.0/len(vol)/framerate)
    diff_index1 = findIndex(vol_diff4,diff_threshold1)
    diff_index2 = findIndex(vol_diff4,diff_threshold2)
    diff_index3 = findIndex(vol_diff4,diff_threshold3)
    setting = nframes * 1.0/len(vol)/framerate
    diff_index1 = list(map(lambda i: i*setting, diff_index1))
    diff_index2 = list(map(lambda i: i*setting, diff_index2))
    diff_index3 = list(map(lambda i: i*setting, diff_index3))
    end = nframes * (1.0/framerate)

    threshold1 = -10
    threshold2 = max(vol)*0.05 + min(vol)*5.0
    threshold3 = min(vol)*10.0

    time = np.arange(0,nframes) * (1.0/framerate)
    frame = np.arange(0,len(vol)) * (nframes*1.0/len(vol)/framerate)
    index1 = findIndex(vol_sum,threshold1)
    index2 = findIndex(vol_sum,threshold2)
    index3 = findIndex(vol_sum,threshold3)
    index1_init = findIndex(vol,threshold1)
    index2_init = findIndex(vol,threshold2)
    index3_init = findIndex(vol,threshold3)
    setting = nframes * 1.0/len(vol)/framerate
    index1 = list(map(lambda i: i*setting, index1))
    index2 = list(map(lambda i: i*setting, index2))
    index3 = list(map(lambda i: i*setting, index3))
    index1_init = list(map(lambda i: i*setting, index1_init))
    index2_init = list(map(lambda i: i*setting, index2_init))
    index3_init = list(map(lambda i: i*setting, index3_init))
    end = nframes * (1.0/framerate)

    def index_cut(index):
        #index1_init是原wavedate 取 0DB為基準
        #diff_index1是微4次 wavedate 取 0DB為基準
        index_del = []
        for i in range(len(index)-1):
            if i % 2 == 1: #尾為防止春嬌被切成春的尾跟嬌的頭
                if index[i+1] - index[i] < 0.1:
                    index_del.append(index[i])
                    index_del.append(index[i+1])
            if i % 2 == 0 and i < len(index)-2: #頭最外的頭，讓音最寬
                if index[i+1] - index[i] < 0.05 and index[i+2] - index[i+1] < 0.5:
                    index_del.append(index[i+1])
                    index_del.append(index[i+2])
        for i in range(len(index_del)):
            if index_del[i] in index:
                index.remove(index_del[i])

    index_cut(index1_init)
    print("切完index1_init:", index1_init)
    index_cut(diff_index1)
    print("切完diff_index1:", diff_index1)

    final_index = []
    final_index.extend(index1_init)

    for i in range(len(index1_init)-1):
        if i % 2 == 0:  #頭
            j = 0
            while diff_index1[j] < index1_init[i]:
                if diff_index1[j + 1] > index1_init[i]:
                    final_index[i] = diff_index1[j]
                j = j + 2
                if j > len(diff_index1) - 1:
                    break
        if i % 2 == 1:  #尾
            k = len(diff_index1) - 1
            while diff_index1[k] > index1_init[i]:
                if diff_index1[k-1] < index1_init[i]:
                    final_index[i] = diff_index1[k]
                k = k - 2
                if k < 0:
                    break
    print("合併後final_index:", final_index)

    def cut_voice(index):
        files = listdir("splitFile")
        print(files)
        for f in files:
            fullpath = join("splitFile/", f)
            os.remove(fullpath)

        song = AudioSegment.from_wav(thiswav_16K)
        for i in range(len(index) - 1):
            if i % 2 == 0:
                add_msec = (1 - (index[i+1] - index[i])) / 2 * 1000
                if add_msec < 0:
                    add_msec = 0
                firstSong = song[max(0,index[i]*1000-add_msec):min(index[i+1]*1000+add_msec, nframes / framerate * 1000)]
                if i<20:
                    firstSong.export("splitFile/firstSong0" + str(int(i/2)) + ".wav", format="wav")
                else:
                    firstSong.export("splitFile/firstSong" + str(int(i/2)) + ".wav", format="wav")

    cut_voice(final_index)
    return label_wav("splitFile", "conv_labels.txt", "my_frozen_graph.pb", 'wav_data:0','labels_softmax:0', 3)

