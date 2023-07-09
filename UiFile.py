import tkinter as tk
from tkinter.ttk import *

# since there is no status bar widget in Tk people just use a label as one
# this is a simple class to basically just create a label
class StatusBar(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.label = tk.Label(self, bd=1, relief="sunken", anchor="w", pady=4, padx=8) # the settings will give the look of a status bar to the label
        self.label.grid(column=0, row=0, sticky="ew")                                  # make sure to stretch the label bounds left/right
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
    
    # set text of the label
    def setText(self, newText):
        self.label.config(text=newText)

    # clear text in the label
    def clearText(self):
        self.label.config(text="")

# Main App class to create window
class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.geometry("1280x768")                                        # set window dimensions
        self.title("Clone Hero Playlist Manager - Standalone UI file")   # set top title bar name
        
        # create 2 tk vars to store path strings
        # tk vars allow you to change a var once and an tk element
        # using that var will update there values
        self.path_current_songs   = tk.StringVar()
        self.path_current_songs.set(r"No Path Selected")
        self.path_available_songs = tk.StringVar()
        self.path_available_songs.set(r"No Path Selected")

        # 4 booleans for changing sorting directions of treeview nodes
        self.sort_current_artist_alpha   = True
        self.sort_current_name_alpha     = True
        self.sort_available_artist_alpha = True
        self.sort_available_name_alpha   = True

        # Create Frames
        self.frame_main               = Frame(self)                          # main frame holding everything
        self.frame_current_songlist   = Frame(self.frame_main, padding=10)   # frame for current treeview/remove btn/open current file location/current path
        self.frame_available_songlist = Frame(self.frame_main, padding=10)   # frame for available treeview/add btn/ open available file location/available path

        # create status bar across bottom of window
        self.status_bar = StatusBar(self.frame_main)
        
        # Create buttons
        self.button_add            = Button(self.frame_available_songlist, text="Add", underline=0)
        self.button_remove         = Button(self.frame_current_songlist, text="Remove", underline=1)
        self.button_open_available = Button(self.frame_available_songlist, text="Open selected song folder(s)")
        self.button_open_current   = Button(self.frame_current_songlist, text="Open selected song folder(s)")

        # create and setup both treeviews
        # Current Treeview setup
        self.treeview_current_songlist            = Treeview(self.frame_current_songlist)                                   # create treeview for current song list
        self.scrollbar_treeview_current_songlist  = Scrollbar(self.frame_current_songlist, orient="vertical")               # create scrollbar widget for treeview
        self.treeview_current_songlist["columns"] = ["artist", "name"]                                                      # setup 2 columns
        self.treeview_current_songlist.column("#0", width=20, stretch=False)                                                # this column holds button to expand parent node/make it a set size
        self.treeview_current_songlist.heading("artist", text="Artist")                                                     # set label of first column
        self.treeview_current_songlist.heading("name", text="Name")                                                         # set label of second column
        self.treeview_current_songlist.tag_configure("parent_top", background="#809EC2", foreground="white")                # set color scheme for parent node holding added songs
        self.treeview_current_songlist.tag_configure("parent_pending", background="#ABABAB", foreground="white")            # set color scheme for parent node holding pending song moves
        self.treeview_current_songlist.tag_configure("odd_row", background="#EBF2F5", foreground="black")                   # set color scheme for all songs in an odd row
        self.treeview_current_songlist.tag_configure("pending_odd_row", background="#E8E8E8", foreground="black")           # set color scheme for all songs in an odd row that's pending
        # Link treeview_current scroll with treeview_scrollbar position
        self.treeview_current_songlist.configure(yscrollcommand=self.scrollbar_treeview_current_songlist.set)               # connect y position of treeview to scrollbar
        self.scrollbar_treeview_current_songlist.configure(command=self.treeview_current_songlist.yview)                    # connect scrollbar position to treeview y position
        # Info for Current Treeview folder path
        self.label_current_songs_path = Label(self.frame_current_songlist, textvariable=self.path_current_songs)
        # create the 2 parent nodes
        self.current_base_entry    = self.treeview_current_songlist.insert(parent="", index="end", iid=0, values=("Currently Added",), open=True, tags=("parent_top"))
        self.current_pending_entry = self.treeview_current_songlist.insert(parent="", index="end", iid=1, values=("Pending",), open=True, tags=("parent_pending"))
        
        # Available Treeview setup
        self.treeview_available_songlist            = Treeview(self.frame_available_songlist)
        self.scrollbar_treeview_available_songlist  = Scrollbar(self.frame_available_songlist, orient="vertical")
        self.treeview_available_songlist["columns"] = ["artist", "name"]
        self.treeview_available_songlist.column("#0", width=20, stretch=False)
        self.treeview_available_songlist.heading("artist", text="Artist")
        self.treeview_available_songlist.heading("name", text="Name")
        self.treeview_available_songlist.tag_configure("parent_top", background="#C27E7F", foreground="white")               
        self.treeview_available_songlist.tag_configure("parent_pending", background="#ABABAB", foreground="white")          
        self.treeview_available_songlist.tag_configure("odd_row", background="#F5EAEB", foreground="black")                 
        self.treeview_available_songlist.tag_configure("pending_odd_row", background="#E8E8E8", foreground="black")         
        # Link treeview_available scroll with treeview_scrollbar position
        self.treeview_available_songlist.configure(yscrollcommand=self.scrollbar_treeview_available_songlist.set)  # connect y position of treeview to scrollbar
        self.scrollbar_treeview_available_songlist.configure(command=self.treeview_available_songlist.yview)  # connect scrollbar position to treeview y position
        # Info for available Treeview
        self.label_available_song_path = Label(self.frame_available_songlist, textvariable=self.path_available_songs)
        # create the 2 parent nodes
        self.available_base_entry    = self.treeview_available_songlist.insert(parent="", index="end", iid=0, values=("Currently Available",), open=True, tags=("parent_top"))
        self.available_pending_entry = self.treeview_available_songlist.insert(parent="", index="end", iid=1, values=("Pending",), open=True, tags=("parent_pending"))

        # Pack widgets into their frames
        # setup treeview_current and it's button's grid
        self.label_current_songs_path.grid(column=0, row=0, columnspan=2, sticky="ew")
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
        self.label_available_song_path.grid(column=0, row=0, columnspan=2, sticky="ew")
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
        self.status_bar.grid(column=0, row=1, columnspan=2, sticky="ew")
        self.frame_current_songlist.grid(column=0, row=0, sticky="news", padx=10, pady=10)
        self.frame_available_songlist.grid(column=1, row=0, sticky="news", padx=10, pady=10)

        # Configure app's grid weights
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Configure frame_main's grid weights
        self.frame_main.rowconfigure(0, weight=100)
        self.frame_main.rowconfigure(1, weight=1)
        #self.frame_main.rowconfigure(2, weight=1)
        self.frame_main.columnconfigure(0, weight=1)
        self.frame_main.columnconfigure(1, weight=1)