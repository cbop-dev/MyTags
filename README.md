MyTags
========
This is a set of tools, mostly in python, providing basic functionality for a tagging files in a cross-platform way that is compatible with [TagSpaces](http://tagspaces.org) "sidecar" metafiles. A file's (or folder's) tags are stored in a JSON "sidecar" metafile in the .ts directory of the file's (or folder's) parent directory; each file's metafile has the same name as its originating file with an appended ".json" extension. This is being developed on Linux (Mint versions 18.1, 19.1/1/2, and 20 have all been tested), but with the hopes that it could be (eventually) usable across platforms.

This project can also be integrated with the Nemo file manager (tested with versions 3.2.2 up to 4.6.4), using the nemo-python package to extend it (`mytags-nemo-extension.py` goes into `~/.local/share/nemo-python/extensions`, and the `src` directory must be in your `PYTHONPATH` environment variable; more info below).  Some basic integration with the Recoll engine and tmsu is also implemented. (See installation instructions below.)

This is a functioning system (I've used it for more than 2 years for organizing files), but it is also a work in progress! 

Demo:
-------------------------
![MyTags Nemo Extension screenshot1](https://github.com/cbop-dev/MyTags/blob/master/images/menu.gif "MyTags Nemo Extension capture 1")

![MyTags Nemo Extension screenshot2](https://github.com/cbop-dev/MyTags/blob/master/images/addremove.gif "MyTags Nemo Extension capture 2")


UPDATE HISTORY:
---------------

**Version 0.5:**

* initial port to Python3

**Version 0.4.1:**

* Now handles symbolic links
* Nemo extension additions:
   - `Files`->`Index` action: Re-indexes selected files.
   - `Config` option: Opens `config.py` file in editor.

**Version 0.4** 

* Basic tmsu tool integegration (config options in 'config' module)
* Consolidated config options in config module (`src/mytags/config.py`). You must also edit the few options in `mytags-nemo-extension` module (found in the `src/mytags/nemo` directory, but which goes into your nemo extensions folder as described below).

**Version 0.3.1:**

* Nemo extension functions for tags (add/remove-some/remove-all/replace) and files (copy, move, rename, delete) and on background (clean meta-folder).  The interface is fairly basic, without giving additional options. 
* The python library (`mytags.MyTagsUtils`) is what does the file-tagging work and includes the file operations (copy, rename, move, delete) that take sidecar files into account.  
* Simple command-line bash script (using jq) for reading tags from files (`src/mytags/bash/ts-tags`) 
* Recoll file-indexing integration. (See installation instructions below.) 


Requirements:
-------------

* Python 3 (for version 0.5 and later); Python 2.7.x for earlier versions.
* [jq](https://stedolan.github.io/jq/) (Fast JSON parser)
* Python libraries:
  * [Tkinter](https://wiki.python.org/moin/TkInter)
  * [TkTreectrl](http://tkintertreectrl.sourceforge.net)
  * [pyjq](https://pypi.python.org/pypi/pyjq) -- jq binding for python
  * [filelock](https://pypi.python.org/pypi/filelock) for creating lock-files
  * [portalocker](https://pypi.python.org/pypi/portalocker) for file-locking
* For Python extension:
  * Nemo (3.x)
  * nemo-python extension. This may, in turn, require:
    * gnome-pkg-tools
    * python-gi-dev 
    * libnemo-extension-dev
* For indexing, either or both: 
  * [Recoll](https://www.lesbonscomptes.com/recoll) 1.23+. (For `apt-get`, you may need to add `ppa:recoll-backports/recoll-1.15-on` to your repositories [e.g., `sudo add-apt-repository ppa:recoll-backports/recoll-1.15-on`]).
  * [tmsu](https://tmsu.org) (Source code available [here at github](https://github.com/oniony/TMSU). The tmsu binary needs to be in your environment `PATH`.

There may be other requirements that I've overlooked...

Installation
-------------------------

1. Make sure you've met all the requirements above!  
2. Download/clone the repository. 
2. Copy the `src/mytags/nemo/mytags-nemo-extension` to `~/.local/share/nemo-python/extensions` (or create this directory if it does not exist). 
3. Copy the "mytags" folder (found in the "src" directory) to a path where python libraries are stored, or add the `src` folder to your `PYTHONPATH` environment variable before running Nemo (e.g, in Bash: `env PYTHONPATH=$PYTHONPATH:/home/user/git/MyTags/src` nemo). OR, edit the top of `mytags-nemo-extension.py` and set the python path as mentioned in the comments.
4. For Recoll integration (optional):
   * You must have Recoll installed and setup, and a index already configured. (See https://www.lesbonscomptes.com/recoll)
   * Edit `src/mytags/config.py` and set recoll to True and recoll_config to point to your Recoll config diretory, eg., `/home/user/.recoll`.
   * Copy the `src/mytags/bash/ts-tags` script to somewhere on your system path (e.g., `/usr/local/bin`) so it will be read by the recollindex engine.
   * Make sure to either set the `PYTHONPATH` variable points to the `mytags/src` directory for your Nemo session, or set the path manually at the top of `mytags-nemo-extension.py` (this file goes in your `nemo-python/extensions` folder, e.g., `/home/user/.local/share/nemo-python/extensions`)
   * Configure your recoll index (e.g., edit `~/.recoll/recoll.cfg`) to not index  `.ts/` folders and avoid `.ts` files. (See example in `src/mytags/recoll/`), and a line with the metacmds entry such as this: `metadatacmds = ; tags = ts-tags %f;` (This tells recoll to call the `ts-tags` tools, passing the filename, whenever it indexes a file, and store the results in the `tags` field of the database.)
5. For tmsu:
   * edit `src/mytags/config.py` and set `tmsu` to `True` and `tmsu_db` to point to your tmsu database (e.g., `/home/user/.tmsu/db`).
5. Close all instances of Nemo (`nemo -q`), then run nemo with the correct environment settings (e.g, `env PYTHONPATH="$PYTHONPATH:/home/user/git/MyTags/src`, unless your manually setting the path as in step 3). 
   * For development or debugging, try running Nemo with the `gdb` tool: `env PYTHONPATH="$PYTHONPATH:/home/user/git/MyTags/src gdb nemo`
5. Select one or more files, then right-click, and try the "MyTags" submenus and commands. NB: None of "Tags" commands will change your files themselves; these functions only mess with metafiles in ".ts" folders in the same directory. BUT, the "Files" commands will copy/move/rename your selected files (except rename, which takes 1 file), after prompting your for a directory/name, and make the appropriate changes to the metafiles (and re-index the new files if indexing is turned on in index.py and recoll is configured correctly).


Motivation:
-----------
This project developed out of a desire to have some way to adding arbitrary tags to files in a traditional filesystem, especially for managing large amounts of documents and books, making for easy searching and retrieval. One problem with hierarchical file-systems is that as the number of files/folders grows, it becomes increasingly difficult to organize files that fit into more than one category. Completely reorganizing one's folder system is not always feasible, and it would not help with files that really belong in several folders. Using links (hard or symbolic) creates problems with backing-up and transfering to other drives/systems. 

Some way of "tagging" files would provide a very useful way to handle this problem, though "tagging," non-hierarchical file-systems are either not well-developed, not common, or not the right solution anyway (simply abandoning a hierarchical system may create other problems). Tagging on top of a traditional file-system seems like the most feasible way to go.

And various solutions to tagging files have been developed. TagSpaces provides an intriguing approach (NOT with its free, "let's add tags to the filename" approach which seems like a *really* bad idea; but in its PRO version, with sidecar metafiles, which do not touch the original, "tagged" files). Unfortunately, TagSpaces had created a somewhat cumbersome file-manager that does not handle large files/directories well, nor had it implemented (when the project began) a usable indexing/search feature. (When I tried to search my Documents directory, with  100+ GB of files, the app froze and crashed, because it recursively checked each file/folder for its sidecard file, reading/parsing the contents of this file, and then searched for the search terms!) Why should we have to re-invent the wheel, creating a new file-manager? And why sacrifice efficient searching (which defeats one of the main benefits of having tags in the first place), or start from the ground up with a new search engine? Search engines are often work well with keywords or tags; the problem is, the most-used filesystems do not (yet) have a universal way to handle arbitrary, non-hierarchical tags. These tools are offered in hopes of providing a workable solution to this problem, at least on the Linux platform.

TO-DO:
------
* Indexing: handle deleted files better?
* Further testing/improvements:
  * Nemo extension
  * Recoll indexing integration
* Test on other Linux platforms
* Integrate with Windows? (low priority)



