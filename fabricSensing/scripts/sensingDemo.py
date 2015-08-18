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
        #Create variables for moving the LEP
        self.LEPCurrentPos = -.75
        self.LEPPosMax = -1.7
        self.LEPPosMin = -.1

        #Create the maestor object to talk to MAESTOR
        self.robot = maestor()

        self.robot.setProperty("REP", "velocity", .5)
        self.robot.setProperty("RSP", "velocity", .5)
        self.robot.setProperty("LEP", "velocity", .5)

        self.robot.setProperty("REP", "position", self.elbowCurrentPos)
        self.robot.setProperty("RSP", "position", self.RSPCurrentPos)
        self.robot.setProperty("LEP", "position", self.LEPCurrentPos)


        #Create a list of the functions to call map to each sensor number
        self.responses = [self.moveElbowUp, self.moveElbowDown, self.doNothing, self.doNothing, self.moveLEPUp, self.moveLEPDown, self.doNothing, self.doNothing ] #self.moveRSYRight, self.moveRSYLeft, self.moveRSRUp, self.moveRSRDown, self.moveRSPUp, self.moveRSPDown]
        self.thresholds = [False, False, False, False, False, False, False, False]
        self.THRESHOLD = 2
        #Create a list of previous values, This will be used to calculate the local slope at each step
        # which is our analog to the derivative.
        self.history = [0, 0, 0, 0, 0, 0, 0, 0]
        self.smoothing = [6, 6, 6, 6, 6, 6, 6, 6]
        self.alpha = .3 
        #Open up the serial connection 
        try:
            self.ser.open()
            self.initializeHistory()
        except Exception, e:
            print "Serial Connection could not be opened: " + str(e)


    def initializeHistory(self):
        '''
        Read values from serial and start this as the first history values
        '''
        if self.ser.isOpen():
            try:
                #Try to read
                self.ser.flushOutput()
                response = self.ser.readline()
                #Once the line is read we can parse the string and initalize the data
                currentValues = response.split(" ")

                count = 0
                #Loop through the input and set the history
                while count < 8:
                    val = float(currentValues[count])
                    self.history[count] = val
                    #self.smoothing[count] = val
                    count += 1
                
            except Exception, e:
                print "Error: " + str(e)

    '''
    Here begins the functions that move the joints on hubo. 
    There probably could be a better way of compressing these but for now 
    it works. They all do the same thing and for incrementing work. 
    '''

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

    def moveLEPUp(self):
        self.LEPCurrentPos += self.increment

        if self.LEPCurrentPos < self.LEPPosMax: #less than because it's all negative
            self.LEPCurrentPos = self.LEPPosMax

        self.robot.setProperty("LEP", "position", self.LEPCurrentPos)


    def moveLEPDown(self):
        self.LEPCurrentPos -= self.increment

        if self.LEPCurrentPos > self.LEPPosMin: #less than because it's all negative
            self.LEPCurrentPos = self.LEPPosMin

        self.robot.setProperty("LEP", "position", self.LEPCurrentPos)



    def doNothing(self):
        pass


    def readAndRespond(self):
        """ 
        Read a message from the serial port and 
        respond with the correct movement from the robot.
        """

        if self.ser.isOpen():
            try:
                #Try to read
                self.ser.flushOutput()
                response = self.ser.readline()
                #Once the line is read we can parse the string and process the data
                self.parseString(response)
                
            except Exception, e:
                print "Error: " + str(e)

    def cleanUp(self):
        self.robot.setProperties("RSP REP LEP", "position position position", "0 0 0")


    def determineTouch(self, value, index):
        '''
        Check if the derivative, the rate of change over time, passed
        a determined threshold. This is the easiest way but we can start
        to expand this by creating a dynamic threshold.
        '''

        #If the sensor failed and returns a zero ignore this data point. 
        if value == 0:  
            return False

        difference = value - self.smoothing[index] #The derivative 
        self.history[index] = value #Update the history
        
        

        #If the difference is larger than the normal threshold then say we have a touch. 
        if difference > self.THRESHOLD or value >= 11:
            self.thresholds[index] = True
        else:
            self.thresholds[index] = False
            #Only add the moving average if we don't think there is a touch. 
            self.smoothing[index] = self.alpha * value + (1 - self.alpha)*self.smoothing[index] #Exponential Moving Average


        return self.thresholds[index]


    def parseString(self, responseString):
        '''
        Parse the serial string from the robot and cast the values 
        to floats. For each of the floats determine if there was a touch.

        If there was a touch call the corresponding response function.
        '''
        values = responseString.split(" ")

        if len(values) != 8:
            print "Error on serial read string" 
            return

        count = 0
        print responseString
        #Loop through the input and do the right thing 
        while count < 8:
            val = float(values[count])

            if self.determineTouch(val, count):
                #Call the function
                self.responses[count]()
            #Increment the counter
            count += 1

        print self.smoothing

    def cleanUp(self):
        '''
        Reset the robot joints back to zero and reset for the next demo.
        '''

        self.robot.setProperties("RSP REP LEP", "position position position", "0 0 0")


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








        
