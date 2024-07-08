# PlayLister

  Got tired of manually going through my Clone Hero game folders to remove songs or read songs.
Created this little python program to allow me to on the fly while playing to just remove or read songs.
Uses Tkinter for GUI.

## 2 files
- PlayLister.pyw
- settings.json

settings.json stores the starting directories for where you want to store unused songs not in the game, and
the current directory holding songs in the game. These paths can be either changed in the file by just providing 
the paths or clicking on the text to openwindows file brower for folder selection.

---

# How to Use

  If python is installed just double-click the PlayLister.pyw. The program uses built in Python libraries for
GUI, and file operations. The program will launch with no paths used. To change the path to the folder containing
the songs in-game or the songs you don't want. Just click the text above each treeview to launch a windows file
browser. The left treeview is for songs in the game, while the right is for songs stored outside of it. To save
the chosen path to always be used on relaunch just __click set default__

- if you want to quickly browse to a selected songs file location just select it/them and use __open file location__.

- When you add/remove a song it is placed in it's respected pending list at the bottom. Pressing __enter__ will commit
the transfers and clear the pending list.

- You can organize treeview columns alphabetically by clicking on column headers.

> [!WARNING]
> Make sure you are not hovering over a song you want to move in-game or it will stall on transfer since the game
> is holding the song file for preview playing.


# Features that should be added

- [ ] Actual button to confirm song transfer
- [ ] Safe guards to move files to not have hiccups when previewing song ingame that needs to be moved
- [ ] Remove formating from song names in treeview for better sorting
