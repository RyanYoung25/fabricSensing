#!/usr/bin/env python

import serial
import time
from Maestor import maestor

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
        #Create variables for moving the arm
        self.currentPos = -.75
        self.posMax = -1.7
        self.posMin = -.1
        self.increment = -.05
        #Create the maestor object to talk to MAESTOR
        self.robot = maestor()
        self.robot.setProperty("LEP", "position", self.currentPos)
        #Open up the serial connection 
        try:
            self.ser.open()
        except Exception, e:
            print "Serial Connection could not be opened: " + str(e)

    def moveArmUp(self):
        #Increment the arm up
        self.currentPos += self.increment

        if self.currentPos < self.posMax: #less than because it's all negative
            self.currentPos = self.posMax

        self.robot.setProperty("LEP", "position", self.currentPos)

    def moveArmDown(self):
        #Increment the arm down
        self.currentPos -= self.increment

        if self.currentPos > self.posMin: #less than because it's all negative
            self.currentPos = self.posMin

        self.robot.setProperty("LEP", "position", self.currentPos)


    def readAndRespond(self):
        """ Read a message from the serial port and 
        respond with the correct movement from the robot.
        """

        if self.ser.isOpen():
            try:
                #Try to read
                self.ser.flushOutput()
                response = self.ser.readline()
                print response
                if response.strip() == "up":
                    self.moveArmUp()
                    print "Moving Up!"
                elif response.strip() == "down":
                    self.moveArmDown()
                    print "Moving Down!"
            except Exception, e:
                print "Error: " + str(e)

def mainDemo():
    demoSensor = fabricSensor()
    continuing = True
    while continuing: 
        demoSensor.readAndRespond()
        time.sleep(.1)

if __name__ == '__main__':
    mainDemo()








        
