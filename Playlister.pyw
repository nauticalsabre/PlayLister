import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import shutil
import platform
import os
import subprocess

import json
import re

app_path = os.path.abspath(__file__)
app_directory = os.path.dirname(app_path)
os.chdir(app_directory)

program_settings = {}

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        print(f"Currently running OS: {platform.system()}")
        self.geometry("1280x768")
        self.title("Clone Hero Playlist Manager")

        self.my_style = ttk.Style()
        self.my_style.configure("Custom.TLabelframe", labeloutside=False, borderwidth=1, font=('Tahoma', 22))
        self.my_style.configure("TLabelframe.Label", font=('Tahoma', 12))
        self.my_style.configure("Search.TRadiobutton", font=("Tahoma", 12, "italic"))
        
        global program_settings
        try:
            with open("settings.json", "r") as settings_file:
                program_settings = json.load(settings_file)
        except FileNotFoundError:
            print("No settings file found, creating new one")
            settings_template = {
                "current_path": "",
                "available_path": "",
                "favourites": []
            }
            with open("settings.json", "w") as settings_file:
                json.dump(settings_template, settings_file, indent=4)
            program_settings = settings_template
            

        self.font_label_bold = ("Tahoma", 12, "bold")
        self.font_standard = ("Tahoma", 12)


        self.search_entry_input = tk.StringVar()
        self.path_current_songs = tk.StringVar()
        self.path_current_songs.set(program_settings["current_path"])
        self.path_available_songs = tk.StringVar()
        self.path_available_songs.set(program_settings["available_path"])

        self.current_song_list           = []
        self.current_song_list_pending   = []
        self.available_song_list         = []
        self.available_song_list_pending = []
        self.search_results              = []

        self.last_sort_category = ""

        # Create Tk Interface
        # Create Frames
        self.frame_treeviews          = ttk.Frame(self)
        self.frame_tools              = ttk.Frame(self, padding=10, relief="raised")
        self.frame_current_songlist   = ttk.LabelFrame(self.frame_treeviews, text="Currently Added Songs", labelanchor="n", relief="flat", style="Custom.TLabelframe")
        self.frame_available_songlist = ttk.LabelFrame(self.frame_treeviews, text="Songs Available to Add", labelanchor="n", relief="flat", style="Custom.TLabelframe")

        # Create TOOLS buttons
        # Setup OPERATION elements
        self.button_commit = ttk.Button(self.frame_tools, text="Commit", command=self.CommitChanges)
        # Setup SEARCH elements
        self.button_search = ttk.Button(self.frame_tools, text="Search", command=lambda: self.SearchSongs(self.Var_search_tree.get(), self.combobox_search_category.get()))
        self.entry_search  = ttk.Entry(self.frame_tools, textvariable=self.search_entry_input, width=40, font=self.font_standard)
        self.search_entry_input.set("Search Songs...")
        self.entry_search.bind("<Button-3>", lambda i: self.search_entry_input.set(""))
        self.combobox_search_category = ttk.Combobox(self.frame_tools, width=10, font=self.font_standard)
        self.combobox_search_category["state"]  = "readonly"
        self.combobox_search_category["values"] = ("artist", "name", "genre")
        self.combobox_search_category.set("name")
        self.Var_search_tree = tk.StringVar(value="current")
        self.radiobutton_current_songs   = ttk.Radiobutton(self.frame_tools, text="Current", variable=self.Var_search_tree, value="current", style="Search.TRadiobutton")
        self.radiobutton_available_songs = ttk.Radiobutton(self.frame_tools, text="Available", variable=self.Var_search_tree, value="available", style="Search.TRadiobutton")
        self.seperator_tools_one = ttk.Separator(self.frame_tools, orient="vertical")
        # setup PATH elements
        self.button_pick_current_path   = ttk.Button(self.frame_tools, text="Set Cur.", command=self.ChangeCurrentSongsPath)
        self.entry_current_song_path    = ttk.Entry(self.frame_tools, textvariable=self.path_current_songs, width=55)
        self.button_set_default_current = ttk.Button(self.frame_tools, command=lambda: self.SetCurrentSongPathDefault(self.path_current_songs.get()), text="Default")
        self.button_pick_available_path = ttk.Button(self.frame_tools, text="Set Avai.", command=self.ChangeAvailableSongsPath)
        self.entry_available_song_path = ttk.Entry(self.frame_tools, textvariable=self.path_available_songs, width=55)
        self.button_set_default_available = ttk.Button(self.frame_tools, command=lambda: self.SetAvailablePathDefault(self.path_available_songs.get()), text="Default")
    

        # Current Songlist TREEVIEW setup
        self.treeview_current_songlist           = ttk.Treeview(self.frame_current_songlist)
        self.scrollbar_treeview_current_songlist = ttk.Scrollbar(self.frame_current_songlist, orient="vertical")  # create scrollbar widget for treeview
        self.button_add                          = ttk.Button(self.frame_available_songlist, text="Add", command=self.AddSong, underline=0)
        self.button_open_current                 = ttk.Button(self.frame_current_songlist, text="Open selected song folder(s)", command=self.OpenSelectedCurrentFolders)
        self.button_favourite                    = ttk.Button(self.frame_current_songlist, text="★", command=self.FavouriteSong)

        self.button_set_default_current["state"]  = "disabled"
        self.treeview_current_songlist["columns"] = ["artist", "name", "genre", "duration", "favourite"]
        self.treeview_current_songlist.column("#0", width=20, stretch=False)
        self.treeview_current_songlist.heading("artist", text="Artist", command=lambda: self.SortTreeview("artist", "current"))
        self.treeview_current_songlist.heading("name", text="Name", command=lambda: self.SortTreeview("name", "current"))
        self.treeview_current_songlist.heading("genre", text="Genre", command=lambda: self.SortTreeview("genre", "current"))
        self.treeview_current_songlist.heading("duration", text="Dur.", command=lambda: self.SortTreeview("length", "current"))
        self.treeview_current_songlist.heading("favourite", text="★", command=lambda: self.SortTreeview("favourite", "current"))
        self.treeview_current_songlist.column("duration", width=10, anchor="center")
        self.treeview_current_songlist.column("favourite", width=5, anchor="center")
        self.treeview_current_songlist.column("genre", width=65)
        self.treeview_current_songlist.column("name", width=165)
        self.treeview_current_songlist.column("artist", width=110)
        self.treeview_current_songlist.tag_configure("parent_top", background="#809EC2", foreground="white")
        self.treeview_current_songlist.tag_configure("parent_pending", background="#ABABAB", foreground="white")
        self.treeview_current_songlist.tag_configure("odd_row", background="#EBF2F5", foreground="black")
        self.treeview_current_songlist.tag_configure("pending_odd_row", background="#E8E8E8", foreground="black")
        self.treeview_current_songlist.tag_configure("search_results", background="#DBBB12", foreground="black")
        self.treeview_current_songlist.tag_configure("search_odd_row", background="#fffdcf", foreground="black")
        # self.treeview_current_songlist.tag_configure("favourite", background="black", foreground="white")
        # Link treeview_current scroll with treeview_scrollbar position
        self.treeview_current_songlist.configure(yscrollcommand=self.scrollbar_treeview_current_songlist.set)  # connect y position of treeview to scrollbar
        self.scrollbar_treeview_current_songlist.configure(command=self.treeview_current_songlist.yview)  # connect scrollbar position to treeview y position
        # Info for Current Treeview
        self.current_base_entry = self.treeview_current_songlist.insert(parent="", index="end", iid=0, values=("Currently Added - 0",), open=True, tags=("parent_top"))
        self.current_pending_entry = self.treeview_current_songlist.insert(parent="", index="end", iid=1, values=("Pending",), open=True, tags=("parent_pending"))

        # Available Songlist Treeview setup
        self.treeview_available_songlist           = ttk.Treeview(self.frame_available_songlist)
        self.scrollbar_treeview_available_songlist = ttk.Scrollbar(self.frame_available_songlist, orient="vertical")  # create scrollbar widget for treeview
        self.button_remove                         = ttk.Button(self.frame_current_songlist, text="Remove", command=self.RemoveSong, underline=1)
        self.button_open_available                 = ttk.Button(self.frame_available_songlist, text="Open selected song folder(s)", command=self.OpenSelectedAvailableFolders)
        
        self.button_set_default_available["state"]  = "disabled"
        self.treeview_available_songlist["columns"] = ["artist", "name", "genre", "duration"]
        self.treeview_available_songlist.column("#0", width=20, stretch=False)
        self.treeview_available_songlist.heading("artist", text="Artist", command=lambda: self.SortTreeview("artist", "available"))
        self.treeview_available_songlist.heading("name", text="Name", command=lambda: self.SortTreeview("name", "available"))
        self.treeview_available_songlist.heading("genre", text="Genre", command=lambda: self.SortTreeview("genre", "available"))
        self.treeview_available_songlist.heading("duration", text="Dur.", command=lambda: self.SortTreeview("length", "available"))
        self.treeview_available_songlist.column("duration", width=10, anchor="center")
        self.treeview_available_songlist.column("genre", width=65)
        self.treeview_available_songlist.column("name", width=165)
        self.treeview_available_songlist.column("artist", width=110)
        self.treeview_available_songlist.tag_configure("parent_top", background="#C27E7F", foreground="white")
        self.treeview_available_songlist.tag_configure("parent_pending", background="#ABABAB", foreground="white")
        self.treeview_available_songlist.tag_configure("odd_row", background="#F5EAEB", foreground="black")
        self.treeview_available_songlist.tag_configure("pending_odd_row", background="#E8E8E8", foreground="black")
        self.treeview_available_songlist.tag_configure("search_results", background="#DBBB12", foreground="black")
        # Link treeview_available scroll with treeview_scrollbar position
        self.treeview_available_songlist.configure(yscrollcommand=self.scrollbar_treeview_available_songlist.set)  # connect y position of treeview to scrollbar
        self.scrollbar_treeview_available_songlist.configure(command=self.treeview_available_songlist.yview)  # connect scrollbar position to treeview y position
        

        self.available_base_entry = self.treeview_available_songlist.insert(parent="", index="end", iid=0, values=("Currently Available",), open=True, tags=("parent_top"))
        self.available_pending_entry = self.treeview_available_songlist.insert(parent="", index="end", iid=1, values=("Pending",), open=True, tags=("parent_pending"))

        # Pack widgets into their frames
        # Pack frames into window
        self.frame_tools.grid(column=0, row=0, sticky="we", padx=10, pady=10)
        self.frame_treeviews.grid(column=0, row=1, sticky="news")
        self.frame_current_songlist.grid(column=0, row=0, sticky="news", padx=10, pady=10)
        self.frame_available_songlist.grid(column=1, row=0, sticky="news", padx=10, pady=10)
        # setup main buttons in main grid
        self.entry_search.grid(column=0, row=0, sticky="we", columnspan=3)
        self.combobox_search_category.grid(column=2, row=1, sticky="we", pady=5)
        self.button_search.grid(column=3, row=0, sticky="news", rowspan=2, padx=10)
        self.radiobutton_current_songs.grid(column=0, row=1, sticky="we", padx=5)
        self.radiobutton_available_songs.grid(column=1, row=1, sticky="we", padx=5)
        self.seperator_tools_one.grid(column=4, row=0, sticky="ns", rowspan=2, padx=10)
        self.button_pick_current_path.grid(column=5, row=0, sticky="w", padx=5, pady=5, ipadx=10)
        self.entry_current_song_path.grid(column=6, row=0, sticky="we")
        self.button_set_default_current.grid(column=7, row=0, sticky="e", pady=5, padx=10)
        
        self.button_pick_available_path.grid(column=5, row=1, sticky="w", padx=5, pady=5, ipadx=10)
        self.entry_available_song_path.grid(column=6, row=1, sticky="we")
        self.button_set_default_available.grid(column=7, row=1, sticky="e", pady=5, padx=10)
        self.button_commit.grid(column=8, row=0, columnspan=2, rowspan=2, sticky="news", pady=5, padx=5)
        
        # setup treeview_current and it's button's grid
        self.treeview_current_songlist.grid(column=0, row=0, sticky="news", columnspan=4)
        self.scrollbar_treeview_current_songlist.grid(column=4, row=0, sticky="ns")
        self.button_remove.grid(column=0, row=1, sticky="ew", pady=5, padx=5)
        self.button_open_current.grid(column=2, row=1, sticky="ew", pady=5, ipadx=10)
        self.button_favourite.grid(column=3, row=1, sticky="ew", pady=5, padx=5)
        # setup treeview_available and it's button's grid
        self.treeview_available_songlist.grid(column=0, row=1, columnspan=3, sticky="news")
        self.scrollbar_treeview_available_songlist.grid(column=3, row=1, sticky="ns")
        self.button_add.grid(column=0, row=2, sticky="ew", pady=5, padx=5)
        self.button_open_available.grid(column=2, row=2, sticky="ew", pady=5, ipadx=10)

        # Configure Frames Weights
        # Configure frame_current grid weights
        self.frame_current_songlist.rowconfigure(0, weight=1)
        self.frame_current_songlist.rowconfigure(1, weight=0)
        self.frame_current_songlist.columnconfigure(0, weight=1)
        self.frame_current_songlist.columnconfigure(1, weight=0)
        self.frame_current_songlist.columnconfigure(2, weight=0)
        self.frame_current_songlist.columnconfigure(3, weight=0)
        # Configure frame_available grid weights
        self.frame_available_songlist.rowconfigure(0, weight=0)
        self.frame_available_songlist.rowconfigure(1, weight=1)
        self.frame_available_songlist.rowconfigure(2, weight=0)
        self.frame_available_songlist.columnconfigure(0, weight=1)
        self.frame_available_songlist.columnconfigure(1, weight=0)
        self.frame_available_songlist.columnconfigure(2, weight=0)
        self.frame_available_songlist.columnconfigure(3, weight=0)
        # Configure frame_treeviews grid weights
        self.frame_treeviews.rowconfigure(0, weight=1)
        self.frame_treeviews.columnconfigure(0, weight=1)
        self.frame_treeviews.columnconfigure(1, weight=1)
        # Configure app's grid weights
        self.columnconfigure(0, weight=1)
        #self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)


        self.UpdateSongListFromDirectory("available")
        self.UpdateSongListFromDirectory("current")

        self.UpdateEntries(self.treeview_current_songlist, self.current_song_list, self.current_song_list_pending)
        self.UpdateEntries(self.treeview_available_songlist, self.available_song_list, self.available_song_list_pending)


    def FavouriteSong(self):
        items_selected = self.treeview_current_songlist.selection()
        for item in items_selected:
            if self.treeview_current_songlist.item(item, "values")[4] == "":
                self.treeview_current_songlist.set(item, "favourite", "★")
            else:
                self.treeview_current_songlist.set(item, "favourite", "")

            new_fav_path = self.treeview_current_songlist.item(item)["values"][-1]
            for song in self.current_song_list:
                if new_fav_path in song["folder_path"]:
                    if song["favourite"] == "":
                        song["favourite"] = "★"
                        program_settings["favourites"].append(song["folder_path"])
                    else:
                        song["favourite"] = ""
                        program_settings["favourites"].remove(song["folder_path"])
        
        
        with open("settings.json", "w") as settings_file:
            json.dump(program_settings, settings_file, indent=4)

    def CommitChanges(self):
        # go through pending list of songs to add to the game, moving the folders over.
        if len(self.current_song_list_pending) != 0:
            for item in self.current_song_list_pending:
                shutil.move(self.path_available_songs.get() + "/" + item["folder_path"], self.path_current_songs.get())
                self.current_song_list.append(item)
            self.current_song_list_pending = []
            self.UpdateEntries(self.treeview_current_songlist, self.current_song_list, self.current_song_list_pending)
        else:
            print("NO new songs to ADD to current playlist")

        if len(self.available_song_list_pending) != 0:
            for item in self.available_song_list_pending:
                shutil.move(self.path_current_songs.get() + "/" + item["folder_path"], self.path_available_songs.get())
                self.available_song_list.append(item)
            self.available_song_list_pending = []
            self.UpdateEntries(self.treeview_available_songlist, self.available_song_list, self.available_song_list_pending)
        else:
            print("NO new songs to REMOVE from current playlist")


    def SortTreeview(self, category, song_list):
        reverse_sort = False
        if category == self.last_sort_category:
            reverse_sort = True
            self.last_sort_category = ""
        else:
            self.last_sort_category = category

        print(f"category {category} - treeview {song_list} - reverse sorting {reverse_sort}")

        match song_list:
            case "current":
                temp = sorted(self.current_song_list, key=lambda item: item[category], reverse=reverse_sort if category != "favourite" else not reverse_sort)
                self.current_song_list = temp
                self.UpdateEntries(self.treeview_current_songlist, self.current_song_list, self.current_song_list_pending)
            case "available":
                temp = sorted(self.available_song_list, key=lambda item: item[category], reverse=reverse_sort)
                self.available_song_list = temp
                self.UpdateEntries(self.treeview_available_songlist, self.available_song_list, self.available_song_list_pending)

        
    def UpdateEntries(self, _treeview, _songlist, _pendingsonglist):
        for entry in _treeview.get_children("0"):
            _treeview.delete(entry)
        for entry in _treeview.get_children("1"):
           _treeview.delete(entry)

        for song_entry in _songlist:
            _treeview.insert("0", index="end", values=list(song_entry.values()), tags=(("odd_row") if _songlist.index(song_entry) % 2 == 0 else ()))
        _treeview.item("0", values=("Currently Added - " + str(len(_treeview.get_children("0"))),))

        for song_entry in _pendingsonglist:
            _treeview.insert("1", index="end", values=list(song_entry.values()), tags=(("pending_odd_row") if _pendingsonglist.index(song_entry) % 2 == 0 else ()))
        _treeview.item("1", values=("Pending - " + str(len(_treeview.get_children("1"))),))

    # intricate
    def ___Update_CurrentSongList_Entries(self, col_sort):
        alphabet = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","misc"]
        # remove all entries from treeview
        for entry in self.treeview_current_songlist.get_children(self.current_base_entry):
            self.treeview_current_songlist.delete(entry)
        for entry in self.treeview_current_songlist.get_children(self.current_pending_entry):
            self.treeview_current_songlist.delete(entry)


        self.treeview_current_songlist.column("#0", width=40, stretch=False)
        for i in alphabet:
            self.treeview_current_songlist.insert(self.current_base_entry, iid=alphabet.index(i)+2, index="end", values=i.upper())

        for song_info in self.current_song_list:
            parent_letter = 28
            if song_info[col_sort][0].lower() in alphabet:
                parent_letter = alphabet.index(song_info[col_sort][0].lower())+2
            self.treeview_current_songlist.insert(parent_letter, index="end", values=song_info, tags=(("odd_row") if self.current_song_list.index(song_info) % 2 == 0 else ()))

    def UpdateSongListFromDirectory(self, song_list):
        playlist_directory = ""
        songs_path = ""

        song_artist_search_terms = ["artist=", "artist = "]
        song_name_search_terms   = ["name=", "name = "]
        song_genre_search_terms  = ["genre=", "genre = "]
        song_dur_search_terms    = ["song_length=", "song_length = "]

        try:
            match song_list:
                case "available":
                    playlist_directory = os.listdir(self.path_available_songs.get())
                    songs_path = self.path_available_songs.get()
                case "current":
                    playlist_directory = os.listdir(self.path_current_songs.get())
                    songs_path = self.path_current_songs.get()
                case _:
                    print("song_list provided does not match trees")

            for folder in playlist_directory:
                placeholder_song = {"artist":"", "name":"", "genre":"", "length":"", "favourite":"", "folder_path":""}
                placeholder_song["folder_path"] = folder
                if folder in program_settings["favourites"]:
                    placeholder_song["favourite"] = "★"
                try:
                    with open(songs_path + "/" + folder + "/song.ini", "r", encoding="utf8") as song_file:
                        try:
                            for line in song_file:
                                if any(art_match in line for art_match in song_artist_search_terms):
                                    raw_artist = line.split("=", maxsplit=1)[-1].strip().lower()
                                    if re.search(r"<[^>]+>", raw_artist):
                                        sanitized_artist = re.sub(r"<[^>]+>", "", raw_artist)
                                        placeholder_song["artist"] = sanitized_artist
                                    else:
                                        placeholder_song["artist"] = raw_artist
                                if any(nam_match in line for nam_match in song_name_search_terms):
                                    raw_name = line.split("=", maxsplit=1)[-1].strip().lower()
                                    if re.search(r"<[^>]+>", raw_name):
                                        sanitized_name = re.sub(r"<[^>]+>", "", raw_name)
                                        placeholder_song["name"] = sanitized_name
                                    else:
                                        placeholder_song["name"] = raw_name
                                if any(gen_match in line for gen_match in song_genre_search_terms):
                                    raw_genre = line.split("=", maxsplit=1)[-1].strip().lower()
                                    if re.search(r"<[^>]+>", raw_genre):
                                        sanitized_genre = re.sub(r"<[^>]+>", "", raw_genre)
                                        placeholder_song["genre"] = sanitized_genre
                                    else:
                                        placeholder_song["genre"] = raw_genre
                                if any(gen_match in line for gen_match in song_dur_search_terms):
                                    placeholder_song["length"] = ConvertMilliToTime(line.split("=")[1].strip().lower())
                            if song_list == "available":
                                self.available_song_list.append(placeholder_song)
                            else:
                                self.current_song_list.append(placeholder_song)
                        except UnicodeDecodeError:
                            if song_list == "available":
                                self.available_song_list.append([folder, "--SONG.INI NOT UTF8 ENC--", "", "", folder])
                            else:
                                self.current_song_list.append([folder, "--SONG.INI NOT UTF8 ENC--", "", "", folder])
                except FileNotFoundError:
                    if song_list == "available":
                        self.available_song_list.append([folder, "--MULTIPLE NESTED FOLDERS--", "", "", folder])
                    else:
                        self.current_song_list.append([folder, "--MULTIPLE NESTED FOLDERS--", "", "", folder])
        except FileNotFoundError:
            print("Tried searching Directory for Available Songs-Invalid Path")

    def AddSong(self, event=None):
        items_selected = [list(self.treeview_available_songlist.item(i, 'values')) for i in self.treeview_available_songlist.selection()]
        if len(items_selected) != 0:
            
            for item in items_selected:
                placeholder_song = {"artist":"", "name":"", "genre":"", "length":"", "favourite":"", "folder_path":""}
                placeholder_song["folder_path"] =item[-1]
                placeholder_song["artist"]      =item[0]
                placeholder_song["name"]        =item[1]
                placeholder_song["genre"]       =item[2]
                placeholder_song["length"]      =item[3]
                placeholder_song["favourite"]   =item[4]
                
                if placeholder_song in self.available_song_list:
                    self.current_song_list_pending.append(placeholder_song)
                    self.available_song_list.remove(placeholder_song)
                else:
                    self.current_song_list.append(placeholder_song)
                    self.available_song_list_pending.remove(placeholder_song)

            self.UpdateEntries(self.treeview_current_songlist, self.current_song_list, self.current_song_list_pending)
            self.UpdateEntries(self.treeview_available_songlist, self.available_song_list, self.available_song_list_pending)

    def RemoveSong(self, _event=None):
        items_selected = [list(self.treeview_current_songlist.item(i, "values")) for i in self.treeview_current_songlist.selection()]
        if len(items_selected) != 0:
            
            for item in items_selected:
                placeholder_song = {"artist":"", "name":"", "genre":"", "length":"", "favourite":"", "folder_path":""}
                placeholder_song["folder_path"] =item[-1]
                placeholder_song["artist"]      =item[0]
                placeholder_song["name"]        =item[1]
                placeholder_song["genre"]       =item[2]
                placeholder_song["length"]      =item[3]
                placeholder_song["favourite"]   =item[4]

                if placeholder_song in self.current_song_list:
                    self.available_song_list_pending.append(placeholder_song)
                    self.current_song_list.remove(placeholder_song)
                    if self.treeview_current_songlist.exists(3):
                        for i in self.treeview_current_songlist.get_children(3):
                            i_values = self.treeview_current_songlist.item(i, "values")
                            i_values = list(i_values)
                            if i_values == item:
                                self.treeview_current_songlist.delete(i)
                        if len(self.treeview_current_songlist.get_children(3)) == 0:
                            self.treeview_current_songlist.delete(3)
                else:
                    self.available_song_list.append(placeholder_song)
                    self.current_song_list_pending.remove(placeholder_song)

            self.UpdateEntries(self.treeview_current_songlist, self.current_song_list, self.current_song_list_pending)
            self.UpdateEntries(self.treeview_available_songlist, self.available_song_list, self.available_song_list_pending)

    def SearchSongs(self, tree_to_search, category_to_search):
        good_results = False
        item_category_index = 1
        treeview_to_search = ""
        self.search_results = []
        match tree_to_search:
            case "current":
                treeview_to_search = self.treeview_current_songlist
            case "available":
                treeview_to_search = self.treeview_available_songlist

        if self.treeview_current_songlist.exists(3):
            self.treeview_current_songlist.delete(3)
        if self.treeview_available_songlist.exists(3):
            self.treeview_available_songlist.delete(3)

        match category_to_search:
            case "artist":
                item_category_index = 0
            case "name":
                item_category_index = 1
            case "genre":
                item_category_index = 2

        for child_id in treeview_to_search.get_children("0"):
            treeview_item = treeview_to_search.item(child_id, "values")
            if self.search_entry_input.get().lower() in treeview_item[item_category_index].lower():
                self.search_results.append(treeview_item)
                good_results = True

        if good_results == False and "<No Matches Found>" not in self.search_entry_input.get():
            self.search_entry_input.set(self.search_entry_input.get() + " <No Matches Found>")

        if good_results:
            search_results_node = treeview_to_search.insert(parent="", index=0, iid=3, values=(f"Search Results - {len(self.search_results)} found",), open=True, tags=("search_results"))
            for i in self.search_results:
                treeview_to_search.insert(search_results_node, index="end", values=i, tags=("search_odd_row") if self.search_results.index(i) % 2 == 0 else (""))
        
    def OpenSelectedAvailableFolders(self):
        items_selected_available_treeview = [self.treeview_available_songlist.item(i) for i in self.treeview_available_songlist.selection()]

        if len(items_selected_available_treeview) != 0:
            for item in items_selected_available_treeview:
                OpenFileLoc(self.path_available_songs.get() + "/" + item['values'][-1])

    def OpenSelectedCurrentFolders(self):
        items_selected_current_treeview = [self.treeview_current_songlist.item(i) for i in self.treeview_current_songlist.selection()]

        if len(items_selected_current_treeview) != 0:
            for item in items_selected_current_treeview:
                OpenFileLoc(self.path_current_songs.get() + "/" + item['values'][-1])

    def ChangeCurrentSongsPath(self):
        new_path = filedialog.askdirectory()
        if len(new_path) != 0:
            self.button_set_default_current["state"] = "enabled"
            self.button_set_default_current["text"] = "Set Default"
            self.current_song_list = []
            self.current_song_list_pending = []
            self.path_current_songs.set(new_path)
            self.UpdateSongListFromDirectory("current")
            self.UpdateEntries(self.treeview_current_songlist, self.current_song_list, self.current_song_list_pending)

    def ChangeAvailableSongsPath(self):
        new_path = filedialog.askdirectory()
        if len(new_path) != 0:
            self.button_set_default_available["state"] = "enabled"
            self.button_set_default_available["text"] = "Set Default"
            self.available_song_list = []
            self.available_song_list_pending = []
            self.path_available_songs.set(new_path)
            self.UpdateSongListFromDirectory("available")
            self.UpdateEntries(self.treeview_available_songlist, self.available_song_list, self.available_song_list_pending)

    """
        Button Pressed - Default Current Path
            Disables the set default button for current songs path and changes it text.
            Updates the new path to current songs in the settings and dumps the settings
            to the settings file.
    """
    def SetCurrentSongPathDefault(self, path):
        self.button_set_default_current["state"] = "disabled"
        self.button_set_default_current["text"] = "Default"
        program_settings["current_path"] = path
        with open("settings.json", "w") as settings_file:
            json.dump(program_settings, settings_file, indent=4)

    """
        Button Pressed - Default Available Path
            Disables the set default button for available songs path and changes it text.
            Updates the new path to available songs in the settings and dumps the settings
            to the settings file.
    """
    def SetAvailablePathDefault(self, path):
        self.button_set_default_available["state"] = "disabled"
        self.button_set_default_available["text"] = "Default"
        program_settings["available_path"] = path
        with open("settings.json", "w") as settings_file:
            json.dump(program_settings, settings_file, indent=4)

    def TruncatePathLabel(self, _pathstr):
        pass


def OpenFileLoc(filename):
        match platform.system():
            case "Linux":
                try:
                    subprocess.run(['xdg-open', filename], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error opening file: {e}")
                except FileNotFoundError:
                    print("xdg-open command not found. Please ensure it is installed.")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
            #case "Windows":
                #TODO
                #os.startfile(self.path_current_songs.get() + "/" + item['values'][3])



def ConvertMilliToTime(m):
    raw = int(m)
    seconds = int((raw/1000)%60)
    minutes = int((raw/(1000*60))%60)
    final = f"{minutes}:{seconds:02d}"

    return final



if __name__ == "__main__":
    app = App()
    app.mainloop()
