from pytube import YouTube, exceptions
import curses
import printer

class AV():
    def __init__(self, url: str, Window = curses.initscr()) -> None:
        super().__init__()
        self.window           = Window
        self.url              = url
        self.testtims: float  = 0
        self.title: str       = ''
        self.isPlaylist: bool = True if 'playlist' in url else False
        self.__style: dict  = {
                "res"  : 0,
                "type" : 0,
                "mime" : 0,
                "prog" : 0,
                "size" : 0
                }

        if not self.isPlaylist:
            try:
                self.__yt: YouTube  = YouTube(url)
                self.__yt.register_on_progress_callback(lambda stream, chunk, bytes_remaining: printer.progress(self.window, stream, chunk, bytes_remaining, (8, 2)))
            except exceptions.RegexMatchError:
                curses.endwin()
        
            self._streams       = self.__yt.streams
            self._stream       = list(self._streams.filter(type='audio')) + list(self._streams.filter(type='video'))
        else:
            self.__audio: list[dict] = [
                {'abr': 48,  'type': 'audio', 'mime': 'mp4/webm', 'stream': 'adaptive', 'size': '--/--'},
                {'abr': 50,  'type': 'audio', 'mime': 'mp4/webm', 'stream': 'adaptive', 'size': '--/--'},
                {'abr': 70,  'type': 'audio', 'mime': 'mp4/webm', 'stream': 'adaptive', 'size': '--/--'},
                {'abr': 128, 'type': 'audio', 'mime': 'mp4/webm', 'stream': 'adaptive', 'size': '--/--'},
                {'abr': 160, 'type': 'audio', 'mime': 'mp4/webm', 'stream': 'adaptive', 'size': '--/--'},
                ]
            self.__video: list[dict] = [
                {'res': 144, 'type': 'video', 'mime': 'mp4/webm', 'stream': 'adaptive', 'size': '--/--'},
                {'res': 240, 'type': 'video', 'mime': 'mp4/webm', 'stream': 'adaptive', 'size': '--/--'},
                {'res': 360, 'type': 'video', 'mime': 'mp4/webm', 'stream': 'adaptive', 'size': '--/--'},
                {'res': 480, 'type': 'video', 'mime': 'mp4/webm', 'stream': 'adaptive', 'size': '--/--'},
                {'res': 720, 'type': 'video', 'mime': 'mp4/webm', 'stream': 'adaptive', 'size': '--/--'}
                ]
            self._pstream: list[dict] = self.__audio + self.__video

        self.__dload: list = []
        self.__break: bool = False

    def __load_av(self) -> None:
        self.__list: list  = []
        if not self.isPlaylist:
            for i in self._stream:
                self.__list.append([i.resolution if i.resolution is not None else i.abr, i.type, i.mime_type[6:], "Progressive" if i.is_progressive else "Adaptive", str(round(i.filesize_mb, 2))])
        else:
            for i in self._pstream:
                self.__list.append([str(i['res'])+'p' if i['type'] == 'video' else str(i['abr']) + 'kbps', i['type'], i['mime'], i['stream'], i['size']])

        self.__maxy, self.__maxx = self.window.getmaxyx()
        self.__Elist             = printer.formatter2(self.__list, self.__maxx -8)
        self.__i: int            = 0
        self.__n: int            = min(int((self.__maxy -2)/ 4), len(self.__Elist))
        self.__box: printer.Box  = printer.Box(1, 1, self.__maxx -3, 2, Window=self.window)  
        self.window.clear()
        self.__box.boxes(self.__n)
        self.window.refresh()
        
    def __av(self) -> None:
        while not self.__break:
            for j in range(self.__n):
                printer.printer2(self.__Elist[self.__i + j], (4 * j) + 1, 4, self.__style, self.window)
                self.window.refresh()

            key = self.window.getch()

            if key == curses.KEY_MOUSE:
                _, a, b, _, _ = curses.getmouse()

                if a >=0 and b>= 0:
                    if _ == curses.BUTTON1_CLICKED:
                        if b > 1 + (self.__n * 4) or b == 1:
                            continue
                        self.__handle(int((b - 1) / 4 ) + self.__i)

                    elif _ == curses.BUTTON4_PRESSED:
                        self.__i = max(0, self.__i -1)

                    elif _ == curses.BUTTON5_PRESSED:
                        self.__i = (self.__i + 1) if (self.__i + self.__n) < len(self.__list) else self.__i
    
    def __handle(self, selected: int) -> None:
        if not self.isPlaylist:
            stream = self._stream[selected]
            self.__dload.append(stream)

            if stream.type == 'video':
                if not stream.is_progressive:
                    self._stream = list(self._streams.filter(type='audio'))
                    self.__load_av()
                else:
                    self.__break = True
            else:
                self.__break = True

        else:
            stream = self._pstream[selected]
            self.__dload.append(stream)

            if stream['type'] == 'video':
                self._pstream = self.__audio
                self.__load_av()
            else:
                self.__break = True

    def __returnAV(self) -> list[list]:
        dload: list = list()
        stream: list = list()
        if len(self.__dload) == 1:
            if self.__dload[0].is_progressive:
                dload.append([int(self.__dload[0].resolution[:-1]), None])
                stream = [self.__dload[0], None]
            else:
                dload.append([None, int(self.__dload[0].abr[:-4])])
                stream = [None, self.__dload[0]]
        else:
            dload.append([int(self.__dload[0].resolution[:-1]), int(self.__dload[1].abr[:-4])])
            stream = [self.__dload[0], self.__dload[1]]
        dload = dload + [self.__yt.length, sum(map(lambda x: x.filesize_mb if x is not None else 0, stream)), self.__yt.watch_url, stream]

        return [dload]


    def __call__(self) -> list:
        self.__load_av()
        self.__av()
        return self.__dload if self.isPlaylist else self.__returnAV()

    #######################################################


if __name__ == '__main__':
    c = curses.initscr() 
    c.keypad(True)
    curses.mousemask(curses.ALL_MOUSE_EVENTS)
    curses.noecho()
    curses.curs_set(0)
    #b = AV('https://youtube.com/playlist?list=PLqhTK1mPb1pk9zugArRFvVjvyUEmKGI8P&si=Sd3Bp6Gcqo5L5qdS',c)
    b = AV('https://youtu.be/CzSL-YKjYn4?si=R00q1KYp7egDfimwH0',c)
    a= b()
    curses.endwin()
    print(a) 

