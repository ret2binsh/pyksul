import tkinter
from functools import partial

Yellow = "#ffff00"
Blue   = "#0000ff"
Red    = "#FF0000"
Lime   = "#00FF00"
White  = "#ffffff"
Black  = "#000000"
ColorState = [
        Yellow,
        Blue,
        Red,
        Lime,
        White,
        Black]
ColorNum = len(ColorState)
CurrentColor = Black

class MainProgram:

    def __init__(self, event=None):
        self.master = tkinter.Tk()
        self.master.title("LED Matrix Creator")
        self.buttonArray = []
        self.buttonState = []

        for x in range(16):
            templist = []
            stateInit = []
            for y in range(16):
                stateInit.append(Black)
                ButtonPress = partial(self.ButtonPress,x,y)
                templist.append(tkinter.Button(self.master,
                        command=ButtonPress))
                templist[y].grid(row=y,column=x)
                templist[y].config(height=3,width=5,bg=Black)
            self.buttonArray.append(templist)
            self.buttonState.append(stateInit)
 
        self.printButton = tkinter.Button(self.master,text="Generate",
                command=self.GenerateOutput)
        self.printButton.grid(row=17,column=7)
        self.printButton.config(height=5,width=5)
        self.clearButton = tkinter.Button(self.master,text="Clear",
                command=self.ClearGrid)
        self.clearButton.grid(row=17,column=8)
        self.clearButton.config(height=5,width=5)
        self.GenerateColorPalette()
        self.master.mainloop()

    def GenerateOutput(self):
        print("Attempting to write current matrix")
        with open("ledframe.txt","w") as f:
            for x in range(16):
                for y in range(16):
                    ledNum = y * 16 + x
                    print("Button state: {}".format(self.buttonState[x][y]))
                    type(self.buttonState[x][y])
                    color = int(self.buttonState[x][y][1:],16)
                    if color:
                        command = "led[{}] = CRGB({});\n".format(ledNum,color)
                        f.write(command)

            f.write("FastLED.show();\n")
            f.write("FastLED.delay(1000/FRAMES_PER_SECOND")
        print("Write Complete!")

    def ButtonPress(self, x, y):
        global CurrentColor
        print("Received button press at {}:{}".format(x,y))
        self.buttonArray[x][y].configure(bg= CurrentColor)
        self.buttonState[x][y] = CurrentColor
        if not self.buttonState[x][y] == Black:
            self.buttonArray[x][y].configure(relief=tkinter.SUNKEN)
        else:
            self.buttonArray[x][y].configure(relief=tkinter.RAISED)

    def ClearGrid(self):
        for buttonRow in self.buttonArray:
            for button in buttonRow:
                button.configure(relief=tkinter.RAISED,bg=Black)
        for stateRow in self.buttonState:
            for state in stateRow:
                state = Black 

    def GenerateColorPalette(self):
       self.sub = tkinter.Tk()
       self.colorPalette = []
       for y in range(len(ColorState)):
           SetColor = partial(self.SetColor,y)
           self.colorPalette.append(tkinter.Button(
               self.sub,
               command=SetColor))
           self.colorPalette[y].grid(row=0,column=y)
           self.colorPalette[y].config(height=3,width=3,bg=ColorState[y])

    def SetColor(self, y):
        global CurrentColor
        CurrentColor = ColorState[y] 

if __name__ == "__main__":
    start = MainProgram()
