import os
import sys

target = ""

for index, arg in enumerate(sys.argv):
    if "-t" == arg:
        if index > len(sys.argv):
            print("passed argument with no value")
            exit(0)
        target = sys.argv[index + 1].removesuffix("/")

if 0 == len(target):
    print("required argument -t [path to target dir]")
    exit(0)

for root, dirs, files in os.walk(target):
    if (root.endswith("/")):
        root = root.removesuffix("/")

    for file in files:
        if not file.endswith(".lua"):
            continue

        print(root + "/" + file)

        file_open = open(root + "/" + file, "rb")
        file_data = file_open.read()
        file_open.close()

        file_data = bytes([file_data[i] for i in range(8, len(file_data))])

        file_open = open(root + "/" + file, "wb")
        write_len = file_open.write(file_data)
        file_open.close()
