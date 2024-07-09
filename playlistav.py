from pytube import Playlist, StreamQuery, exceptions, Stream
import hover
import printer
import time
import curses

class PlaylistAV():
    def __init__(self, url: str, data: list[dict], Window) -> None:
        self.url = url
        self.window = Window
        self.time = 0
        self.__usr_stream = data
        self.__break: bool = False
        self.__isStreamEnabled: bool = False
        self.__isStreamInitialized: bool = False
        self.__maxy, self.__maxx = self.window.getmaxyx()
        self.__hms     = lambda sec: (sec//3600, (sec- 3600*(sec//3600))//60, (sec - 3600*(sec//3600))%60)
        self.__hms_str = lambda h, m, s: "{}:{}:{}".format(h if h > 9 else '0'+str(h),m if m > 9 else '0'+str(m),s if s > 9 else '0'+str(s))
        self.__removed: list = list()
        self.window.clear()

        if len(self.__usr_stream) == 1:
            self.__playlist_type: str = 'audio'
            self.__stream_str: list = [None, self.__usr_stream[0] ['abr']]
        else:
            self.__playlist_type: str = 'video'
            self.__stream_str: list = [self.__usr_stream[0] ['res'], self.__usr_stream[1] ['abr']]

        #Hover
        options = ["Edit streams", "Inv Select", "Finish", "Exit"]
        self.__menu: hover.Hover = hover.Hover(options, 0, self.__maxx - 14, self.window.getmaxyx(), (0, 0))

        # Getting Playlist info
        self.window.addstr(self.__maxy -1, 1, "Fetching ")
        self.__plist: list = list()
        try:
            self.__playlist: Playlist = Playlist(self.url)
        except:
            curses.endwin()
            print("KeyError: Invalid Url")
            time.sleep(2)

        self.title: str = self.__playlist.title
        self.__length: int = self.__playlist.length
        for i, j in enumerate(self.__playlist.videos):
            start = time.time()
            self.__plist.append([j.title, j.length, self.__playlist_type, self.__stream_str, None, None, j, j.watch_url])
            end = time.time()
            self.window.addstr(self.__maxy -1, 10, "{}/{} {}%".format(i +1, self.__length, str(int(((i +1) / self.__length) * 100))))
            self.window.addstr(self.__maxy -1, self.__maxx -13, "eta {}".format(self.__hms_str(*self.__hms(int((end - start) * (self.__length - (i + 1)))))))
            self.window.refresh()
        self.__length = len(self.__plist)

    def __load_playlist(self) -> None:
        self.__list: list = list()
        for i in self.__plist:
            self.__list.append(printer.formatter1([i[0], ' ' if i[4] is None else str(round((i[5][0].filesize_mb if i[5][0] is not None else 0) + i[5][1].filesize_mb, 2)) , self.__hms_str(*self.__hms(i[1]))], self.__maxx - 6) + [chr(9472) + str(i[3][0]) + chr(9472) + ((str(i[3][1]) + chr(32)) if i[3][1] < 100 else str(i[3][1])) + 'kbps' + chr(9472)])

        self.__maxy, self.__maxx = self.window.getmaxyx()
        self.__i: int            = 0
        self.__n: int            = min(int((self.__maxy -2)/ 4), len(self.__list))
        self.__box: printer.Box  = printer.Box(1, 1, self.__maxx -3, 2, Window=self.window)  
        self.window.clear()
        self.window.addstr(0, 2, self.title[:self.__maxx - 4].center(self.__maxx - 4), curses.A_BOLD)
        self.window.addstr(0, self.__maxx - 1, ':')
        self.__box.boxes(self.__n)
        self.window.refresh()

    def __loadStream(self) -> None:
        self.window.clear()
        self.window.refresh()
        self.window.addstr(self.__maxy -1, 1, "Fetching ")
        self.window.refresh()
        for i, j in enumerate(self.__playlist.videos):
            start = time.time()
            self.__plist[i][4] = j.streams
            self.__plist[i][3], self.__plist[i][5] = printer.filter(self.__plist[i][3], self.__plist[i][4])
            end = time.time()
            self.window.addstr(self.__maxy -1, 10, "{}/{} {}%".format(i +1, self.__length, str(int(((i +1) / self.__length) * 100))))
            self.window.addstr(self.__maxy -1, self.__maxx -13, "eta {}".format(self.__hms_str(*self.__hms(int((end - start) * (self.__length - (i + 1)))))))
            self.window.refresh()

    def __updateStream(self, i: int, lstream: tuple[Stream | None, Stream | None]) -> None:
        stream = self.__plist[i]
        for k, j in enumerate(lstream):
            if j is not None:
                stream[5][k] = j
                stream[3][k] = int(j.abr[:-4]) if j.abr is not None else int(j.resolution[:-1])
        if stream[5][0] is not None:
            stream[2] = 'video'

        self.__plist[i] = stream
        self.__list[i]  = printer.formatter1([stream[0], ' ' if stream[4] is None else str(round((stream[5][0].filesize_mb if stream[5][0] is not None else 0) + stream[5][1].filesize_mb, 2)) , self.__hms_str(*self.__hms(stream[1]))], self.__maxx - 6) + [chr(9472) + ((str(stream[3][0]) + chr(9472)) if stream[3][0] is None else (str(stream[3][0])) + 'p') + chr(9472) + ((str(stream[3][1]) + chr(32)) if stream[3][1] < 100 else str(stream[3][1])) + 'kbps' + chr(9472)]

    def __selectStream(self, streams: StreamQuery, type: str, x: int, y: int):
        streams = streams.filter(adaptive=True).filter(type=type)
        options = printer.formatter3(stream=streams, type=type)
        qhover  = hover.Hover(options=options, yPos=y, xPos=x, maxyx=(self.__maxy, self.__maxx), style=(0, 0))
        l: int | None = qhover.hover()
        self.window.clear()
        self.window.addstr(0, 2, self.title[:self.__maxx - 4].center(self.__maxx - 4), curses.A_BOLD)
        self.window.addstr(0, self.__maxx - 1, ':')
        self.__box.boxes(self.__n)
        self.window.refresh()
        return streams[l] if l is not None else None

    def __playlist_av(self) -> list | None:
        while not self.__break:
            for j in range(self.__n):
                if self.__i + j in self.__removed:
                    printer.printer1(self.__list[self.__i + j], (4 * j) + 2, 3, (curses.A_DIM, curses.A_DIM), self.window)
                    self.window.addstr((4 * j) + 4 ,self.__maxx - 16, self.__list[self.__i + j][3], curses.A_DIM)
                else:
                    printer.printer1(self.__list[self.__i + j], (4 * j) + 2, 3, (0, 0), self.window)
                    self.window.addstr((4 * j) + 4 ,self.__maxx - 16, self.__list[self.__i + j][3])
                self.window.refresh()

            key = self.window.getch()

            if key == curses.KEY_MOUSE:
                _, a, b, _, _ = curses.getmouse()

                if a >= 0 and b >= 0:
                    if _ == curses.BUTTON1_CLICKED:
                        if b > 1 + (self.__n * 4):
                            continue

                        elif b == 0:
                            k = self.__menu.hover()
                            if k == 0:
                                if not self.__isStreamInitialized:
                                    self.__isStreamInitialized =True
                                    self.__isStreamEnabled = True
                                    self.__loadStream()
                                    self.__load_playlist()

                            elif k == 1:
                                self.__invertSelect()

                            elif k == 2:
                                return self.__finish()
                            
                            elif k == 3:
                                self.__exit()
                                continue

                            self.__box.boxes(self.__n)
                            self.window.addstr(0, self.__maxx - 1, ':')
                            self.window.refresh()
                            continue

                        choice = int((b - 1) / 4 ) + self.__i 
                        if self.__isStreamEnabled:
                            if (b - 1) % 4 == 3:
                                if a > self.__maxx - 10:
                                    selected_stream = self.__selectStream(self.__plist[choice][4], type='audio', x=a, y=b)
                                    if selected_stream is None:
                                        pass 
                                    else:
                                        self.__updateStream(choice, (None, selected_stream))
                                    continue
                                elif a > self.__maxx - 17 and a < self.__maxx - 10:
                                    selected_stream = self.__selectStream(self.__plist[choice][4], type='video', x=a, y=b)
                                    if selected_stream is None:
                                        pass
                                    else:
                                        self.__updateStream(choice, (selected_stream, None))
                                    continue

                        if choice not in self.__removed:
                            self.__removed.append(choice)
                        else:
                            self.__removed.remove(choice)

                    elif _ == curses.BUTTON4_PRESSED:
                        self.__i = max(0, self.__i -1)

                    elif _ == curses.BUTTON5_PRESSED:
                        self.__i = (self.__i + 1) if (self.__i + self.__n) < len(self.__list) else self.__i

    def __invertSelect(self) -> None:
        for i in range(len(self.__plist)):
            if i in self.__removed:
                self.__removed.remove(i)
            else:
                self.__removed.append(i)

    def __exit(self) -> None:
        self.__break = True

    def __finish(self) -> list:
        PLAYLIST: list = list()
        for i, j in enumerate(self.__plist):
            if i in self.__removed:
                continue
            else:
                PLAYLIST.append([j[3], j[1], None if j[5] is None else ((j[5][0].filesize_mb if j[5][0] is not None else 0) + (j[5][1].filesize_mb)),j[6].watch_url, None])
        return PLAYLIST
       
    def __call__(self) -> list | None:
        try:
            self.__load_playlist()
            PLAYLIST = self.__playlist_av()
            return PLAYLIST
        except Exception as e:
            curses.endwin()
            print(e)

