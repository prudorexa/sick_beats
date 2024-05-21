import tkinter as tk
from tkinter import messagebox, simpledialog
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = 'c8c42796a18144eb908ed405a5ae16ff'
CLIENT_SECRET = '92d532c92e5247ea99b16694edcdb103'
REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = 'playlist-modify-public playlist-read-private'

class SpotifyApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Spotify Playlist Manager")

        self.sp = self.authenticate_spotify()
        self.user_id = self.sp.me()['id']
        
        self.playlist_id = None
        self.playlist_tracks = []

        self.create_widgets()
        self.fetch_playlists()

    def authenticate_spotify(self):
        auth_manager = SpotifyOAuth(client_id=CLIENT_ID,
                                    client_secret=CLIENT_SECRET,
                                    redirect_uri=REDIRECT_URI,
                                    scope=SCOPE)
        return Spotify(auth_manager=auth_manager)
    
    def create_widgets(self):
        self.playlist_box = tk.Listbox(self.master, width=50)
        self.playlist_box.grid(row=0, column=0, padx=10, pady=10, rowspan=6)
        self.playlist_box.bind('<<ListboxSelect>>', self.on_playlist_select)
        
        tk.Label(self.master, text="Track URI:").grid(row=0, column=1, padx=10, pady=10)
        self.track_uri_var = tk.StringVar()
        tk.Entry(self.master, textvariable=self.track_uri_var).grid(row=0, column=2, padx=10, pady=10)

        tk.Button(self.master, text="Add Track", command=self.add_track).grid(row=1, column=1, columnspan=2, pady=10)
        tk.Button(self.master, text="Remove Selected Track", command=self.remove_selected_track).grid(row=2, column=1, columnspan=2, pady=10)
        tk.Button(self.master, text="Reorder Track", command=self.reorder_track).grid(row=3, column=1, columnspan=2, pady=10)
        tk.Button(self.master, text="Fetch Playlists", command=self.fetch_playlists).grid(row=4, column=1, columnspan=2, pady=10)
        
        self.track_box = tk.Listbox(self.master, width=50)
        self.track_box.grid(row=6, column=0, columnspan=3, padx=10, pady=10)
    
    def on_playlist_select(self, event):
        w = event.widget
        if w.curselection():
            index = int(w.curselection()[0])
            self.playlist_id = self.playlists[index]['id']
            self.fetch_tracks()
    
    def fetch_playlists(self):
        self.playlists = self.sp.user_playlists(self.user_id)['items']
        self.playlist_box.delete(0, tk.END)
        for playlist in self.playlists:
            self.playlist_box.insert(tk.END, playlist['name'])
    
    def fetch_tracks(self):
        if not self.playlist_id:
            return
        self.playlist_tracks = self.sp.playlist_tracks(self.playlist_id)['items']
        self.track_box.delete(0, tk.END)
        for track in self.playlist_tracks:
            self.track_box.insert(tk.END, track['track']['name'])
    
    def add_track(self):
        track_uri = self.track_uri_var.get()
        if not track_uri or not self.playlist_id:
            messagebox.showwarning("Input Error", "Track URI or Playlist not selected!")
            return
        self.sp.playlist_add_items(self.playlist_id, [track_uri])
        self.fetch_tracks()
    
    def remove_selected_track(self):
        selected_track_index = self.track_box.curselection()
        if not selected_track_index:
            messagebox.showwarning("Selection Error", "No track selected!")
            return
        track_uri = self.playlist_tracks[selected_track_index[0]]['track']['uri']
        self.sp.playlist_remove_all_occurrences_of_items(self.playlist_id, [track_uri])
        self.fetch_tracks()
    
    def reorder_track(self):
        selected_track_index = self.track_box.curselection()
        if not selected_track_index:
            messagebox.showwarning("Selection Error", "No track selected!")
            return
        old_position = selected_track_index[0]
        new_position = simpledialog.askinteger("Input", f"Enter new position for track {old_position + 1}:", minvalue=1, maxvalue=len(self.playlist_tracks)) - 1
        if new_position is not None:
            self.sp.playlist_reorder_items(self.playlist_id, range_start=old_position, insert_before=new_position)
            self.fetch_tracks()

if __name__ == "__main__":
    root = tk.Tk()
    app = SpotifyApp(root)
    root.mainloop()
