from pytube import YouTube
import time
import json
import printer

class Downloader():
    def __init__(self, playlist: list[list], window, dtitle: str = '') -> None:
        self.window = window
        self.window.clear()
        self.__plist = playlist
        self.__dtitle = printer.reduceName(dtitle, 250)
        self.__hms     = lambda sec: (sec//3600, (sec- 3600*(sec//3600))//60, (sec - 3600*(sec//3600))%60)
        self.__hms_str = lambda h, m, s: "{}:{}:{}".format(h if h > 9 else '0'+str(h),m if m > 9 else '0'+str(m),s if s > 9 else '0'+str(s))
        with open('./path.json', 'r') as f:
            Path = json.load(f)
        self.__path = Path['path']
        self.__loadDownloader()

    def __loadDownloader(self) -> None:
        self.__maxy, self.__maxx = self.window.getmaxyx()

    def __downloader(self) -> None:
        for i, p in enumerate(self.__plist):
            stream: list = list()
            stream_str: list = list()
            self.window.addstr(1, 1, "[Downloading {}/{}]".format((i+1), len(self.__plist)))
            if p[4] is not None:
                fname: list = printer.formatter1([p[4][0].title if p[-1][0] is not None else p[4][1].title, '', self.__hms_str(*self.__hms(p[1]))], self.__maxx - 4)
                self.window.addstr(3, 2, fname[0])
                self.window.addstr(4, 2, fname[1])
                self.window.addstr(4, 2 + len(fname[1]), fname[2])
                stream = p[4]
                stream_str = p[0]
                self.window.refresh()
            else:
                av = YouTube(p[3])
                av.register_on_progress_callback(lambda stream, chunk, bytes_remaining: printer.progress(self.window, stream, chunk, bytes_remaining, (8, 2)))
                fname: list = printer.formatter1([av.title, '', self.__hms_str(*self.__hms(p[1]))], self.__maxx - 4)
                self.window.addstr(3, 2, fname[0])
                self.window.addstr(4, 2, fname[1])
                self.window.addstr(4, 2 + len(fname[1]), fname[2])
                self.window.addstr(6, 2, 'Getting Stream ')
                Streams = av.streams
                stream_str, stream = printer.filter(p[0], Streams)
                self.window.addstr(6, 17, "Done")
                self.window.refresh()

            file_name = ((printer.zeros(len(str(len(self.__plist))), i) + '-') if i != 0 else '') + printer.reduceName(stream[0].title if stream[0] else stream[1].title, 245 - len(str(len(self.__plist))))
            ext: str  = stream[0].subtype if stream[0] else stream[1].subtype 

            for k, l in enumerate(stream): 
                if l:
                    l.download(filename = file_name + ".part{}".format(k + 1), output_path = self.__path + self.__dtitle)
                    time.sleep(1)
                else:
                    self.window.addstr(8 + k, 2, "Video" if k == 0 else "Audio")
                    self.window.addstr(8 + k, 8, "[None]")
                    self.window.refresh()
                self.window.refresh()

            if None not in stream:
                self.window.addstr(11, 2, "Merging ")
                self.window.refresh()
                code = printer.merger(self.__path + self.__dtitle + file_name + '.part1', self.__path + self.__dtitle + file_name + '.part2', ext, self.__path + self.__dtitle + file_name)
                if code == 0:
                    self.window.addstr(11, 11, "Done")
                else:
                    self.window.addstr(11, 11, "Error")
                self.window.refresh()

            else:
                if stream[0]:
                    printer.renameFile(self.__path + self.__dtitle + file_name + '.part1', self.__path + self.__dtitle + file_name + '.' + ext)
                elif stream[1]:
                    printer.renameFile(self.__path + self.__dtitle + file_name + '.part2', self.__path + self.__dtitle + file_name + '.' + ext)

            printer.deleteFiles([self.__path + self.__dtitle + file_name + '.part1', self.__path + self.__dtitle + file_name + '.part2'])

            self.window.clear()

    def __call__(self) -> None:
        self.__downloader()
