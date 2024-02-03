from urllib import request
import os
import sys
import time
import threading

targetDir = "files2_Download"
targetFile = "filelist2.txt"
targetUrl = "http://assets.playcobalt.com/"

url = targetUrl + targetFile
if not os.path.exists(targetFile):
    print("Downloading required file " + targetFile)
    response = request.urlretrieve(url, targetFile)

data = open(targetFile, "r").readlines()
for i, line in enumerate(data):
    file = line.strip().split(";")[3]
    
    url = targetUrl + "files2/" + file.replace(" ", "%20")
    path = targetDir + "/" + file
    if not os.path.exists(path.rsplit("/", 1)[0]):
        os.makedirs(path.rsplit("/", 1)[0])
    if not os.path.exists(path):
        print("Downloading " + str(len(data)) + "/" + str(i + 1) + "  " + file)
        for i in range(5):
            try:
                response = request.urlretrieve(url, path)
                break
            except:
                print("Failed retrying in 5s")
            time.sleep(5)
