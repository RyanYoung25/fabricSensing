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
        #Create variables for moving the elbow
        self.elbowCurrentPos = -.75
        self.elbowPosMax = -1.7
        self.elbowPosMin = -.1
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
        #Create the maestor object to talk to MAESTOR
        self.robot = maestor()

        self.robot.setProperty("REP", "velocity", .5)
        self.robot.setProperty("RSP", "velocity", .5)
        self.robot.setProperty("RSR", "velocity", .5)
        self.robot.setProperty("RSY", "velocity", .5)

        self.robot.setProperty("REP", "position", self.elbowCurrentPos)
        self.robot.setProperty("RSP", "position", self.RSPCurrentPos)
        self.robot.setProperty("RSR", "position", self.RSRCurrentPos)
        self.robot.setProperty("RSY", "position", self.RSYCurrentPos)


        #Create a list of the functions to call map to each sensor number
        self.responses = [self.moveElbowUp, self.moveElbowDown, self.doNothing, self.doNothing, self.doNothing, self.doNothing, self.doNothing, self.doNothing ] #self.moveRSYRight, self.moveRSYLeft, self.moveRSRUp, self.moveRSRDown, self.moveRSPUp, self.moveRSPDown]
        self.thresholds = [2, 2, 2, 2, 2, 2, 2, 2]
        #Open up the serial connection 
        try:
            self.ser.open()
        except Exception, e:
            print "Serial Connection could not be opened: " + str(e)

    def moveElbowUp(self):
        #Increment the Elbow up
        self.elbowCurrentPos += self.increment

        if self.elbowCurrentPos < self.elbowPosMax: #less than because it's all negative
            self.elbowCurrentPos = self.elbowPosMax

        self.robot.setProperty("REP", "position", self.elbowCurrentPos)


    def moveElbowDown(self):
        #Increment the Elbow down
        self.elbowCurrentPos -= self.increment

        if self.elbowCurrentPos > self.elbowPosMin: #less than because it's all negative
            self.elbowCurrentPos = self.elbowPosMin

        self.robot.setProperty("REP", "position", self.elbowCurrentPos)


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

    def cleanUp(self):
        self.robot.setProperties("RSP REP LEP", "position position position", "0 0 0")


    def parseString(self, responseString):
        values = responseString.split(" ")

        if len(values) != 8:
            print "Error on serial read string" 
            return

        count = 0
        #Loop through the input and do the right thing 
        while count < 8:
            val = float(values[count])

            if val > self.thresholds[count]:
                #Update the threshold TODO: make this better
                self.thresholds[count] = val - .5
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
    demoSensor.cleanUp()

if __name__ == '__main__':
    mainDemo()








        
