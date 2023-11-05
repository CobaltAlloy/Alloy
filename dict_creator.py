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
source_read = source_open.read().replace("\ufeff", "")
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
decomp_read = decomp_open.read().replace("\ufeff", "")
decomp_open.close()

key_words = ["arg_", "var_", "iter_"]
key_chars = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "_"]
wildcards = ["(", ")", "[", "]", "{", "}", ",", ".", " ", ":", "\n"]

stripped_decomp = []
key_dict = {}
for line in decomp_read.split("\n"):
    if (len(line.rstrip()) > 0):
        stripped_decomp.append(line.rstrip())
    
    for key_word in key_words:
        line_proc = line
        while key_word in line_proc:
            line_proc = line_proc.split(key_word, 1)[1]
            key_candidate = key_word
            chars = True
            while chars:
                chars = False
                for char in key_chars:
                    if line_proc.startswith(char):
                        line_proc = line_proc.removeprefix(char)
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
    val = int(key_parts[2]) * 100000 + int(key_parts[1] * 10)
    if "arg" == key_parts[0]:
        val += 1
    if "var" == key_parts[0]:
        val += 2
    if "iter" == key_parts[0]:
        val += 3
    return val
sorted_keys = sorted(key_dict.keys(), key=lambda s: key_sort(s))

previous_search = ""
out = source.split("/")[-1] + "\n"
for progress, key in enumerate(sorted_keys):
    print("\x1b[2J\x1b[1;0H=================Looking for: " + key + " ================= " + str(progress + 1) + "/" + str(len(sorted_keys)) + " \x1b[K")
    for i in range(11):
        key_line = key_dict[key]
        if (key_line + i - 5 > -1 and key_line + i - 5 < len(stripped_decomp)):
            print("\x1b[" + str(i + 2) + ";0H" + " \x1b[K" + stripped_decomp[key_line + i - 5].replace(key, "\x1b[38;2;200;200;0m" + key + "\x1b[0m"))
    print("\x1b[13;0H================================================================")
    loop = True
    while loop:
        print("\x1b[14;0H\x1b[KPrevious search: " + previous_search)
        search = input('\x1b[15;0H\x1b[KEnter search term or "num" or press enter for previous search: ')
        if (len(search) == 0):
            search = previous_search
        previous_search = search

        source_correction = 0
        decomp_correction = 0
        if (search.startswith("num ")):
            split = search.split(" ")
            search = split[0]
            if (len(split) > 1):
                source_correction = int(split[2])
                decomp_correction = int(split[1])
        
        selection = ""
        if (search.strip() == "num"):
            key_line = key_dict[key]
            for i in range(11):
                if (key_line + source_correction + i - 5 > -1 and key_line + source_correction + i - 5 < len(stripped_source)):
                    if (i == 5):
                        line_start = stripped_decomp[key_line + decomp_correction].split(key)[0].strip().replace(", ", ",")
                        stripped_source_line = stripped_source[key_line + source_correction].strip().replace(", ", ",")
                        if (len(line_start) > 0):
                            line = stripped_source_line.split(line_start, 1)
                        else:
                            line = ["", stripped_source_line.replace(", ", ",")]
                        print("\x1b[30;0H\x1b[K" + stripped_source_line + " ==== " + line_start)
                        if (len(line) > 1):
                            line = line[1].strip()
                            selection_candidates = []
                            for char in wildcards:
                                selection_candidates.append(line.split(char, 1)[0])
                            selection_candidates.sort(key=len)
                            selection = selection_candidates[0]
                    print("\x1b[" + str(i + 17) + ";0H" + "\x1b[K" + stripped_source[key_line + source_correction + i - 5].replace(selection, "\x1b[38;2;0;200;200m" + selection + "\x1b[0m"))
                else:
                    print("\x1b[" + str(i + 17) + ";0H" + "\x1b[K")
        else:
            for index, line in enumerate(stripped_source):
                if search in line:
                    for i in range(11):
                        if (index + i - 5 > -1 and index + i - 5 < len(stripped_source)):
                            print("\x1b[" + str(i + 17) + ";0H" + "\x1b[K" + stripped_source[index + i - 5].replace(search, "\x1b[38;2;0;200;200m" + search + "\x1b[0m"))
                        else:
                            print("\x1b[" + str(i + 17) + ";0H" + "\x1b[K")
                else:
                    for i in range(11):
                        print("\x1b[" + str(i + 17) + ";0H" + "\x1b[K")

        if (len(selection) > 0):
            print("\x1b[29;0H\x1b[KAutomatic selection: " + selection)
        mapping = input('\x1b[31;0HEnter mapping or "use selection" to use automatic selection or press enter for another search: \x1b[K')
        if (mapping == "use selection"):
            mapping = selection
        if (len(mapping.strip()) > 0):
            for char in wildcards:
                for index, line in enumerate(stripped_decomp):
                    line = line + "\n"
                    stripped_decomp[index] = line.replace(key + char, mapping.strip() + char).removesuffix("\n")
            
            out += key + " " + mapping.strip() + "\n"
            loop = False

output = open(source.split("/")[-1].removesuffix(".lua") + ".map", "w")
output.write(out)
output.close()    
