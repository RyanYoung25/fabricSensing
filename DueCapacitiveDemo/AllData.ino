#include <CapacitiveSensor.h>

#define NOPS 8
#define SAMPLES 30

// Send pins
int sp0 = 22;
int sp1 = 26;
int sp2 = 30;
int sp3 = 34;
int sp4 = 38;
int sp5 = 42;
int sp6 = 46;
int sp7 = 50;

// Receive pins
int rp0 = 24;
int rp1 = 28;
int rp2 = 32;
int rp3 = 36;
int rp4 = 40;
int rp5 = 44;
int rp6 = 48;
int rp7 = 52;

float initEMA = 20;
float a = 0.1;
float diff = 2;
float threshold = 11.0;

long total[NOPS];
float logTotal[NOPS];
float logTotalEMA[NOPS] = { initEMA, initEMA, initEMA, initEMA, initEMA, initEMA, initEMA, initEMA };
float hold[NOPS];
bool isTouched[NOPS] = { false, false, false, false, false, false, false, false };

const char sep = ' ';

// 
CapacitiveSensor block0 = CapacitiveSensor(sp0, rp0);
CapacitiveSensor block1 = CapacitiveSensor(sp1, rp1);
CapacitiveSensor block2 = CapacitiveSensor(sp2, rp2);
CapacitiveSensor block3 = CapacitiveSensor(sp3, rp3);
CapacitiveSensor block4 = CapacitiveSensor(sp4, rp4);
CapacitiveSensor block5 = CapacitiveSensor(sp5, rp5);
CapacitiveSensor block6 = CapacitiveSensor(sp6, rp6);
CapacitiveSensor block7 = CapacitiveSensor(sp7, rp7);

void setup() {
  // put your setup code here, to run once:  
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  
  //REP UP 0 solidBrown
  //REP Down 1 twistedGreen
  //RSY Right 2 solidGreen
  //RSY Left 3 twistedBrown
  //RSR up solidOrange
  //rsr down twistedBlue
  //RSP up twistedOrange
  //RSP down solidBlue
  
  // Firing pattern to minimize cross-talk - seems to work...
  total[0] = block0.capacitiveSensor(SAMPLES); // 0
  total[2] = block2.capacitiveSensor(SAMPLES); // 2
  total[4] = block4.capacitiveSensor(SAMPLES); // 4
  total[6] = block6.capacitiveSensor(SAMPLES); // 6
  total[1] = block1.capacitiveSensor(SAMPLES); // 1
  total[3] = block3.capacitiveSensor(SAMPLES); // 3
  total[5] = block5.capacitiveSensor(SAMPLES); // 5
  total[7] = block7.capacitiveSensor(SAMPLES); // 7
  
  if (!getLogTotal()) {
    printValues(logTotal);    
  }
    
  // Arbitrary delay
  delay(100);
}

void printValues(float *output) {
  for (int i = 0; i < NOPS-1; i++) {
    Serial.print(output[i]);
    Serial.print(sep);
  }
  Serial.println(output[NOPS-1]);
}

long getLogTotal(void) {
  for (int i = 0; i < NOPS; i++) {
    // Return the first instance of an error value when encountered (<0)
    if (total[i] >= 0) {
      logTotal[i] = log(total[i] + 1.0);
    } else {
      return total[i];
    }
  }
  // Return 0 upon completion
  return 0;
}


