import curses
from av import AV
from playlistav import PlaylistAV
from downloader import Downloader
from pytube import Playlist
import sys

def run(url: str) -> None:
    window = curses.initscr()
    curses.curs_set(0)
    curses.noecho()
    curses.mousemask(curses.ALL_MOUSE_EVENTS)
    window.keypad(True)
    window.clear()

    ObjAV = AV(url, window)()
    window.clear()
    window.refresh()
    if 'playlist' in url:
        title = Playlist(url).title
        ObjPlaylist = PlaylistAV(url, ObjAV, window)
        playlist = ObjPlaylist()
        window.clear()
        window.refresh()
        if playlist:
            Downloader(playlist, window, dtitle=title + '/')()
    else:
        Downloader(ObjAV, window, dtitle='')()

    window.clear()
    window.refresh()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        curses.endwin()
        raise Exception("Provide Valid Url")
    try:
        run(sys.argv[1])
        curses.endwin()
    except Exception as e:
        curses.endwin()
        print(e)
		

