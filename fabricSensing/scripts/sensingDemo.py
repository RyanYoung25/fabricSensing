#!/usr/bin/env python

import serial
import time
import signal
from Maestor import maestor

continuing = True

class fabricSensor:
    """A class to represent a fabricSensor sensor that talks 
    over serial using and arduino. All the sensor does is send
    serial messages either up or down and causes the robot to move up or down"""
    def __init__(self, port="/dev/ttyACM0", baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1, xonxoff=False):
        #Create and configure the serial reader
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = baudrate
        self.ser.bytesize = bytesize
        self.ser.parity = parity
        self.ser.stopbits = stopbits
        self.ser.timeout = timeout
        self.ser.xonxoff = xonxoff
        #Used for movement
        self.increment = -.1
        #Create variables for moving the REP
        self.REPCurrentPos = -.75
        self.REPPosMax = -1.7
        self.REPPosMin = -.1
        #Create variables for moving the RSP
        self.RSPCurrentPos = 0
        self.RSPPosMax = -1
        self.RSPPosMin = 1
        #Create variables for moving the RSR
        self.RSRCurrentPos = 0
        self.RSRPosMax = -1.3
        self.RSRPosMin = 0
        #Create variables for moving the RSY 
        self.RSYCurrentPos = 0
        self.RSYPosMax = -1.35
        self.RSYPosMin = 1.35
        #Create variables for moving the LEP
        self.LEPCurrentPos = .75
        self.LEPPosMax = 1.7
        self.LEPPosMin = .1
        #Create the maestor object to talk to MAESTOR
        self.robot = maestor()

        self.robot.setProperty("REP", "velocity", .5)
        self.robot.setProperty("RSP", "velocity", .5)
        self.robot.setProperty("RSR", "velocity", .5)
        self.robot.setProperty("RSY", "velocity", .5)
        self.robot.setProperty("LEP", "velocity", .5)

        self.robot.setProperty("REP", "position", self.REPCurrentPos)
        self.robot.setProperty("RSP", "position", self.RSPCurrentPos)
        self.robot.setProperty("RSR", "position", self.RSRCurrentPos)
        self.robot.setProperty("RSY", "position", self.RSYCurrentPos)
        self.robot.setProperty("LEP", "position", self.LEPCurrentPos)

        #Create a list of the functions to call map to each sensor number
        self.responses = [self.moveREPUp, self.moveREPDown, self.moveRSPUp, self.moveRSPDown, self.moveLEPUp, self.moveLEPDown, self.doNothing, self.doNothing ] #self.moveRSYRight, self.moveRSYLeft, self.moveRSRUp, self.moveRSRDown, self.moveRSPUp, self.moveRSPDown]
        self.thresholds = [2, 2, 2, 2, 2, 2, 2, 2]
        #Open up the serial connection 
        try:
            self.ser.open()
        except Exception, e:
            print "Serial Connection could not be opened: " + str(e)

    def moveREPUp(self):
        #Increment the Right Elbow up
        self.REPCurrentPos += self.increment

        if self.REPCurrentPos < self.REPPosMax: #less than because it's all negative
            self.REPCurrentPos = self.REPPosMax

        self.robot.setProperty("REP", "position", self.REPCurrentPos)


    def moveREPDown(self):
        #Increment the Right Elbow down
        self.REPCurrentPos -= self.increment

        if self.REPCurrentPos > self.REPPosMin: #less than because it's all negative
            self.REPCurrentPos = self.REPPosMin

        self.robot.setProperty("REP", "position", self.REPCurrentPos)


    def moveRSPUp(self):

        self.RSPCurrentPos += self.increment

        if self.RSPCurrentPos < self.RSPPosMax: 
            self.RSPCurrentPos = self.RSPPosMax

        self.robot.setProperty("RSP", "position", self.RSPCurrentPos)


    def moveRSPDown(self):
        self.RSPCurrentPos -= self.increment

        if self.RSPCurrentPos > self.RSPPosMin: #less than because it's all negative
            self.RSPCurrentPos = self.RSPPosMin

        self.robot.setProperty("RSP", "position", self.RSPCurrentPos)

    def moveRSRUp(self):
        self.RSRCurrentPos += self.increment

        if self.RSRCurrentPos < self.RSRPosMax: #less than because it's all negative
            self.RSRCurrentPos = self.RSRPosMax

        self.robot.setProperty("RSR", "position", self.RSRCurrentPos)


    def moveRSRDown(self):
        self.RSRCurrentPos -= self.increment

        if self.RSRCurrentPos > self.RSRPosMin: #less than because it's all negative
            self.RSRCurrentPos = self.RSRPosMin

        self.robot.setProperty("RSR", "position", self.RSRCurrentPos)


    def moveRSYRight(self):
        self.RSYCurrentPos -= self.increment

        if self.RSYCurrentPos < self.RSYPosMax: #less than because it's all negative
            self.RSYCurrentPos = self.RSYPosMax

        self.robot.setProperty("RSY", "position", self.RSYCurrentPos)


    def moveRSYLeft(self):
        self.RSYCurrentPos += self.increment

        if self.RSYCurrentPos > self.RSYPosMin: #less than because it's all negative
            self.RSYCurrentPos = self.RSYPosMin

        self.robot.setProperty("RSY", "position", self.RSYCurrentPos)
        
    def moveLEPUp(self):
        #Increment the Left Elbow up
        self.LEPCurrentPos += self.increment

        if self.LEPCurrentPos < self.LEPPosMax: #less than because it's all negative
            self.LEPCurrentPos = self.LEPPosMax

        self.robot.setProperty("LEP", "position", self.LEPCurrentPos)
        
    def moveLEPDown(self):
        #Increment the Left Elbow down
        self.LEPCurrentPos -= self.increment

        if self.LEPCurrentPos > self.LEPPosMin: #less than because it's all negative
            self.LEPCurrentPos = self.LEPPosMin

        self.robot.setProperty("LEP", "position", self.LEPCurrentPos)
    
    def doNothing(self):
        pass


    def readAndRespond(self):
        """ Read a message from the serial port and 
        respond with the correct movement from the robot.
        """

        if self.ser.isOpen():
            try:
                #Try to read
                self.ser.flushOutput()
                response = self.ser.readline()
                self.parseString(response)
                print response
                #if response.strip() == "up":
                #    self.moveArmUp()
                #    print "Moving Up!"
                #elif response.strip() == "down":
                #    self.moveArmDown()
                #    print "Moving Down!"
            except Exception, e:
                print "Error: " + str(e)


    def parseString(self, responseString):
        values = responseString.split(" ")

        if len(values) != 8:
            print "Error on serial read string" 
            return

        count = 0
        #Loop through the input and do the right thing 
        while count < 8:
            val = bool(values[count])

            if val == True
                #Update the threshold TODO: make this better
                #self.thresholds[count] = val - .5
                #Call the function
                self.responses[count]()
            #Increment the counter
            count += 1


def finishDemo(signum, frame):
    global continuing
    continuing = False

def mainDemo():
    global continuing
    signal.signal(signal.SIGINT, finishDemo)
    demoSensor = fabricSensor()
    continuing = True
    while continuing: 
        demoSensor.readAndRespond()
        #time.sleep(.1)

if __name__ == '__main__':
    mainDemo()








        
