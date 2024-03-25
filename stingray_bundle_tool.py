import time
import zlib
import sys
import os

##
##  Argument processing
##

def print_help():
    print("usage: ")
    print("   unpacking: python stingray_bundle_tool.py -u <targetBundlePath> <outputFolderPath>")
    print("   repacking: python stingray_bundle_tool.py -p <targetFolderPath>")
    print("   add to map: python stingray_bundle_tool.py -m <targetFolderPath> <relativeFilePath>")

if len(sys.argv) < 3:
    print_help()
    quit()

match sys.argv[1]:
    case "-u":
        source = sys.argv[2]
        target = sys.argv[3]
    case "-p":
        source = ""
        target = sys.argv[2]
    case "-m":
        source = sys.argv[3]
        target = sys.argv[2]
    case "-h" | "--help":
        print_help()
        quit()
    case _:
        print("switch unrecognised, please run without arguments for usage help")
        quit()

##
##  File hash mappings
##

known_types = {
        b'\x3f\x37\x1f\xdb\xea\x82\x7f\x38':("default",         ".meta"),       # metadata ?
        #b'\x3f\x45\xa7\xe9\x0b\x8d\xa4\xe0':("default",         ".b"),          #
        b'\x50\x70\xb9\x13\x7b\xd9\xfa\x5b':("default",         ".composite"),  # composite ?
        b'\x5b\x22\x2e\x97\x9a\xc2\x1d\x66':("lua-bytecode",    ".ids"),        # lua binary .ids
        b'\x64\x25\xe3\xfb\x6d\xd4\xb7\x8c':("default",         ".aiconcepts"), # aiconcepts ?
        b'\x74\xc3\xba\xf6\xe8\xa9\x1f\x3b':("default",         ".network_cfg"), # network config ? contains a lot of rpc stuff
        b'\x7a\xe7\xe5\xd1\x9e\x6d\x9c\xad':("default",         ".package"),    # package ? looks like a dict
        b'\x82\x3a\xc1\x8e\x8f\xce\x3e\x54':("default",         ".leaderboard_sort"), # ? seems like instructions for ordering, it mentions time a lot
        b'\x8b\xc3\x6b\xe6\x1f\x21\x34\xda':("default",         ".map"),        # map ?
        b'\x92\x83\x5d\xb7\xc6\x27\x67\x0e':("default",         ".tilephysics"), # tilephysics ?
        b'\x93\x9a\x23\x77\xa4\x32\xee\xe5':("default",         ".sl"),         # shader libraries ?
        b'\x95\x27\x20\xc3\x09\x85\xfd\xe2':("default",         ".pieces"),     # pieces ?
        b'\x9c\x31\x95\x47\xe2\x2f\x86\x27':("default",         ".render_cfg"), # render config ?
        b'\xac\x5b\x35\xdb\x4a\xc8\x84\x88':("default",         ".data"),       # ? lots of repeating data
        b'\xa7\x31\x36\x74\xab\xb2\xd1\x04':("default",         ".movement"),   # movement ?
        b'\xb5\xae\x75\x45\xc7\x3c\x5c\x9e':("default",         ".sl_group"),   # shader library group ?
        b'\xcc\x2f\x7a\xa3\x23\xeb\x31\xad':("lua-bytecode",    ".convert"),    # lua binary .convert
        b'\xc6\x26\xe1\xe9\x48\xe6\x58\x8d':("default",         ".map_data"),   # ? one of the two files from map bundles
        b'\xd3\xae\xa5\x55\xf6\xf2\x44\x77':("default",         ".localisation"), # localisation ?
        #b'\xd3\x0f\xb4\x10\xab\x2b\x97\x0d':(), #
        b'\xd6\x7e\xa4\x37\x06\x2a\xd1\x53':("default",         ".tilesprites"), # tilesprites ?
        b'\xdf\xde\x6a\x87\x97\xb4\xc0\xea':("default",         ".material"),   # material ?
        b'\xe2\x17\xd1\x2c\xfa\x8d\x4e\xa1':("lua-bytecode",    ".lua"),        # lua binary .lua
        b'\xec\x3e\x5d\x22\x3e\x03\x58\xac':("default",         ".rig"),        # rig ?
        b'\xf0\xad\xad\x85\xec\x4c\xe1\xd8':("default",         ".teams"),      # teams ?
        b'\xf3\xe1\x01\x39\x90\xf1\x02\x4d':("small",           ".small"),      # ? small files also a strange case of buffer violation
        b'\xf4\x22\xf9\xe5\x78\xcb\x03\xd5':("default",         ".talks"),      # talks ?
        }

