import UiFile
from tkinter import filedialog
import os
import shutil

# storing song list information
current_song_list = []            # list of songs currently in the game
current_song_list_pending = []    # list of songs to be added to the game on commit
available_song_list = []          # list of songs not in the game but are able to add
available_song_list_pending = []  # list of songs to be removed from the game on commit


"""
Search folder path to setup list of songs currently in the game
"""
def UpdateCurrentSongListFromDirectory():
    global current_song_list
    try:                                                                                                                        # CHECK to make sure the path used is a valid path
        main_window.current_playlist_directory = os.listdir(main_window.path_current_songs.get())                               # get list of folder in directory of the path used
        for folder in main_window.current_playlist_directory:
            song_info_to_add_to_tree = ["","",folder]                                                                           # 1st index contains artist name, 2nd index contains name of song, 3rd index is the folder name in directory
            song_artist_search_terms = ["artist=", "artist = "]                                                                 # 2 terms to look for in songs .ini file to get artist
            song_name_search_terms = ["name=", "name = "]                                                                       # 2 terms to look for in songs .ini file to get name of song
            try:                                                                                                                # CHECK to see if there is a 'song.ini' file in current folder
                with open(f"{main_window.path_current_songs.get()}\{folder}\song.ini", "r", encoding="utf8") as song_file:      # open 'song.ini' file to get information about the songs
                    try:                                                                                                        # CHECK for whether we can read the song.ini file in given format (utf8)
                        for line in song_file:                                                                                  # read lines of file for wanted search terms
                            if any(art_match in line for art_match in song_artist_search_terms):                                # check for artist value
                                song_info_to_add_to_tree[0] = (line.split("=")[1].strip())                                      # if found store artist value
                            if any(nam_match in line for nam_match in song_name_search_terms):                                  # check for name value
                                song_info_to_add_to_tree[1] = (line.split("=")[1].strip())                                      # if found store name value
                        current_song_list.append(song_info_to_add_to_tree)                                                      # add created list of artist/name/folder path to song list
                    except UnicodeDecodeError:                                                                                  # if we find a song.ini but cant open it, then the file must not be in utf8 format
                        current_song_list.append([folder, "--SONG.INI NOT UTF8 ENC--", folder])
            except FileNotFoundError:                                                                                           # if you try to open the folder and cant find a song.ini file, must mean there isn't one or more than likely its just a folder of folders
                current_song_list.append([folder, "--MULTIPLE NESTED FOLDERS--", folder])
    except FileNotFoundError:                                                                                                   # invalid path and wasnt able to start search of folders
        print("Tried searching Directory for Current Songs-Invalid Path")

"""
Update nodes in current treeview to be in line with song lists
"""
def UpdateCurrentSongListEntries():
    global current_song_list, current_song_list_pending
    for entry in main_window.treeview_current_songlist.get_children(main_window.current_base_entry):      # delete all nodes under parent node for current songs
        main_window.treeview_current_songlist.delete(entry)
    for entry in main_window.treeview_current_songlist.get_children(main_window.current_pending_entry):   # delete all nodes under parent node for pending songs
        main_window.treeview_current_songlist.delete(entry)
    # loop through list of current songs/add nodes/set color scheme of nodes
    for song_info in current_song_list:
        main_window.treeview_current_songlist.insert(main_window.current_base_entry, index="end", values=song_info, tags=(("odd_row") if current_song_list.index(song_info) % 2 == 0 else ()))
    # loop through list of current pending songs/add nodes/set color scheme of nodes
    for song_info in current_song_list_pending:
        main_window.treeview_current_songlist.insert(main_window.current_pending_entry, index="end", values=song_info, tags=(("pending_odd_row") if current_song_list_pending.index(song_info) % 2 == 0 else ()))
    
    UpdateStatusBarInfo()

"""
let user change path to search for songs currently in the game
"""   
def ChangeCurrentSongsPath(_event=None):
    global current_song_list, current_song_list_pending
    new_path = filedialog.askdirectory()              # create dialog window which allows choosing new path to folder

    if new_path != "":                                # make sure the path is valid. can be invalid if user just closes filedialog window without choosing a folder
        current_song_list = []                        # wipe list of current songs
        current_song_list_pending = []                # wipe pending list of current songs
        main_window.path_current_songs.set(new_path)  # set new path to current songs
        UpdateCurrentSongListFromDirectory()          # update list of song folders/treeview nodes
        UpdateCurrentSongListEntries()

