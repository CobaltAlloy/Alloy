# Co-tools
Random cobalt stuff

## Editor modifications

### Preparing the editor

Editor modifications are based on unpacked Cobalt code from the BitSquid version of the game located in `7efe746cbba01385`.  

For that you will need:  

> [bitsquid_unp](https://web.archive.org/web/20221018164344/https://zenhax.com/download/file.php?id=959&sid=b46f061347c43223468aa896550bd9eb) (internet archive download)  
> [luajit-decompiler-v2](https://github.com/marsinator358/luajit-decompiler-v2) (github repo)  
> [truncate_bytes.py](/truncate_bytes.py) (this repo)  
> [rename_bitsquid.py](/rename_bitsquid.py) (this repo)  
> [python 3](https://www.python.org/downloads/) (can be downloaded here)  

#### Getting decompiled lua source

- First step is unpacking `7efe746cbba01385` done by running `bitsquid_unp.exe`:  
```
bitsquid_unp.exe [path to cobalt steam directory (browse files for cobalt in steam) bundle/7efe746cbba01385]
```
This results in the unpacked lua bytecode files being places where `bitsquid_unp.exe` was run from.  
- Second step is removing the trailing 8 bytes from all lua bytecode files and can be done using `truncate_bytes.py` like so:
```
python truncate_bytes.py -t [path to unpacked 7efe746cbba01385]
```
The script changes the files on the spot so any required backups/files should be copied somwhere else before executing, it also strips leading bytes from all files ending with .lua so tread carefully and execute only once!  
- Third step is decompiling the bytecode using `luajit-decompiler-v2.exe` like so:
```
luajit-decompiler-v2.exe [path to unpacked and truncated files]
```
Decompiler creates a folder called `output` for the output files and leaves the input files alone, any files that threw errors while decompiling can be copied from the `daisyMoon` folder within a downloaded cobalt steam repo aquired via running the following command within the steam console:  
```
download_depot 357340 357342 4393965309640351424
```
- Forth step is running `rename_bitsquid.py` over the files to regain the required virtual folder structure like so:  
```
python rename_bitsquid.py -s [path to output folder from step 3 / output folder from luajit-decompiler-v2.exe] -t [path to new output folder]
```
The specified folder should contain all files that were sucessfully decompiled, the before mentioned files that failed thecompiling and any other desired files should be copied into this folder and subfolders.  

#### Running the editor using lua source
First either make a copy of cobalt just for running a modified editor or backup your cobalt files.  
Open the desired cobalt's files and copy the contents of cobalt's source `daisyMoon` directory into the desired cobalt's one.  
Run the desired cobalt's `cobaltDM.exe` through steam as a non-steam game.  
Optionally create `steam_appid.txt` in the desired cobalt's directory, the created file should look like this:  
```
357340
```

### Alloy
#### Installing
All files required to run alloy are provided [here](/alloy).  
- `eng.translations` go into the `translations` folder  
- `alloy_editor_mod_xx.diff` is applied over a prepared `daisyMoon` folder (using a copy of cobalt is strongly recomended)  
For linux apply `alloy_editor_mod_x_x_x.diff` by executing the following command in the desired cobalt's folder:
```
patch -p0 < [path to alloy_editor_mod_x_x_x.diff]
```
After attempting to save an alloy for the first time the game should automatically create a folder called `alloys` within its directory, put any desired alloys there, the menus should explain the rest.  
#### Quickmenu
Columns still work as before, the top row is accesed without any modifiers, the second row is accesed while holding `CTRL`.