# generates mappings from file types to their hashes
file_to_hash = {}
for key in known_types:
    file_to_hash[known_types[key][1]] = key

##
##  Global settings
##

announce_output = True

U64_MAX_VALUE = 0xffffffffffffffff
U32_MAX_VALUE = 0xffffffff


##
##  Minor functions
##

def u64(value):
    return value & U64_MAX_VALUE

def u32(value):
    return value & U32_MAX_VALUE

# from bitsquid-foundation/murmur_hash.cpp
# seed -> unsigned 64 bit value
# key -> key to hash in ascii bytes
def hash(key, seed=0):
    key = bytes(key)
    _len = len(key) # string's size in bits
    seed = u64(seed)
    
    m = 0xc6a4a7935bd1e995
    r = 47

    h = seed ^ u64(_len * m)
    i = 0
    for i in range(8, _len + 1, 8):
        k = int.from_bytes(key[i-8:i], byteorder="little")
        
        k = u64(k * m)
        k ^= k >> r
        k = u64(k * m)

        h ^= k
        h = u64(h * m)
   
    choice = _len & 7
    if choice >= 7:
        h ^= key[i + 6] << 48
    if choice >= 6:
        h ^= key[i + 5] << 40
    if choice >= 5:
        h ^= key[i + 4] << 32
    if choice >= 4:
        h ^= key[i + 3] << 24
    if choice >= 3:
        h ^= key[i + 2] << 16
    if choice >= 2:
        h ^= key[i + 1] << 8
    if choice >= 1:
        h ^= key[i]
        h = u64(h * m)
   
    h ^= h >> r
    h = u64(h * m)
    h ^= h >> r

    return int.to_bytes(h, 8, byteorder="little")


# flips the byte buffer
def switch_endian(byte, strip_empty=True):
    out = b''
    if strip_empty:
        byte = byte.strip(b'\x00')
    size = len(byte)
    for i in range(0, size):
        out += byte[ size - i - 1:size - i ]
    return out

# creates hex representation of bytes as a string with min required length
def hex_str(byte, buffer=16):
        h_str = str(hex(int.from_bytes(byte,byteorder="little"))).removeprefix("0x")
        return "0" * (buffer - len(h_str)) + h_str

# makes sure the path is a valid directory
def ensure_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
        if announce_output:
            print("created directory " + dir)
 
# writes file to path
def write_data_to_target(name_data, suffix, byte_data, hex_names=True):
    global target
    global announce_output

    path = target
    if hex_names:
        name = hex_str(name_data) + suffix
    else:
        loc, name = name_data.rsplit("/", 1)
        path += "/" + loc

    ensure_dir(path)
    
    if announce_output: 
        print("writing file: " + path + "/" + name)
    open(path + "/" + name, "wb").write(byte_data)

def read_file(path):
    if not os.path.exists(path):
        print("unable to locate file: " + path)
        exit()
    read_handle = open(path, "rb")
    data = b''
    while True:
        b = read_handle.read(256)
        data += b
        if len(b) < 256:
            break
    return data

##
##  Decompiler features
##

# partial implementation that should work in most if not all cases
def get_le_ub128(pointer, buffer):
    value = buffer[pointer]
    pointer += 1
    if value >= 0x80:
        value = value & 0x7f | (buffer[pointer] & 0x7f) << 7
        pointer += 1
    return pointer, value

def get_chunk(pointer, buffer):
    pointer, size = get_le_ub128(pointer, buffer)
    if size == 0:
        return b'', 0
    data = buffer[pointer:pointer + size]
    assert len(data) == size
    return pointer, data 

##
##
##

map = []
lua_name_map = {}

##
##  Execution section
##

start_time = time.time()

