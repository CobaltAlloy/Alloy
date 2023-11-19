# Co-tools
Random cobalt tools

For cobalt bitsquid data contained in `7efe746cbba01385`:  
-first run the file trough `bitsquid_unp.exe`  
-run `python truncate_bytes.py -t [path to unpacked 7efe746cbba01385]`  
-the script will remove the leading bytes from all .lua files in given folder  
-then run the files trough `luajit-decompiler-v2.exe`  
-lastly to sort the files to folders  
-run `python rename_bitsquid.py -s [path to decompiled lua source] -t [path to output folder]`  
-the output folder should contain the files with the given virtual folder structure  
