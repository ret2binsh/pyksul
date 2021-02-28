import argparse
import json
import tkinter
from functools import partial
from tkinter.messagebox import showinfo
from tkinter.filedialog import asksaveasfile
from tkinter.filedialog import askopenfile
from string import Template

from src.colors import *
import src.templates as t

ColorNum = len(ColorState)
CurrentColor = Black

class MainProgram:
    '''
        Main program class that handles all tkinter widgets.
        Maintains an internal list of buttons and button
        states in order to keep track of the current drawing.
        Currently handles:
            Adding new animation frames
            Saving current state
            Opening a previous save
            Generating C code based off of a template
            Limited number of colors
            '''

    #inits project space and creates blank "canvas"
    def __init__(self, projname, event=None):
        self.projname = projname
        self.master = tkinter.Tk()
        self.master.title("LED Matrix Creator")
        self.frameCount = 0
        self.framePtr = 0
        self.buttonArray = []
        self.buttonState = []
        self.frameList = []

        #iterate and create a 16x16 grid of buttons
        for x in range(16):
            templist = []
            for y in range(16):
                ButtonPress = partial(self.ButtonPress,x,y)
                templist.append(tkinter.Button(self.master,
                        command=ButtonPress))
                templist[y].grid(row=y,column=x)
                templist[y].config(height=3,width=5,bg=Black)
            self.buttonArray.append(templist)

        # create our first empty state list
        self.CreateEmptyFrame()
        self.buttonState = self.frameList[0]

        # generate all command buttons
        self.printButton = tkinter.Button(self.master,text="Generate",
                command=self.GenerateOutput)
        self.printButton.grid(row=17,column=7)
        self.printButton.config(height=5,width=5)
        self.clearButton = tkinter.Button(self.master,text="Clear",
                command=self.ClearGrid)
        self.clearButton.grid(row=17,column=8)
        self.clearButton.config(height=5,width=5)
        self.exitButton = tkinter.Button(self.master,text="Exit",
                command=self.Exit)
        self.exitButton.grid(row=17,column=15)
        self.exitButton.config(height=5,width=5)
        self.saveButton = tkinter.Button(self.master, text="save",
                command=self.Save)
        self.saveButton.grid(row=17, column=14)
        self.saveButton.config(height=5,width=5)
        self.openButton = tkinter.Button(self.master, text="open",
                command=self.Open)
        self.openButton.grid(row=17,column=13)
        self.openButton.config(height=5,width=5)

        # create animation frame display
        self.newFrame = tkinter.Button(self.master, text="+", command=self.NewFrame)
        self.newFrame.grid(row=17,column=0)
        self.newFrame.config(height=5,width=5)
        self.frameLabel = tkinter.Label(self.master, text="Frame")
        self.frameLabel.grid(row=17,column=1)
        self.frameLabel.config(height=5,width=5)
        self.currentFrame = tkinter.Label(self.master, text="1/1")
        self.currentFrame.grid(row=17,column=2)
        self.currentFrame.config(height=5,width=5)

        # create previous and next buttons for toggling through frames
        self.prev = tkinter.Button(self.master,text="<", command=self.Previous)
        self.prev.grid(row=17,column=3)
        self.prev.config(height=5,width=5)
        self.next = tkinter.Button(self.master,text=">", command=self.Next)
        self.next.grid(row=17,column=4)
        self.next.config(height=5,width=5)

        # generate the color palette and start main program
        self.GenerateColorPalette()
        self.master.mainloop()

    def NewFrame(self):
        ''' Build new empty frame and add to list '''
        self.CreateEmptyFrame()
        self.currentFrame.configure(text="{}/{}".format(self.framePtr+1,self.frameCount))

    def Previous(self):
        ''' Toggle to previous frame '''
        self.framePtr = (self.framePtr - 1) % len(self.frameList)
        self.UpdateFrame(self.framePtr)
        self.currentFrame.configure(text="{}/{}".format(self.framePtr+1,self.frameCount))

    def Next(self):
        ''' Toggle to next frame '''
        self.framePtr = (self.framePtr + 1) % len(self.frameList)
        self.UpdateFrame(self.framePtr)
        self.currentFrame.configure(text="{}/{}".format(self.framePtr+1,self.frameCount))

    def CreateEmptyFrame(self):
        ''' Build empty frame list, append to list, increment count '''
        emptyFrame = []
        for x in range(16):
            stateInit = []
            for y in range(16):
                stateInit.append(Black)
            emptyFrame.append(stateInit)
        self.frameList.append(emptyFrame)
        self.frameCount += 1

    def UpdateFrame(self,frameIndex):
        ''' Update the current view with the new state '''
        self.buttonState = self.frameList[frameIndex]
        for y in range(16):
            for x in range(16):
                self.buttonArray[x][y].configure(bg=self.buttonState[x][y])

    def GenerateOutput(self):
        '''
            Generate and export the C code.
            Utilizes a template and builds according to the WS2812b 16x16
            array. This array snakes back and forth rather than counting
            left to right on each row. '''
            
        filetyp = [("C File","*.c")]
        saveFile = asksaveasfile(initialdir="output",filetypes=filetyp,defaultextension=filetyp)
        body = ""
        for state in self.frameList:
            for y in range(16):
                for x in range(16):
                    if y % 2 == 0:
                        ledNum = (y * 16) + (15 - x)
                    else:
                        ledNum = (y * 16) + x
                    #color = int(self.buttonState[y][x][1:],16)
                    color = int(state[x][y][1:],16)
                    if color:
                        body += Template(t.c_frame).substitute(led_current=ledNum,color=color)
            body += t.c_show
            body += t.c_clear
        output = Template(t.c_output).substitute(project_name=self.projname,body=body)
        saveFile.write(output)
        showinfo("Success","Saved as {}".format(saveFile.name))
        saveFile.close()

    def ButtonPress(self, x, y):
        ''' Update button color according to current color '''
        global CurrentColor
        self.buttonArray[x][y].configure(bg= CurrentColor)
        self.buttonState[x][y] = CurrentColor

    def ClearGrid(self):
        ''' Reset the current frame to blank state '''
        for buttonRow in self.buttonArray:
            for button in buttonRow:
                button.configure(bg=Black)
        for y in range(16):
            for x in range(16):
                self.buttonState[x][y] = Black

    def GenerateColorPalette(self):
        ''' Build the color palette based off of current colors '''
        #TODO: Generate true 0,0,0 - 255,255,255 color palette
        self.colorPalette = []
        for y in range(len(ColorState)):
            SetColor = partial(self.SetColor,y)
            self.colorPalette.append(tkinter.Button(
                self.master,
                command=SetColor))
            self.colorPalette[y].grid(row=18,column=y)
            self.colorPalette[y].config(height=5,width=5,bg=ColorState[y])

    def Save(self):
        ''' Save the current animation as a json dump '''
        filetyp = [("Dat file","*.dat")]
        fname = asksaveasfile(initialdir="saves",filetypes=filetyp, defaultextension=filetyp)
        try:
            json.dump(self.frameList,fname)
            showinfo("Success","Saved file as: {}".format(fname.name))
        except:
            showinfo("Error","Failed to save file: {}".format(fname.name))
        fname.close()

    def Open(self):
        ''' Open and update display from a json dump file '''
        filetyp = [("Dat file","*dat")]
        with askopenfile(initialdir="saves",filetypes=filetyp) as f:
            try:
                self.frameList = json.load(f)
            except:
                showinfo("Error","Failed to parse save file")
        self.frameCount = len(self.frameList)
        self.framePtr = 0
        self.UpdateFrame(0)
        self.currentFrame.configure(text="{}/{}".format(self.framePtr+1,self.frameCount))

    def SetColor(self, y):
        ''' Set the current color '''
        global CurrentColor
        CurrentColor = ColorState[y] 

    def Exit(self):
        ''' Gracefully destroy all tkinter objects '''
        self.master.destroy()

def getargs():

    p = argparse.ArgumentParser("\nPyksul - A 16x16 animation generator.\n" +\
            "This program provides the ability to quickly design\n" +\
            "animations for the 16x16 WS2812b matrix.\n")
    p.add_argument("-p", dest="pname", default="default",
            help="project name for current workspace.")
    return p.parse_args()

if __name__ == "__main__":

    args = getargs()
    start = MainProgram(args.pname)
