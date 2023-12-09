# Alloy

Alloy is a modding toolkit for Cobalt, built to be as unrestrictive as possible.

Using Alloy, modders create "alloys", which can change how the game behaves, add new items, weapons or expand the game to their heart's content, all using an in-game editor and lua scripting.

## Installation

### Preparing the editor

Alloy is based on unpacked Cobalt source code from the BitSquid version of the game, located in `7efe746cbba01385`.  

To prepare the editor, you will need:  

> [Bitsquid unpacker (bitsquid_unp)](https://web.archive.org/web/20221018164344/https://zenhax.com/download/file.php?id=959&sid=b46f061347c43223468aa896550bd9eb) (internet archive download)  
> [Lua JIT decompiler (luajit-decompiler-v2)](https://github.com/marsinator358/luajit-decompiler-v2) (github repo)  
> [truncate_bytes.py](/truncate_bytes.py) (this repo)  
> [rename_bitsquid.py](/rename_bitsquid.py) (this repo)  
> [Python 3](https://www.python.org/downloads/)

#### Getting decompiled lua source
##### Option 1: Download from the Cobalt archive
If you don't want to locally decompile, a version of the decompiled source can be found at the [Cobalt archive Google drive folder](https://drive.google.com/drive/folders/10Tw1c530qnA5l3P6u1jRyzI9fa3sEWz5?usp=drive_link)

##### Option 2: Unpacking and decompiling locally

The first step is unpacking `7efe746cbba01385`, using `bitsquid_unp.exe`:  
```
bitsquid_unp.exe [path to cobalt steam directory (browse files for cobalt in steam) bundle/7efe746cbba01385]
```

This unpacks the lua bytecode into the same folder `bitsquid_unp.exe` was ran.

Next, we need to remove 8 trailing bytes from all lua bytecode files using `truncate_bytes.py`:
```
python3 truncate_bytes.py -t [path to unpacked 7efe746cbba01385]
```

**The script changes files on the spot, so any required backups/files should be copied somwhere else before executing.**

**It also strips leading bytes from all .lua files, so tread carefully and execute only once!**
 
Next, we will decompile the bytecode using `luajit-decompiler-v2.exe`:

```
luajit-decompiler-v2.exe [path to unpacked and truncated files]
```

The decompiler creates a folder called `output` for the output files and leaves the input files alone.

Any files that threw errors while decompiling can be copied from the `daisyMoon` folder of a downloaded Cobalt steam depot, acquired by running the following command within the steam console:  

```
download_depot 357340 357342 4393965309640351424
```

- The last step is running `rename_bitsquid.py` over the files to regain the required virtual folder structure:
  
```
python3 rename_bitsquid.py -s [path to output folder from step 3 / output folder from luajit-decompiler-v2.exe] -t [path to new output folder]
```

The specified folder should now contain all sucessfully decompiled files, the before mentioned files that failed to decompile and any other desired files should now be copied into this folder and its subfolders.  

#### Running the editor using lua source code
First, either make a copy of Cobalt just for running the modified editor, or backup your game files.  

Next, copy the contents of the source code's `daisyMoon` folder into the target Cobalt's `daisyMoon` folder.  

Lastly, create `steam_appid.txt` in the target Cobalt's game files:

```
357340
```

Now you can run the target Cobalt's `cobaltDM.exe` through Steam as a non-steam game.  

### Installing Alloy

All files required to run Alloy are provided in [the alloy folder](/alloy).

To install them:

- Copy `eng.translations` into the game's `translations` folder,

- Apply `alloy_editor_mod_xx.diff` over a prepared `daisyMoon` folder

#### Applying diffs

##### Linux

On linux systems, apply `alloy_editor_mod_x_x_x.diff` by executing the following command in the target Cobalt's root game directory:

```
patch -p0 < [path to alloy_editor_mod_x_x_x.diff]
```

If the previous command returns different line ending errors, execute this:  

```
find daisyMoon/ -type f -name '*.lua' -exec dos2unix '{}' +
```

and rerun the patch command.

## Usage

### alloys folder

After attempting to save an alloy for the first time, the game should automatically create a folder called `alloys` within its directory;

Alloys are saved to and loaded from that folder.

### Quickmenu

Columns still work as before, the top row is accesed without any modifiers, the second row is accesed while holding `CTRL`.
