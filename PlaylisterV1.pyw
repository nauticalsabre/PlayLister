import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import *
import shutil
import os

import json

# TODO
# add status bar along bottom
# maybe implement menu bar
# maybe implement a file to store settings to store last paths used > Implimented

program_settings = {}

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("1280x768")
        self.title("Clone Hero Playlist Manager")
		
        global program_settings
        try:
            with open("settings.json", "r") as settings_file:
                program_settings = json.load(settings_file)
        except FileNotFoundError:
            print("No settings file found")

        
        self.path_current_songs           = tk.StringVar()
        self.path_current_songs.set(program_settings["current_path"])
        self.path_available_songs         = tk.StringVar()
        self.path_available_songs.set(program_settings["available_path"])
        
        self.current_song_list = []
        self.current_song_list_pending = []
        self.available_song_list = []
        self.available_song_list_pending = []

        self.sort_current_artist_alpha = True
        self.sort_current_name_alpha = True
        self.sort_available_artist_alpha = True
        self.sort_available_name_alpha = True

        self.bind("<Return>", self.CommitChanges)
        self.bind('a', self.AddSong)
        self.bind('r', self.RemoveSong)

        # Create Frames
        self.frame_main               = Frame(self)
        self.frame_current_songlist   = Frame(self.frame_main, padding=10)
        self.frame_available_songlist = Frame(self.frame_main, padding=10)
        
        # Create buttons
        self.button_add            = Button(self.frame_available_songlist, text="Add", command=self.AddSong, underline=0)
        self.button_remove         = Button(self.frame_current_songlist, text="Remove", command=self.RemoveSong, underline=1)
        self.button_set_default_current = Button(self.frame_current_songlist, command=lambda: self.SetCurrentSongPathDefault(self.path_current_songs.get()), text="Default Path")
        self.button_set_default_current["state"] = "disabled"
        self.button_set_default_available = Button(self.frame_available_songlist, command=lambda: self.SetAvailablePathDefault(self.path_available_songs.get()), text="Default Path")
        self.button_set_default_available["state"] = "disabled"
        self.button_open_available = Button(self.frame_available_songlist, text="Open selected song folder(s)", command=self.OpenSelectedAvailableFolders)
        self.button_open_current   = Button(self.frame_current_songlist, text="Open selected song folder(s)", command=self.OpenSelectedCurrentFolders)
		

        # Current Treeview setup
        self.treeview_current_songlist = Treeview(self.frame_current_songlist)
        self.scrollbar_treeview_current_songlist = Scrollbar(self.frame_current_songlist, orient="vertical")  # create scrollbar widget for treeview
        self.treeview_current_songlist["columns"] = ["artist", "name"]
        self.treeview_current_songlist.column("#0", width=20, stretch=False)
        self.treeview_current_songlist.heading("artist", text="Artist", command=self.Sort_CurrentTreeview_Artist)
        self.treeview_current_songlist.heading("name", text="Name", command=self.Sort_CurrentTreeview_Name)
        self.treeview_current_songlist.tag_configure("parent_top", background="#809EC2", foreground="white")
        self.treeview_current_songlist.tag_configure("parent_pending", background="#ABABAB", foreground="white")
        self.treeview_current_songlist.tag_configure("odd_row", background="#EBF2F5", foreground="black")
        self.treeview_current_songlist.tag_configure("pending_odd_row", background="#E8E8E8", foreground="black")
        # Link treeview_current scroll with treeview_scrollbar position
        self.treeview_current_songlist.configure(yscrollcommand=self.scrollbar_treeview_current_songlist.set)  # connect y position of treeview to scrollbar
        self.scrollbar_treeview_current_songlist.configure(command=self.treeview_current_songlist.yview)  # connect scrollbar position to treeview y position
        # Info for Current Treeview
        self.label_current_songs_path     = Label(self.frame_current_songlist, textvariable=self.path_current_songs)
        self.label_current_songs_path.bind("<Button-1>", self.ChangeCurrentSongsPath)

        self.current_base_entry = self.treeview_current_songlist.insert(parent="", index="end", iid=0, values=("Currently Added - 0",), open=True, tags=("parent_top"))
        self.current_pending_entry = self.treeview_current_songlist.insert(parent="", index="end", iid=1, values=("Pending",), open=True, tags=("parent_pending"))
        

        # Available Treeview setup
        self.treeview_available_songlist = Treeview(self.frame_available_songlist)
        self.scrollbar_treeview_available_songlist = Scrollbar(self.frame_available_songlist, orient="vertical")  # create scrollbar widget for treeview
        self.treeview_available_songlist["columns"] = ["artist", "name"]
        self.treeview_available_songlist.column("#0", width=20, stretch=False)
        self.treeview_available_songlist.heading("artist", text="Artist", command=self.Sort_AvailableTreeview_Artist)
        self.treeview_available_songlist.heading("name", text="Name", command=self.Sort_AvailableTreeview_Name)
        self.treeview_available_songlist.tag_configure("parent_top", background="#C27E7F", foreground="white")
        self.treeview_available_songlist.tag_configure("parent_pending", background="#ABABAB", foreground="white")
        self.treeview_available_songlist.tag_configure("odd_row", background="#F5EAEB", foreground="black")
        self.treeview_available_songlist.tag_configure("pending_odd_row", background="#E8E8E8", foreground="black")
        # Link treeview_available scroll with treeview_scrollbar position
        self.treeview_available_songlist.configure(yscrollcommand=self.scrollbar_treeview_available_songlist.set)  # connect y position of treeview to scrollbar
        self.scrollbar_treeview_available_songlist.configure(command=self.treeview_available_songlist.yview)  # connect scrollbar position to treeview y position
        # Info for available Treeview
        self.labelvar_total_available_songs = tk.StringVar()
        self.label_available_song_path      = Label(self.frame_available_songlist, textvariable=self.path_available_songs)
        self.label_available_song_path.bind("<Button-1>", self.ChangeAvailableSongsPath)

        self.available_base_entry = self.treeview_available_songlist.insert(parent="", index="end", iid=0, values=("Currently Available",), open=True, tags=("parent_top"))
        self.available_pending_entry = self.treeview_available_songlist.insert(parent="", index="end", iid=1, values=("Pending",), open=True, tags=("parent_pending"))


        

        # Pack widgets into their frames
        # setup treeview_current and it's button's grid
        self.button_set_default_current.grid(column=1, row=0, sticky="e", pady=5, ipadx=10)
        self.label_current_songs_path.grid(column=0, row=0, sticky="w")
        self.treeview_current_songlist.grid(column=0, row=1, sticky="news", columnspan=2)
        self.scrollbar_treeview_current_songlist.grid(column=2, row=1, sticky="ns")
        self.button_remove.grid(column=0, row=2, sticky="ew", pady=5, padx=5)
        self.button_open_current.grid(column=1, row=2, sticky="ew", pady=5, padx=5)

        # Configure frame_current grid weights
        self.frame_current_songlist.rowconfigure(0, weight=1)
        self.frame_current_songlist.rowconfigure(1, weight=100)
        self.frame_current_songlist.rowconfigure(2, weight=1)
        self.frame_current_songlist.columnconfigure(0, weight=10)
        self.frame_current_songlist.columnconfigure(1, weight=10)
        self.frame_current_songlist.columnconfigure(2, weight=1)

        # setup treeview_available and it's button's grid
        self.button_set_default_available.grid(column=1, row=0, sticky="e", pady=5, ipadx=10)
        self.label_available_song_path.grid(column=0, row=0, sticky="w")
        self.treeview_available_songlist.grid(column=0, row=1, columnspan=2, sticky="news")
        self.scrollbar_treeview_available_songlist.grid(column=2, row=1, sticky="ns")
        self.button_add.grid(column=0, row=2, sticky="ew", pady=5, padx=5)
        self.button_open_available.grid(column=1, row=2, sticky="ew", pady=5, padx=5)
        # Configure frame_available grid weights
        self.frame_available_songlist.rowconfigure(0, weight=1)
        self.frame_available_songlist.rowconfigure(1, weight=100)
        self.frame_available_songlist.rowconfigure(2, weight=1)
        self.frame_available_songlist.columnconfigure(0, weight=10)
        self.frame_available_songlist.columnconfigure(1, weight=10)
        self.frame_available_songlist.columnconfigure(2, weight=1)

        # Pack frames into window
        self.frame_main.grid(column=0, row=0, sticky="news")
        self.frame_current_songlist.grid(column=0, row=1, sticky="news", padx=10, pady=10)
        self.frame_available_songlist.grid(column=1, row=1, sticky="news", padx=10, pady=10)

        # Configure app's grid weights
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        # Configure frame_main's grid weights
        self.frame_main.rowconfigure(0, weight=1)
        self.frame_main.rowconfigure(1, weight=100)
        self.frame_main.columnconfigure(0, weight=1)
        self.frame_main.columnconfigure(1, weight=1)
		
        self.Update_CurrentSongList_FromDirectory()
        self.Update_AvailableSongList_FromDirectory()
	
        self.Update_CurrentSongList_Entries()
        self.Update_AvailableSongList_Entries()

    

    def CommitChanges(self, event):
        #print("commiting changes")
        # go through pending list of songs to add to the game, moving the folders over.
        for item in self.current_song_list_pending:
            print(item[2])
            shutil.move(self.path_available_songs.get() + "//" + item[2], self.path_current_songs.get())
            self.current_song_list.append(item)
        self.current_song_list_pending = []
        self.Update_CurrentSongList_Entries()

        for item in self.available_song_list_pending:
            shutil.move(self.path_current_songs.get() + "//" + item[2], self.path_available_songs.get())
            self.available_song_list.append(item)
        self.available_song_list_pending = []
        self.Update_AvailableSongList_Entries()



    def Update_CurrentSongList_Entries(self):
        for entry in self.treeview_current_songlist.get_children(self.current_base_entry):
            self.treeview_current_songlist.delete(entry)
        for entry in self.treeview_current_songlist.get_children(self.current_pending_entry):
            self.treeview_current_songlist.delete(entry)
 
        for song_info in self.current_song_list:
            self.treeview_current_songlist.insert(self.current_base_entry, index="end", values=song_info, tags=(("odd_row") if self.current_song_list.index(song_info) % 2 == 0 else ()))
        self.treeview_current_songlist.item(0, values=("Currently Added - " + str(len(self.treeview_current_songlist.get_children(self.current_base_entry))),))
        
        for song_info in self.current_song_list_pending:
            self.treeview_current_songlist.insert(self.current_pending_entry, index="end", values=song_info, tags=(("pending_odd_row") if self.current_song_list_pending.index(song_info) % 2 == 0 else ()))
        self.treeview_current_songlist.item(1, values=("Pending - " + str(len(self.treeview_current_songlist.get_children(self.current_pending_entry))),))
        

    def Update_AvailableSongList_Entries(self):
        for entry in self.treeview_available_songlist.get_children(self.available_base_entry):
            self.treeview_available_songlist.delete(entry)
        for entry in self.treeview_available_songlist.get_children(self.available_pending_entry):
            self.treeview_available_songlist.delete(entry)

        for song_info in self.available_song_list:
            self.treeview_available_songlist.insert(self.available_base_entry, index="end", values=song_info, tags=(("odd_row") if self.available_song_list.index(song_info) % 2 == 0 else ()))
        self.treeview_available_songlist.item(0, values=("Currently Available - " + str(len(self.treeview_available_songlist.get_children(self.available_base_entry))),))

        for song_info in self.available_song_list_pending:
            self.treeview_available_songlist.insert(self.available_pending_entry, index="end", values=song_info, tags=(("pending_odd_row") if self.available_song_list_pending.index(song_info) % 2 == 0 else ()))
        self.treeview_available_songlist.item(1, values=("Pending - " + str(len(self.treeview_available_songlist.get_children(self.available_pending_entry))),))


    def Update_CurrentSongList_FromDirectory(self):
        # test getting info from song.ini in each songs folder and separating treeview using it.
        try:
            self.current_playlist_directory = os.listdir(self.path_current_songs.get())
            for folder in self.current_playlist_directory:
                # 1st index contains artist name, 2nd index contains name of song, 3rd index is the folder name in directory
                song_info_to_add_to_tree = ["","",folder]
                # these 2 search term arrays could be changed to regex, if i every learn it like im suppose to
                song_artist_search_terms = ["artist=", "artist = "]
                song_name_search_terms = ["name=", "name = "]
                try:
                    with open(self.path_current_songs.get() + "\\" + folder + "\\song.ini", "r", encoding="utf8") as song_file:
                        try:
                            for line in song_file:
                                if any(art_match in line for art_match in song_artist_search_terms):
                                    song_info_to_add_to_tree[0] = (line.split("=")[1].strip())
                                if any(nam_match in line for nam_match in song_name_search_terms):
                                    song_info_to_add_to_tree[1] = (line.split("=")[1].strip())
                            self.current_song_list.append(song_info_to_add_to_tree)
                        except UnicodeDecodeError:
                            # if we find a song.ini but cant open it, then the file must not be in utf8 format
                            self.current_song_list.append([folder, "--SONG.INI NOT UTF8 ENC--", folder])
                    # if you try to open the folder and cant find a song.ini file, must mean there isn't one or more than likely its just a folder of folders
                except FileNotFoundError:
                    self.current_song_list.append([folder, "--MULTIPLE NESTED FOLDERS--", folder])
        except FileNotFoundError:
            print("Tried searching Directory for Current Songs-Invalid Path")

    def Update_AvailableSongList_FromDirectory(self):
        try:
            self.available_playlist_directory = os.listdir(self.path_available_songs.get())
            for folder in self.available_playlist_directory:
                song_info_to_add_to_tree = ["","",folder]
                song_artist_search_terms = ["artist=", "artist = "]
                song_name_search_terms = ["name=", "name = "]
                try:
                    with open(self.path_available_songs.get() + "\\" + folder + "\\song.ini", "r", encoding="utf8") as song_file:
                        try:
                            for line in song_file:
                                if any(art_match in line for art_match in song_artist_search_terms):
                                    song_info_to_add_to_tree[0] = (line.split("=")[1].strip())
                                if any(nam_match in line for nam_match in song_name_search_terms):
                                    song_info_to_add_to_tree[1] = (line.split("=")[1].strip())
                            self.available_song_list.append(song_info_to_add_to_tree)
                        except UnicodeDecodeError:
                            self.available_song_list.append([folder, "--SONG.INI NOT UTF8 ENC--", folder])
                except FileNotFoundError:
                    self.available_song_list.append([folder, "--MULTIPLE NESTED FOLDERS--", folder])
        except FileNotFoundError:
            print("Tried searching Directory for Available Songs-Invalid Path")


    def AddSong(self, _event=None):
        items_selected = [list(self.treeview_available_songlist.item(i, "values")) for i in self.treeview_available_songlist.selection()]

        if len(items_selected) != 0:
            for item in items_selected:
                if item in self.available_song_list:
                    self.current_song_list_pending.append(item)
                    self.available_song_list.remove(item)
                else:
                    self.current_song_list.append(item)
                    self.available_song_list_pending.remove(item)
        
            self.Update_CurrentSongList_Entries()
            self.Update_AvailableSongList_Entries()
    
    def RemoveSong(self, _event=None):
        items_selected = [list(self.treeview_current_songlist.item(i, "values")) for i in self.treeview_current_songlist.selection()]

        if len(items_selected) != 0:
            for item in items_selected:
                if item in self.current_song_list:
                    self.available_song_list_pending.append(item)
                    self.current_song_list.remove(item)
                else:
                    self.available_song_list.append(item)
                    self.current_song_list_pending.remove(item)
            
            self.Update_CurrentSongList_Entries()
            self.Update_AvailableSongList_Entries()
        

    def OpenSelectedAvailableFolders(self):
        items_selected_available_treeview = [self.treeview_available_songlist.item(i) for i in self.treeview_available_songlist.selection()]

        if len(items_selected_available_treeview) != 0:
            for item in items_selected_available_treeview:
                os.startfile(self.path_available_songs.get() + "\\" + item['values'][2])
    
    def OpenSelectedCurrentFolders(self):
        items_selected_current_treeview = [self.treeview_current_songlist.item(i) for i in self.treeview_current_songlist.selection()]

        if len(items_selected_current_treeview) != 0:
            for item in items_selected_current_treeview:
                os.startfile(self.path_current_songs.get() + "\\" + item['values'][2])


    def ChangeCurrentSongsPath(self, event):
        new_path = filedialog.askdirectory()

        if new_path != "":
            self.button_set_default_current["state"] = "enabled"
            self.button_set_default_current["text"] = "Set Default Path"
            self.current_song_list = []
            self.current_song_list_pending = []
            self.path_current_songs.set(new_path)
            self.Update_CurrentSongList_FromDirectory()
            self.Update_CurrentSongList_Entries()
			
    def SetCurrentSongPathDefault(self, path):
        self.button_set_default_current["state"] = "disabled"
        self.button_set_default_current["text"] = "Default Path"
        program_settings["current_path"] = path
        with open("settings.json", "w") as settings_file:
            json.dump(program_settings, settings_file, indent=4)
    
    def ChangeAvailableSongsPath(self, event):
        new_path = filedialog.askdirectory()

        if new_path != "":
            self.button_set_default_available["state"] = "enabled"
            self.button_set_default_available["text"] = "Set Default Path"
            self.available_song_list = []
            self.available_song_list_pending = []
            self.path_available_songs.set(new_path)
            self.Update_AvailableSongList_FromDirectory()
            self.Update_AvailableSongList_Entries()

    def SetAvailablePathDefault(self, path):
        self.button_set_default_available["state"] = "disabled"
        self.button_set_default_available["text"] = "Default Path"
        program_settings["available_path"] = path
        with open("settings.json", "w") as settings_file:
            json.dump(program_settings, settings_file, indent=4)


    def Sort_CurrentTreeview_Artist(self):
        if self.sort_current_artist_alpha:
            self.current_song_list.sort(key=lambda key: key[0])
            self.sort_current_artist_alpha = False
        else:
            self.current_song_list.sort(key=lambda key: key[0], reverse=True)
            self.sort_current_artist_alpha = True

        self.Update_CurrentSongList_Entries()
    
    def Sort_CurrentTreeview_Name(self):
        if self.sort_current_name_alpha:
            self.current_song_list.sort(key=lambda key: key[1])
            self.sort_current_name_alpha = False
        else:
            self.current_song_list.sort(key=lambda key: key[1], reverse=True)
            self.sort_current_name_alpha = True

        self.Update_CurrentSongList_Entries()

    def Sort_AvailableTreeview_Artist(self):
        if self.sort_available_artist_alpha:
            self.available_song_list.sort(key=lambda key: key[0])
            self.sort_available_artist_alpha = False
        else:
            self.available_song_list.sort(key=lambda key: key[0], reverse=True)
            self.sort_available_artist_alpha = True

        self.Update_AvailableSongList_Entries()
    
    def Sort_AvailableTreeview_Name(self):
        if self.sort_available_name_alpha:
            self.available_song_list.sort(key=lambda key: key[1])
            self.sort_available_name_alpha = False
        else:
            self.available_song_list.sort(key=lambda key: key[1], reverse=True)
            self.sort_available_name_alpha = True

        self.Update_AvailableSongList_Entries()


if __name__ == "__main__":
    app = App()
    app.mainloop()
