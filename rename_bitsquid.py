import os
import sys

source = ""
target = ""

for index, arg in enumerate(sys.argv):
    if "-s" == arg:
        if index > len(sys.argv):
            print("passed argument with no value")
            exit(0)
        source = sys.argv[index + 1].removesuffix("/")
    if "-t" == arg:
        if index > len(sys.argv):
            print("passed argument with no value")
            exit(0)
        target = sys.argv[index + 1].removesuffix("/")

if 0 == len(source):
    print("required argument -s [path to source dir]")
    exit(0)
if 0 == len(target):
    print("required argument -t [path to target dir]")
    exit(0)

for root, dirs, files in os.walk(source):
    if (root.endswith("/")):
        root = root.removesuffix("/")

    for file in files:
        if not file.endswith(".lua"):
            continue

        print("Reading: " + root + "/" + file)
        source_open = open(root + "/" + file, "r")
        source = source_open.read().replace("\ufeff", "")
        source_open.close()

        target_path = source.split("\n", 1)[0].split("/", 1)[1]
        print("writing: " + target + "/" + target_path)

        if not os.path.exists((target + "/" + target_path).rsplit("/", 1)[0]):
            os.makedirs((target + "/" + target_path).rsplit("/", 1)[0])
        target_open = open(target + "/" + target_path, "w")
        target_open.write(source)
        target_open.close()