"""
opens windows explorer to songs selected in current list of songs/ up to 5, just so you don't accidently open hundreds of windows explorers
"""
def OpenSelectedCurrentFolders():
    items_selected_current_treeview = [main_window.treeview_current_songlist.item(i) for i in main_window.treeview_current_songlist.selection()]

    if 5 >= len(items_selected_current_treeview) != 0:                                        # check to see if you have between 1 and 5 songs selected
        for item in items_selected_current_treeview:
            os.startfile(f"{main_window.path_current_songs.get()}/{str(item['values'][2])}")  # use songs selected to open window explorers for each song
    else:
        print("May only open between 1 to 5 files at once")



def UpdateAvailableSongListFromDirectory():
    global available_song_list
    try:
        main_window.available_playlist_directory = os.listdir(main_window.path_available_songs.get())
        for folder in main_window.available_playlist_directory:
            song_info_to_add_to_tree = ["","",folder]
            song_artist_search_terms = ["artist=", "artist = "]
            song_name_search_terms = ["name=", "name = "]
            try:
                with open(f"{main_window.path_available_songs.get()}\{folder}\song.ini", "r", encoding="utf8") as song_file:
                    try:
                        for line in song_file:
                            if any(art_match in line for art_match in song_artist_search_terms):
                                song_info_to_add_to_tree[0] = (line.split("=")[1].strip())
                            if any(nam_match in line for nam_match in song_name_search_terms):
                                song_info_to_add_to_tree[1] = (line.split("=")[1].strip())
                        available_song_list.append(song_info_to_add_to_tree)
                    except UnicodeDecodeError:
                        available_song_list.append([folder, "--SONG.INI NOT UTF8 ENC--", folder])
            except FileNotFoundError:
                available_song_list.append([folder, "--MULTIPLE NESTED FOLDERS--", folder])
    except FileNotFoundError:
        print("Tried searching Directory for Available Songs-Invalid Path")

def UpdateAvailableSongListEntries():
    global available_song_list, available_song_list_pending
    for entry in main_window.treeview_available_songlist.get_children(main_window.available_base_entry):
        main_window.treeview_available_songlist.delete(entry)
    for entry in main_window.treeview_available_songlist.get_children(main_window.available_pending_entry):
        main_window.treeview_available_songlist.delete(entry)

    for song_info in available_song_list:
        main_window.treeview_available_songlist.insert(main_window.available_base_entry, index="end", values=song_info, tags=(("odd_row") if available_song_list.index(song_info) % 2 == 0 else ()))

    for song_info in available_song_list_pending:
        main_window.treeview_available_songlist.insert(main_window.available_pending_entry, index="end", values=song_info, tags=(("pending_odd_row") if available_song_list_pending.index(song_info) % 2 == 0 else ()))

    UpdateStatusBarInfo()

def ChangeAvailableSongsPath(_event=None):
    global available_song_list, available_song_list_pending
    new_path = filedialog.askdirectory()

    if new_path != "":
        available_song_list = []
        available_song_list_pending = []
        main_window.path_available_songs.set(new_path)
        UpdateAvailableSongListFromDirectory()
        UpdateAvailableSongListEntries()

def OpenSelectedAvailableFolders():
    items_selected_available_treeview = [main_window.treeview_available_songlist.item(i) for i in main_window.treeview_available_songlist.selection()]

    if 5 >= len(items_selected_available_treeview) != 0:
        for item in items_selected_available_treeview:
            os.startfile(f"{main_window.path_available_songs.get()}/{str(item['values'][2])}")
    else:
        print("May only open between 1 to 5 files at once")

def UpdateStatusBarInfo():
    main_window.status_bar.setText(f"Current/Pending- {len(current_song_list)} | {len(current_song_list_pending)}    Available/Pending- {len(available_song_list)} | {len(available_song_list_pending)}      {'' if (len(current_song_list_pending) + len(available_song_list_pending)) == 0 else 'Press [Enter] to Commit Changes'}")

def AddSong(_event=None):
    global current_song_list, available_song_list, current_song_list_pending, available_song_list_pending
    items_selected = [list(main_window.treeview_available_songlist.item(i, "values")) for i in main_window.treeview_available_songlist.selection()]

    if len(items_selected) != 0 and main_window.path_current_songs.get() != "No Path Selected":
        for item in items_selected:
            if item in available_song_list:
                current_song_list_pending.append(item)
                available_song_list.remove(item)
            else:
                current_song_list.append(item)
                available_song_list_pending.remove(item)
        
        UpdateCurrentSongListEntries()
        UpdateAvailableSongListEntries()
    else:
        main_window.status_bar.setText("No valid path to current song list")

