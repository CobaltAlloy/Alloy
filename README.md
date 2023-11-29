# Co-tools
Random cobalt stuff

## Editor modifications

### Preparing the editor

Editor modifications are based on unpacked Cobalt code from the BitSquid version of the game located in `7efe746cbba01385`.  

For that you will need:  

> [bitsquid_unp](https://web.archive.org/web/20221018164344/https://zenhax.com/download/file.php?id=959&sid=b46f061347c43223468aa896550bd9eb)
> [luajit-decompiler-v2](https://github.com/marsinator358/luajit-decompiler-v2)
> truncate_bytes.py
> rename_bitsquid.py

Process:  

- to be documented

For cobalt bitsquid data contained in `7efe746cbba01385`:  
-first run the file trough `bitsquid_unp.exe`  
-run `python truncate_bytes.py -t [path to unpacked 7efe746cbba01385]`  
-the script will remove the leading bytes from all .lua files in given folder  
-then run the files trough `luajit-decompiler-v2.exe`  
-lastly to sort the files to folders  
-run `python rename_bitsquid.py -s [path to decompiled lua source] -t [path to output folder]`  
-the output folder should contain the files with the given virtual folder structure  