match sys.argv[1]:
    case "-u":
        # decompressor
        chunk = 0
        sum = 0

        bundle_read_handle = open(source, "rb")
        data = bundle_read_handle.read(4) 
        if data != b'\x04\x00\x00\xf0':
            print(data)
        size = int.from_bytes(bundle_read_handle.read(4),byteorder="little")
        assert bundle_read_handle.read(4) == b'\x00\x00\x00\x00'
    
        unpacked_bytes = b''
        while True:
            chunk = int.from_bytes(bundle_read_handle.read(4),byteorder="little")
            if chunk == 0:
                break
       
            unpacked_bytes += zlib.decompress(bundle_read_handle.read(chunk))
       
            # the following sentence is incrediby stupid so disregard it i just find it amusing
            #
            # the header consists of \x56\x02\x00\x00 read as little endian decimal and not hex
            # followed by 256 bytes of data
            #
            # ignoring that 260 bytes of data are consistant
            # the first 4 seem to be dependant on the file
            # the next 256 seem to be consistant across files
            # as always more researcg necesary
            entries = unpacked_bytes[0:4]
            header = unpacked_bytes[4:260] # header
       
            sum += chunk
        
        ensure_dir(target)
        open(target + "/" + source.split("/")[-1] + ".decompressed", "wb").write(unpacked_bytes)

        # data parser
        unpacked_sum = 0
        last_action = b''
        last_hash = b''
        
        offset = 260
        while offset < len(unpacked_bytes):
            match unpacked_bytes[offset:offset + 8]:
                case b'\x05\x00\x00\x00\x00\x00\x00\x00':
                    print("multi mappings are not supported yet!")
                    quit()
    
                case action if action[0:4] == b'\x01\x00\x00\x00':
                    # handle what we can assume is a file
                    offset += 8
    
                    buffer = unpacked_bytes[offset:offset + 4] 
                    if buffer != b'\x00\x00\x00\x00':
                        print(buffer)
                    offset += 4 # presumed buffer
                    
                    # most files contain 32 bit size
                    size = int.from_bytes(unpacked_bytes[offset:offset + 4],byteorder="little")
                    offset += 4
    
                    if last_action == b'\xf3\xe1\x01\x39\x90\xf1\x02\x4d':
                        print("small file skipping buffer!")
                    elif unpacked_bytes[offset:offset + 4] != b'\x00\x00\x00\x00':
                        print("presumed buffer not empty!\ninstruction " + str(hex(int.from_bytes(last_action,byteorder="big"))))
                    else:
                        offset += 4 # presumed buffer
                    
                    if last_action not in list(known_types):
                        print("type " + hex_str(last_action[::-1]) + " of file " + hex_str(last_hash) + 
                              " not known at global offset " + str(offset))
                        parser = ("default", ".unknown")
                    else:
                        parser = known_types[last_action]
    
                    match parser[0]:
                        case "default":
                            file_bytes = unpacked_bytes[offset:offset + size]
                            write_data_to_target(last_hash, parser[1], file_bytes)
    
                        case "lua-bytecode":
                            # handle a luajit mapping
                            # we can strip the first 8 bytes here since they dont dissasamble
                            if announce_output:
                                # per file size bytes
                                print("lua bytecode of size: " + hex_str(switch_endian(unpacked_bytes[offset:offset + 8], False)))
                            file_bytes = unpacked_bytes[offset + 8:offset + size]

                            file_name = get_chunk(5, file_bytes)[1].decode("utf-8").strip("@")
                            lua_name_map[hex_str(last_hash) + parser[1]] = file_name
                            write_data_to_target(file_name, parser[1], file_bytes, False)
    
                        case "small":
                            # small files witch probably arent even files but still
                            # they all seem to be 4 bytes witch repeat twice in the data
                            print("small size: " + str(size))
                            if unpacked_bytes[offset:offset + size] == unpacked_bytes[offset + size:offset + 2 * size]:
                                print("data confirmed!")
                                file_bytes = unpacked_bytes[offset:offset + size]
                                write_data_to_target(last_hash, parser[1], file_bytes)
                            else:
                                print("data confirmation failed!")
                            size *= 2
    
                        case _:
                            print(last_action)
                            print("parse error at " + str(offset) + " at " + str(sum) + "!")
                            quit()
    
                    unpacked_sum += size
                    offset += size
    
                case b'\x00\x00\x00\x00\x00\x00\x00\x00':
                    print("done!")
                    break
    
                case _:
                    last_action = action 
                    offset += 8
                    # handle known mappings
                    last_hash = unpacked_bytes[offset:offset + 8] 
                    if not (last_hash, last_action) in map:
                        map.append((last_hash, last_action))
                    offset += 8

        map_write_handle = open(target + "/" + source.split("/")[-1] + ".lua_map", "w") 
        for file in lua_name_map:
            map_write_handle.write(file + " " + lua_name_map[file] + "\n")

        print("|provided size:" + str(size) + "|unpacked:" + str(unpacked_sum) + "|read:" + str(sum) + "|entries: " + str(int.from_bytes(entries, byteorder="little")) + "|")

    case "-p":
        candidates = []
        for candidate in os.listdir(target):
            if candidate.endswith(".decompressed"):
                candidates.append(candidate)
                print("found potential bundle data: " + candidate)
        if len(candidates) == 1:
            lua_map_path = target + "/" + candidates[0].strip(".decompressed") + ".lua_map"
            if os.path.exists(lua_map_path):
                print("found lua file map: " + lua_map_path)
                
                for line in open(lua_map_path, "r").readlines():
                    file_hash, file_path = line.strip("\n").split(" ", 1)
                    lua_name_map[file_hash] = file_path

            data_read_handle = open(target + "/" + candidates[0], "rb")
            bundle = candidates[0].split(".")[0]
            print("generating bundle: " + bundle)
        else:
            print("too many potential candidates, make sure the right direcory is being targeted")
            exit()
        
        read_map_size = data_read_handle.read(4)
 
        # same for every file so no clue if relevant
        bundle_header = data_read_handle.read(256)
        if announce_output:
          print("copied header: " + hex_str(switch_endian(bundle_header)))

        bundle_header += b'\x00\x00' * (256 - len(bundle_header))
       
        is_patch = False
        map_size = 0
        bundle_data = b''
        print("generating bundle data")
        for name_hash in lua_name_map:
            hex_name = switch_endian(bytes.fromhex(name_hash.split(".")[0]), False)
            action = hash(str(lua_name_map[name_hash]).split(".")[1].encode("utf-8"))
            entry_data = known_types[action]
            match entry_data[0]:
                case "default":
                    path = target + "/" + name_hash
                    if not os.path.exists(path):
                        is_patch = True
                        continue
                        
                    data = read_file(path)

                    if announce_output:
                        print("writing " + name_hash.split(".")[0] + " of size " + hex_str(len(data).to_bytes(4, "little"), 8))
                    bundle_data += action + hex_name \
                        + b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
                        + len(data).to_bytes(4, "little") + b'\x00\x00\x00\x00' + data

                case "lua-bytecode":
                    if os.path.exists(target + "/" + name_hash):
                        path = target + "/" + name_hash
                    elif os.path.exists(target + "/" + lua_name_map[name_hash]):
                        path = target + "/" + lua_name_map[name_hash]
                    else:
                        is_patch = True
                        continue
                        
                    data = read_file(path)
                    
                    if announce_output:
                        print("writing " + name_hash.split(".")[0] + " of size " + hex_str((len(data) + 8).to_bytes(4, "little"), 8))
                    bundle_data += action + hex_name \
                        + b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
                        + (len(data) + 8).to_bytes(4, "little") + b'\x00\x00\x00\x00' \
                        + len(data).to_bytes(4, "little") + b'\x02\x00\x00\x00' + data

            bundle_header += action + hex_name
            map_size += 1
        
        print("writing bundle: " + bundle + " map size: " + str(map_size))
        if is_patch:
            bundle += ".patch_id"
        bundle_data = map_size.to_bytes(4, byteorder="little") + bundle_header + bundle_data
        bundle_write_handle = open(bundle, "wb")
        bundle_write_handle.write(b'\x04\x00\x00\xf0' + len(bundle_data).to_bytes(4, "little") + b'\x00\x00\x00\x00')

        offset = 0
        while True:
            part = zlib.compress(bundle_data[offset:offset + 65536])
            bundle_write_handle.write((len(part)).to_bytes(2, "little") + b'\x00\x00' + part)
            if offset >= len(bundle_data):
                break
            offset += 65536

        print("done!")
    
    case "-m":
        candidates = []
        for candidate in os.listdir(target):
            if candidate.endswith(".decompressed"):
                candidates.append(candidate)
                print("found potential bundle data: " + candidate)
        if len(candidates) == 1:
            lua_map_path = target + "/" + candidates[0].strip(".decompressed") + ".lua_map"
            if os.path.exists(lua_map_path):
                print("found lua file map: " + lua_map_path)
                
                for line in open(lua_map_path, "r").readlines():
                    file_hash, file_path = line.strip("\n").split(" ", 1)
                    lua_name_map[file_hash] = file_path
        
        else:
            print("too many potential candidates, make sure the right direcory is being targeted")
            exit()
        
        if not os.path.exists(target + "/" + source):
            print("requested file not found")
            exit()

        target_parts = source.rsplit(".", 1)
        lua_name_map[hex_str(hash(target_parts[0].encode("utf-8"))) + "." + target_parts[1]] = source
        print("added entry: " + hex_str(hash(target_parts[0].encode("utf-8"))) + "." + target_parts[1] + " " + source)

        map_write_handle = open(lua_map_path, "w") 
        for file in lua_name_map:
            map_write_handle.write(file + " " + lua_name_map[file] + "\n")

print("execution took: " + str(round(time.time() - start_time, 3)) + "s")