def RemoveSong(_event=None):
    global current_song_list, available_song_list, current_song_list_pending, available_song_list_pending
    items_selected = [list(main_window.treeview_current_songlist.item(i, "values")) for i in main_window.treeview_current_songlist.selection()]

    if len(items_selected) != 0 and main_window.path_available_songs.get() != "No Path Selected":
        for item in items_selected:
            if item in current_song_list:
                available_song_list_pending.append(item)
                current_song_list.remove(item)
            else:
                available_song_list.append(item)
                current_song_list_pending.remove(item)
            
        UpdateCurrentSongListEntries()
        UpdateAvailableSongListEntries()
    else:
        main_window.status_bar.setText("No valid path to available song list")

def SortCurrentTreeviewArtist():
    global current_song_list
    if main_window.sort_current_artist_alpha:
        current_song_list.sort(key=lambda key: key[0])
        main_window.sort_current_artist_alpha = False
    else:
        current_song_list.sort(key=lambda key: key[0], reverse=True)
        main_window.sort_current_artist_alpha = True
    UpdateCurrentSongListEntries()
    
def SortCurrentTreeviewNName():
    global current_song_list
    if main_window.sort_current_name_alpha:
        current_song_list.sort(key=lambda key: key[1])
        main_window.sort_current_name_alpha = False
    else:
        current_song_list.sort(key=lambda key: key[1], reverse=True)
        main_window.sort_current_name_alpha = True
    UpdateCurrentSongListEntries()

def SortAvailableTreeviewArtist():
    global available_song_list
    if main_window.sort_available_artist_alpha:
        available_song_list.sort(key=lambda key: key[0])
        main_window.sort_available_artist_alpha = False
    else:
        available_song_list.sort(key=lambda key: key[0], reverse=True)
        main_window.sort_available_artist_alpha = True

    UpdateAvailableSongListEntries()
    
def SortAvailableTreeviewName():
    global available_song_list
    if main_window.sort_available_name_alpha:
        available_song_list.sort(key=lambda key: key[1])
        main_window.sort_available_name_alpha = False
    else:
        available_song_list.sort(key=lambda key: key[1], reverse=True)
        main_window.sort_available_name_alpha = True

    UpdateAvailableSongListEntries()


def CommitChanges(_event=None):
    global current_song_list, current_song_list_pending, available_song_list, available_song_list_pending
    for item in current_song_list_pending:
        shutil.move(main_window.path_available_songs.get() + "\\" + item[2], main_window.path_current_songs.get())
        current_song_list.append(item)
    current_song_list_pending = []
    UpdateCurrentSongListEntries()

    for item in available_song_list_pending:
        shutil.move(main_window.path_current_songs.get() + "\\" + item[2], main_window.path_available_songs.get())
        available_song_list.append(item)
    available_song_list_pending = []
    UpdateAvailableSongListEntries()



if __name__ == "__main__":
    main_window = UiFile.App() # create tk app to setup window

    # this section binds event of the elements from the ui file to the functions in  the logic file (this file)
    main_window.label_current_songs_path.bind("<Button-1>", ChangeCurrentSongsPath)                   # clicking on the path string will allow changing the current path
    main_window.label_available_song_path.bind("<Button-1>", ChangeAvailableSongsPath)                # clicking on the path string will allow changing the available path

    main_window.bind("<Return>", CommitChanges)                                                       # no button for commiting changes to playlists. so pressing enter fills the void

    main_window.button_remove.configure(command=RemoveSong)
    main_window.button_open_current.configure(command=OpenSelectedCurrentFolders)
    main_window.button_open_available.configure(command=OpenSelectedAvailableFolders)
    main_window.treeview_current_songlist.heading("artist", command=SortCurrentTreeviewArtist)
    main_window.treeview_current_songlist.heading("name", command=SortCurrentTreeviewNName)

    main_window.treeview_available_songlist.heading("artist", command=SortAvailableTreeviewArtist)
    main_window.treeview_available_songlist.heading("name", command=SortAvailableTreeviewName)

    main_window.mainloop() # run the app's mainloop to allow the window to update and process events