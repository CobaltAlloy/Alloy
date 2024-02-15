import zlib
import sys
import os

if len(sys.argv) < 3:
    print("usage: python stingray_bundle_unp.py <targetBundlePath> <outputFolderpath>")
    quit()

# provide 7efe or a copy of it
source = sys.argv[1]
target = sys.argv[2]
hex_names = True
announce_output = False

read_handle = open(source, "rb")
chunk = 0
sum = 0
unpacked_sum = 0
map = []

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

def hex_str(byte, buffer=16):
        h_str = str(hex(int.from_bytes(byte,byteorder="little"))).removeprefix("0x")
        return "0" * (buffer - len(h_str)) + h_str

def write_path(map, suffix, byte_data):
    global target
    global hex_names
    global announce_output

    if not os.path.exists(target):
        os.makedirs(target)
        if announce_output:
            print("created directory " + target)
            
    if hex_names:
        name = hex_str(map, 16) + suffix
    else:
        print("not implemented!")
        quit()

    if announce_output: 
        print(name)
    open(target + "/" + name, "wb").write(byte_data)


def process_bytes(data):
    global map
    
    unpacked = 0
    last_action = b''
    
    offset = 260
    while offset < len(data):
        match data[offset:offset + 8]:
            case b'\x05\x00\x00\x00\x00\x00\x00\x00':
                print("multi mappings are not supported yet!")
                quit()

            case action if action[0:4] == b'\x01\x00\x00\x00':
                # handle what we can assume is a file
                offset += 8

                assert data[offset:offset + 4] == b'\x00\x00\x00\x00'
                offset += 4 # presumed buffer
                
                # most files contain 32 bit size
                size = int.from_bytes(data[offset:offset + 4],byteorder="little")
                offset += 4

                if last_action == b'\xf3\xe1\x01\x39\x90\xf1\x02\x4d':
                    print("small file skipping buffer!")
                elif data[offset:offset + 4] != b'\x00\x00\x00\x00':
                    print("presumed buffer not empty!\ninstruction " + str(hex(int.from_bytes(last_action,byteorder="big"))))
                else:
                    offset += 4 # presumed buffer
                
                if last_action not in list(known_types):
                    print("type " + hex_str(last_action[::-1]) + " of file " + hex_str(map[-1]) + 
                          " not known at global offset " + str(offset))
                    parser = ("default", ".unknown")
                else:
                    parser = known_types[last_action]

                match parser[0]:
                    case "default":
                        file_bytes = data[offset:offset + size]
                        write_path(map[-1], parser[1], file_bytes)

                    case "lua-bytecode":
                        # handle a luajit mapping
                        # we can strip the first 8 bytes here since they dont dissasamble
                        data[offset:offset + 8] # no clue what these are for
                        file_bytes = data[offset + 8:offset + size]
            
                        write_path(map[-1], parser[1], file_bytes)

                    case "small":
                        # small files witch probably arent even files but still
                        # they all seem to be 4 bytes witch repeat twice in the data
                        print("small size: " + str(size))
                        if data[offset:offset + size] == data[offset + size:offset + 2 * size]:
                            print("data confirmed!")
                            file_bytes = data[offset:offset + size]
                            write_path(map[-1], parser[1], file_bytes)
                        else:
                            print("data confirmation failed!")
                        size *= 2

                    case _:
                        print(last_action)
                        print("parse error at " + str(offset) + " at " + str(sum) + "!")
                        quit()

                unpacked += size
                offset += size

            case b'\x00\x00\x00\x00\x00\x00\x00\x00':
                print("done!")
                break

            case _:
                last_action = action 
                offset += 8
                # handle known mappings
                map.append(data[offset:offset + 8])
                offset += 8

    return unpacked


assert read_handle.read(4) == b'\x04\x00\x00\xf0'
size = int.from_bytes(read_handle.read(4),byteorder="little")
assert read_handle.read(4) == b'\x00\x00\x00\x00'

unpacked_bytes = b''
while True:
    chunk = int.from_bytes(read_handle.read(4),byteorder="little")
    if chunk == 0:
        break
   
    unpacked_bytes += zlib.decompress(read_handle.read(chunk))
    
    # the header consists of \x56\x02\x00\x00 read as little endian decimal and not hex
    # followed by 256 bytes of zlib data
    header = unpacked_bytes[0:260] # zlib header
   
    sum += chunk

open(source.split("/")[-1], "wb").write(unpacked_bytes)
unpacked_sum = process_bytes(unpacked_bytes)

print("|provided size:" + str(size) + "|unpacked:" + str(unpacked_sum) + "|read:" + str(sum) + "|")
