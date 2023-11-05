import os
import sys

if (len(sys.argv) < 2):
    print("For help use: python dict_creator.py help")
    exit(0)
    
if (sys.argv[1] == "help" or sys.argv[1] == "h"):
    print("Usage: python dict_creator.py <path/to/source/file> <path/to/decompiled/file>")
    exit(0)

if (len(sys.argv) < 3):
    print("Please provide source and decompiled files")
    exit(0)

source = sys.argv[1].removesuffix("/")
decomp = sys.argv[2].removesuffix("/")


source_open = open(source, "r")
source_read = source_open.read()
source_open.close()

stripped_source = []
in_comment = False
for line in source_read.split("\n"):
    if in_comment:
        if "]]" in line:
            line = line.split("]]", 1)[1]
            in_comment = False
        else:
            continue
    
    split = line.split("--", 1)
    line = split[0]
    comment = ""
    if (len(split) > 1):
        comment = split[1]
        
    if (len(comment) != 0):
        if comment.startswith("[["):
            if "]]" in comment:
                line += " "  + comment.split("]]", 1)[1]
            else:
                in_comment = True

    if (len(line.rstrip()) > 0):
        stripped_source.append(line.rstrip())

decomp_open = open(decomp, "r")
decomp_read = decomp_open.read()
decomp_open.close()

key_words = ["arg_", "var_", "iter_"]
key_chars = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "_"]

stripped_decomp = []
key_dict = {}
for line in decomp_read.split("\n"):
    if (len(line.rstrip()) > 0):
        stripped_decomp.append(line.rstrip())
        
    for key_word in key_words:
        while key_word in line:
            line = line.split(key_word, 1)[1]
            key_candidate = key_word
            chars = True
            while chars:
                chars = False
                for char in key_chars:
                    if line.startswith(char):
                        line = line.removeprefix(char)
                        key_candidate += char
                        chars = True
                        break
            if (len(key_candidate) >= 7):
                if key_candidate in key_dict:
                    continue
                else:
                    key_dict[key_candidate] = len(stripped_decomp) - 1

def key_sort(key):
    key_parts = key.split("_")
    val = int(key_parts[1]) * 1000 + int(key_parts[2]) * 10
    if "arg" == key_parts[0]:
        val += 1
    if "var" == key_parts[0]:
        val += 2
    if "iter" == key_parts[0]:
        val += 3
    return val
sorted_keys = sorted(key_dict.keys(), key=lambda s: key_sort(s))

print(len(stripped_decomp))

out = source.split("/")[-1] + "\n"
for progress, key in enumerate(sorted_keys):
    out += key + " "

    print("\x1b[2J\x1b[1;0H=================Looking for: " + key + " ================= " + str(progress + 1) + "/" + str(len(sorted_keys)) + " \x1b[K")
    for i in range(5):
        key_line = key_dict[key]
        if (key_line + i - 2 > -1 and key_line + i - 2 < len(stripped_decomp)):
            print("\x1b[" + str(i + 2) + ";0H" + stripped_decomp[key_line + i - 2])
    print("\x1b[7;0H================================================================")
    loop = True
    while loop:
        search = input("\x1b[8;0HEnter search term: \x1b[K")

        for index, line in enumerate(stripped_source):
            if search in line:
                for i in range(5):
                    key_line = key_dict[key]
                    if (key_line + i - 2 > -1 and key_line + i - 2 < len(stripped_source)):
                        print("\x1b[" + str(i + 10) + ";0H" + stripped_source[key_line + i - 2] + "\x1b[K")

        mapping = input("\x1b[16;0HEnter mapping or press enter for another search: \x1b[K")
        if (len(mapping) > 0):
            out += mapping + "\n"
            loop = False

output = open(source.split("/")[-1].removesuffix(".lua") + ".map", "w")
output.write(out)
output.close()    
