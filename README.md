MyTags
========
This is a set of tools, mostly in python, (eventually) providing basic functionality for a tagging files in a cross-platform way that is compatible with TagSpaces "sidecar" metafiles (http://tagspaces.org). A file's (or folder's) tags are stored in a JSON "sidecar" metafile in the .ts directory of the file's (or folder's) parent directory; each file's metafile has the same name as its originating file with an appended ".json" extension. This is being developed on Linux (Mint 18), but with the hopes that it could be usable across platforms.

I (cbop-dev) hope this project will soon include a functional "Nemo Action" GUI window for use with Linux's Nemo file manager, as well as index/search integration with the Recoll engine (https://www.lesbonscomptes.com/recoll/). 

This is a work in progress! The initial working version, v0.1.0, is now released. It includes python library (mytags.MyTagsUtils), which is then very simply integrated with with only basic functionality ("Add Tags", "Delete Tags") into Nemo as a file option submenu ("My Tags").


Requirements:
-------------
* Python 2.7.x
* jq: https://stedolan.github.io/jq/ (Fast JSON parser)
* Python libraries:
  * Tkinter: https://wiki.python.org/moin/TkInter
  * TkTreectrl: http://tkintertreectrl.sourceforge.net/
  * pyjq: https://pypi.python.org/pypi/pyjq (jq binding for python)
There may be other requirements that I've overlooked...


Motivation:
-----------
This project developed out of a desire to have some way to adding arbitrary tags to files in a traditional filesystem, especially for managing large amounts of documents and books, making for easy searching and retrieval. One problem with hierarchical file-systems is that as the number of files/folders grows, it becomes increasingly difficult to organize files that fit into more than one category. Completely reorganizing one's folder system is not always feasible, and still does not help with files that really belong in several folders. Using links (hard or symbolic) creates problems with backing-up and transfering to other drives/systems. 

Some way of "tagging" files would provide a very useful way to handle this problem, though "tagging," non-hierarchical file-systems are either not well-developed, not common, or not the right solution anyway (simply abandoning a hierarchical system may create other problems). Tagging on top of a traditional file-system seems like the most feasible way to go.

And various solutions to tagging files have been developed. TagSpaces provides an intriguing approach (NOT with its free, "let's add tags to the filename" approach which seems like a really bad idea; but in its PRO version, with sidecar metafiles, which do not touch the original, "tagged" files). Unfortunately, TagSpaces has created a somewhat cumbersome file-manager that does not handle large files/directories well, nor has it implemented a usable indexing/search feature. (When I try to search my Documents directory, with  100+ GB of files, the app freezes and crashes, because it is recursively checking each file/folder for its sidecard file, reading/parsing the contents of this file, and then searching for the search terms!) Why should we have to re-invent the wheel, creating a new file-manager? And why sacrifice efficient searching (which defeats one of the main benefits of having tags in the first place), or start from the ground up with a new search engine? Search engines are often work well with keywords or tags; the problem is, the most-used filesystems do not (yet) have a universal way to handle arbitrary, non-hierarchical tags. These tools are offered in hopes of providing a workable solution to this problem, at least on the Linux platform.

TO-DO:
------
* Basic file management operations that incorporate tags (copy, move, rename, delete).
* More robust Nemo integration functionality
* Recoll indexing integration
* Test on other Linux platforms
* Integrate with Windows?? (low priority)



