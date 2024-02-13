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

read_handle = open(source, "rb")
chunk = 0
sum = 0
unpacked_sum = 0
map = []

def process_bytes(data):
    global map
    
    unpacked = 0
    
    offset = 260
    while offset < len(data):
        if data[offset:offset + 8] == b'\x01\x00\x00\x00\x00\x00\x00\x00':
            offset += 8
            # handle what we can assume is a file
            assert data[offset:offset + 4] == b'\x00\x00\x00\x00'
            offset += 4 # presumed buffer
   
            size = int.from_bytes(data[offset:offset + 4],byteorder="little")
            offset += 4

            assert data[offset:offset + 4] == b'\x00\x00\x00\x00'
            offset += 4 # presumed buffer
            
            # we can strip the first 8 bytes here since they dont dissasamble
            data[offset:offset + 8] # no clue what these are for
            file_bytes = data[offset + 8:offset + size]
            
            if not os.path.exists(target):
                os.makedirs(target)
            
            if hex_names:
                name = str(hex(int.from_bytes(map[-1],byteorder="little"))).removeprefix("0x")
                name = "0" * (16 - len(name)) + name + ".lua"
            else:
                print("not implemented!")
                quit()

            print(name)
            open(target + "/" + name, "wb").write(file_bytes)

            unpacked += size
            offset += size

        elif data[offset:offset + 8] == b'\xe2\x17\xd1\x2c\xfa\x8d\x4e\xa1':
            offset += 8
            # handle what we can assume is a mapping
            map.append(data[offset:offset + 8])
            offset += 8
        
        elif data[offset:offset + 8] == b'\x00\x00\x00\x00\x00\x00\x00\x00':
            print("done!")
            break

        else:
            print(data[offset:offset + 8])
            print("error at " + str(offset) + " at " + str(sum) + "!")
            quit()

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

unpacked_sum = process_bytes(unpacked_bytes)

print("|provided size:" + str(size) + "|unpacked:" + str(unpacked_sum) + "|read:" + str(sum) + "|")
