import curses
import time

class Hover():
    def __init__(self, options: list, yPos: int, xPos: int, maxyx: tuple[int, int], style: tuple[int, int], Window = curses.initscr(), c_w: int = 2) -> None:
        self.__keys    = options
        self.__style   = style
        self.__y       = yPos
        self.__x       = xPos
        self.window    = Window
        self.__hoverWidth: int  = 0
        self.__maxy, self.__maxx = maxyx
        self.__hoverHeight: int = (len(self.__keys) * 2) +1

        for i in self.__keys:
            if len(i) > self.__hoverWidth:
                self.__hoverWidth = len(i)
        self.__hoverWidth = min(self.__hoverWidth + 2, self.__maxx -2)
        
        if self.__hoverHeight > self.__maxy-2:
            self.__hoverHeight  = self.__maxy -2

        if self.__y + self.__hoverHeight >= self.__maxy:
            self.__y = self.__maxy - self.__hoverHeight - 1

        if self.__x + self.__hoverWidth > self.__maxx:
            self.__x = self.__maxx - self.__hoverWidth -1


    def __drawBoard(self) -> None:
        for i in range(self.__hoverHeight):
            self.window.addstr(self.__y +i, self.__x, ' ' * self.__hoverWidth, self.__style[0])
            time.sleep(0.006125)
            self.window.refresh()
    
    def __hover(self) -> int | None:
        i:      int = 0
        height: int = int(self.__hoverHeight /2)
        n:      int = min(height, len(self.__keys))
        while True:
            for j in range(n):
                self.window.addstr(self.__y + (j * 2) +1, self.__x + 1, self.__keys[i + j] [: (self.__hoverWidth -2)] + ' ' * (self.__hoverWidth -2 - len(self.__keys[i + j])), self.__style[0])
                self.window.refresh()

            Key = self.window.getch()

            if Key == curses.KEY_MOUSE:
                _, a, b, _, _ = curses.getmouse()
                if a >= 0 and b>= 0:
                    if _ == curses.BUTTON1_CLICKED:
                        if a >= self.__x and a <= (self.__x + self.__hoverWidth) and b >= self.__y and b < (self.__y + self.__hoverHeight):
                            return  int((b - self.__y)/2) + i 
                        else:
                            return None
                    elif _ == curses.BUTTON4_PRESSED:
                        i = max(0, i-1)
                    elif _ == curses.BUTTON5_PRESSED:
                        i = (i +1) if (i+n) < len(self.__keys) else i
            else:
                continue

    def hover(self) -> int | None:
        self.__drawBoard()
        selected = self.__hover()
        if selected is not None:
            try:
                self.__keys[selected]
            except:
                return 
            else:
                return selected

