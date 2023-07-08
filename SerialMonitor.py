########################################################################
# Author: Zac Lynn
# Date:   7/7/2023
# 
# Description: Simple serial port monitor that can view and save data
#                   on a single channel. Saved data is stored as a 
#                   binary file. To save txt change the file access mode
#                   and file extension.
########################################################################
import tkinter as tk
import tkinter.scrolledtext as st
from tkinter import *
from tkinter import ttk

import serial
import time
import serial.tools.list_ports

import threading

class SerialMonitor():
    serialConnect = False
    captureData = False
    portName = None
    availablePorts = None
    window = None


    def __init__(self, ):
        self.window = tk.Tk()
        self.window.title("Serial Data Capture")
        self.window.config(bg="blue4")

        self.setupLeftFrame()
        self.setupRightFrame()
        self.window.mainloop()


    def setupLeftFrame(self): 
        self.leftFrame = Frame(self.window, bg = "blue4", height = 600, width = 600)
        self.upperFrame = Frame(self.leftFrame, bg= "grey", height = 300, width = 600)
        self.lowerFrame = Frame(self.leftFrame, bg= "white", height = 300, width = 600)

        self.connectedButton = tk.Button(self.upperFrame, text = "Connect", command=lambda: self.connectToSerialPort())
        self.disconnectedButton = tk.Button(self.upperFrame, text = "Disconnect", command=lambda: self.disconnectFromSerialPort())
        self.checkPortsButton = tk.Button(self.upperFrame, text = "Check Ports", command=lambda: self.checkPorts())

        # Creating scrolled text area
        self.availablePortsLabel = st.ScrolledText(self.upperFrame, width = 30, height = 5, font = ("Times New Roman", 9))
        self.availablePortsLabel.insert('1.0', "Available Ports: Check Ports!")

        self.portSelectionLabel = tk.Label(self.upperFrame, text = "Port Selection: ", bg="grey")

        # spinbox
        self.portSelection = tk.StringVar()
        self.portSpinBox = ttk.Spinbox(self.upperFrame, from_ = 0, to = 0, 
                            increment=1, textvariable = self.portSelection, wrap=True)

        self.outputFilenameEntryLabel = tk.Label(self.lowerFrame, text = "Output file name: ", bg="white")
        self.outputFilenameEntry = tk.Entry(self.lowerFrame)
        self.outputFilenameEntry.insert("end", "test")

        self.stopButton = tk.Button(self.lowerFrame, text = "Stop Data Capture", command=lambda: self.setDataCaptureFlag(0))
        self.startButton = tk.Button(self.lowerFrame, text = "Start Data Capture", command=lambda: self.setDataCaptureFlag(1))
        self.dataCaptureLabel = tk.Label(self.lowerFrame, text = "   ", bg="red")

        # Frames
        self.leftFrame.grid(row = 0, column = 0, padx = 10, pady = 5)
        self.upperFrame.grid(row = 0, column = 0, padx = 10, pady = 5)
        self.lowerFrame.grid(row = 1, column = 0, padx = 10, pady = 5)

        # Upper frame
        self.checkPortsButton.grid(row = 0, column = 0, padx = 10, pady = 5)
        self.availablePortsLabel.grid(row = 0, column = 1, padx = 10, pady = 5)

        self.portSelectionLabel.grid(row = 1, column = 0, padx = 10, pady = 5)
        self.portSpinBox.grid(row = 1, column = 1, padx = 10, pady = 5)

        self.connectedButton.grid(row = 2, column = 0, padx = 10, pady = 5)
        self.disconnectedButton.grid(row = 2, column = 1, padx = 10, pady = 5)

        # Lower Frame
        self.outputFilenameEntryLabel.grid(row = 0, column = 0, padx = 10, pady = 5)
        self.outputFilenameEntry.grid(row = 0, column = 1, padx = 10, pady = 5)

        self.startButton.grid(row = 1, column = 0, padx = 10, pady = 5)
        self.stopButton.grid(row = 1, column = 1, padx = 10, pady = 5)
        self.dataCaptureLabel.grid(row = 1, column = 2, padx = 10, pady = 5)


    def setupRightFrame(self):
        self.rightFrame = Frame(self.window, height = 600, width = 600)

        self.serialMonitorLabel = tk.Label(self.rightFrame, text = "Serial Output ")

        # Creating scrolled text area
        self.serialOutput = st.ScrolledText(self.rightFrame, width = 100, height = 30, font = ("Times New Roman", 12))

        self.rightFrame.grid(row = 0, column = 1, padx = 10, pady = 5)
        self.serialMonitorLabel.grid(row = 0, column = 0)
        self.serialOutput.grid(row = 1, column = 0)


    # Controls whether or not the serial data is saved to a file
    def setDataCaptureFlag(self, flag):
        self.captureData = flag


    def disconnectFromSerialPort(self):
        self.serialConnect = False


    def connectToSerialPort(self):
        self.portName = self.availablePorts[int(self.portSelection.get()) - 1]
        if (self.portName is None):
            self.serialOutput.delete('1.0', 'end')
            self.serialOutput.insert('end', "Select a serial port!\n")
            self.serialConnect = False
            return
        try:
            self.serialPort = serial.Serial(port = self.portName, baudrate = 115200, timeout=1)
            self.serialPort.close() # Not sure why it has to be closed then opened... Maybe is opened on instantiation of object
            self.serialPort.open()

            self.serialOutput.insert('end', "\nSuccesfully opened serial port: " + str(self.portName) )
            self.serialOutput.yview('end')

            self.serialConnect = True

            t = threading.Thread(name="serialPortThread", target=self.readSerialPort, daemon=True)
            t.start()

        except Exception as e:
            print("Failed to open serial connection with error:\n\n" + str(e))
            self.serialConnect = False


    def checkPorts(self):
        self.availablePorts = [comport.device for comport in serial.tools.list_ports.comports()]
        portNames = ""

        for port in range(len(self.availablePorts)):
            portNames += "\n" + str(port+1) + ": " + str(self.availablePorts[port])

        self.availablePortsLabel.delete('1.0', 'end')
        self.availablePortsLabel.insert('1.0', "Available Ports: " + portNames)
        self.portSpinBox.config(from_ = 1, to = len(self.availablePorts))


    def readSerialPort(self):
        fileIsOpen = False
        fp = None

        while self.serialConnect:
            if (self.serialPort.in_waiting > 0):
                data = self.serialPort.read_until('\n')
                self.serialOutput.insert("end", data) 

                if (fileIsOpen and self.captureData):

                    fp.write(data)

            if (self.captureData and fileIsOpen == False):   
                try:
                    fp = open(self.outputFilenameEntry.get() + ".bin", 'wb')                                # Write in bytes
                    fileIsOpen = True
                    self.dataCaptureLabel.config(bg = "green")
                except Exception as e:
                    print("Error when trying to open output file:\n" + str(e))
            elif (self.captureData == False and fileIsOpen):
                try:
                    fp.close()
                    fileIsOpen = False
                    self.dataCaptureLabel.config(bg = "red")
                except Exception as e:
                    print("Error when trying to open output file:\n" + str(e))
                

            time.sleep(0.2)

        self.serialPort.close()
        self.serialOutput.insert('end', "\nConnection closed on serial port: " + self.portName)


SM = SerialMonitor()
