import os
import sys

if (len(sys.argv) < 2):
    print("For help use: python simple_deobfuscator.py help")
    exit(0)

if (sys.argv[1] == "help" or sys.argv[1] == "h"):
    print("Usage: python simple_deobfuscator.py <path/to/dictionary> <path/to/target/dir>")
    exit(0)

if (len(sys.argv) < 3):
    print("Please provide dictionary and target directory")
    exit(0)
    
bindings = sys.argv[1]
target_dir = sys.argv[2]

wildcards = ["(", ")", "[", "]", "{", "}", ",", ".", " ", ":", "\n"]

buffer_map = {}
buffer_name = ""
bindings_map = {}
bindings_read = open(bindings, "r").read()
for line in bindings_read.split("\n"):
    split = line.split(" ")
    
    if (split[0].endswith(".lua")):
        if (len(buffer_name) > 0):
            bindings_map[buffer_name] = buffer_map
        buffer_name = split[0]
        buffer_map = {}
    
    if (len(split) < 2):
        continue
    
    key, value = split[0], split[1] 
    buffer_map[key] = value
    print("mapping " + key + " to " + value + " registered")

if (len(buffer_name) > 0):
    bindings_map[buffer_name] = buffer_map

for root, dirnames, filenames in os.walk(target_dir):
    if (root.endswith("/")):
        root = root.removesuffix("/")
    
    if (len(filenames) == 0) :
        continue

    for file in filenames:
        if (not file.endswith(".lua")):
            continue
        file_open = open(root + "/" + file, "r")
        file_data = file_open.read()
        file_open.close()

        if file in bindings_map:
            file_map = bindings_map[file]        
            for key in file_map:
                for char in wildcards:
                    file_data = file_data.replace(key + char, file_map[key] + char)
        
        file_open = open(root + "/" + file, "w")        
        write_len = file_open.write(file_data)
        file_open.close()
        
        if (write_len != len(file_data)):
            print("Write error on " + root + "/" + file)
        else:
            print("Written " + root + "/" + file)
