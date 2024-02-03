from urllib.error import HTTPError
from urllib.error import ContentTooShortError
from urllib import request
import sys
import os
import time

if len(sys.argv) < 4:
    print("usage: python file_downloader.py <downloadHost> <fileListName> <filesFolderName>")
    quit()

downloadHost = "http://" + sys.argv[1]
fileListName = sys.argv[2].removeprefix("/")
filesFolderName = sys.argv[3].removeprefix("/").removesuffix("/")

targetDir = filesFolderName + "_download"

url = downloadHost + "/" + fileListName
if not os.path.exists(fileListName):
    print("Downloading required file " + fileListName)
    response = request.urlretrieve(url, fileListName)

data = open(fileListName, "r").readlines()
for i, line in enumerate(data):
    file = line.strip().split(";")[3]
    
    url = downloadHost + "/" + filesFolderName + "/" + file.replace(" ", "%20")
    path = targetDir + "/" + file
    if not os.path.exists(path.rsplit("/", 1)[0]):
        os.makedirs(path.rsplit("/", 1)[0])
    if not os.path.exists(path):
        print("Downloading " + str(len(data)) + "/" + str(i + 1) + "  " + file)
        for i in range(5):
            try:
                response = request.urlretrieve(url, path)
                break
            except ContentTooShortError:
                print("Failed retrying in 5s")
                time.sleep(5)
            except HTTPError as e:
                if e.code == 404:
                    print("Requested file doesn't exist")
                    break
print("Done")
