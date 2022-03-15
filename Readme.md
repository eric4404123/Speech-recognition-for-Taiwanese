# Tensoeflow speech recognition for Taiwanese
本實驗以[tensoeflow speech commands](https://www.tensorflow.org/tutorials/audio/simple_audio)為主，搭配以錄製30個台語單詞進行語音辨識## 現行程式所需軟體以及版本


### 所需軟體:
|軟體名稱|軟體版本|
|---     |---     |
|python|3.6.5|
|Django|2.0.2|
|django-allauth|0.35.0|
|pydub|0.23.0|
|ffmpeg|
|tensorflow|1.9.0|
###### 詳細可以參考environment.txt

### 執行網站:
確認路徑為此資料夾，開啟cmd輸入:
```
python manage.py runserver
```
即可使用
### 上傳檔案:
在網站內點選上傳或全部上傳，錄音檔案會儲存至document文件中

## 整理檔案之python程式

#### 1. readAudio.py :
此程式可以整理資料夾內的錄音data數據，每個文本分別有誰錄了多少個並輸出成CSV檔。可在內部修改mypath來指定欲進行統計的資料夾。注:此程式會讀取conv_labels.txt來選擇子資料夾為何
#### 2. testAcc.py:
此程式可以用來篩選那些檔案為較佳的training用檔案。此檔案會去讀my_frozen_graph.pb進行辨識篩選，並將最後的辨識結果有排入前三名者，輸出到一個名為WavOK的資料夾。注:此程式會讀取conv_labels.txt來選擇子資料夾為何
#### 3. transTo16K.py:
可以將wav檔全部轉換成，可traning的16K檔案。可在內部修改mypath來指定欲進行轉換的資料夾

