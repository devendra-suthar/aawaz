#include "CurieIMU.h"

boolean blinkState = false;          // state of the LED
int calibrateOffsets = 1; // int to determine whether calibration takes place or not

unsigned long loopTime = 0;          // get the time since program started
unsigned long interruptsTime = 0;    // get the time when motion event is detected

int axRaw, ayRaw, azRaw, gxRaw, gyRaw, gzRaw;
float ax, ay, az, gx, gy, gz;

int orientation = - 1;   // the board's orientation
int motion = -1;         // the direction offset value

void setup() {
  Serial.begin(9600); // initialize Serial communication
  while(!Serial) ;    // wait for serial port to connect.
  // Initialise the IMU
  CurieIMU.begin();
  CurieIMU.attachInterrupt(eventCallback);

  // Increase Accelerometer range to allow detection of stronger taps (< 4g)
  CurieIMU.setAccelerometerRange(4);

  // Reduce threshold to allow detection of weaker taps (>= 750mg)
  CurieIMU.setDetectionThreshold(CURIE_IMU_DOUBLE_TAP, 750); // (750mg)

  // Set the quite time window for 2 taps to be registered as a double-tap (Gap time between taps <= 1000 milliseconds)
  CurieIMU.setDetectionDuration(CURIE_IMU_DOUBLE_TAP, 1000);

  // Enable Double-Tap detection
  CurieIMU.interrupts(CURIE_IMU_DOUBLE_TAP);

  /* Enable Motion Detection */
  CurieIMU.setDetectionThreshold(CURIE_IMU_MOTION, 20); // 20mg
  CurieIMU.setDetectionDuration(CURIE_IMU_MOTION, 10);  // trigger times of consecutive slope data points
  CurieIMU.interrupts(CURIE_IMU_MOTION);
  
  Serial.println("IMU initialization complete, waiting for events...");
}

void loop() {
  // if motion is detected in 1000ms, LED will be turned up
  loopTime = millis();
  if(abs(loopTime -interruptsTime) < 1000 )
    blinkState = true;
  else
    blinkState = false;
  digitalWrite(13, blinkState);
}

static void eventCallback()
{
  if (CurieIMU.getInterruptStatus(CURIE_IMU_DOUBLE_TAP)) {
     Serial.println("DoubleTapDetected sorry");
  }
  else if (CurieIMU.getInterruptStatus(CURIE_IMU_MOTION)) {
    getMotionAxis();
    
    // read raw accel/gyro measurements from device
    CurieIMU.readMotionSensor(axRaw, ayRaw, azRaw, gxRaw, gyRaw, gzRaw);
    getOrientation();

    convertAccelerometerRawData();
    convertGyrometerRawData();
    
    Serial.print("Detecting_Gesture: ");
    Serial.print(axRaw);
    Serial.print(" ");
    Serial.print(ayRaw);
    Serial.print(" ");
    Serial.print(azRaw);
    Serial.print(" ");
    Serial.print(gx);
    Serial.print(" ");
    Serial.print(gy);
    Serial.print(" ");
    Serial.print(gz);
    Serial.print(" ");
    Serial.print(orientation);
    Serial.print(" ");
    Serial.println(motion);
    interruptsTime = millis(); 
  }
 }

void convertAccelerometerRawData(){
 ax = (axRaw/32768.0)*CurieIMU.getAccelerometerRange(); 
 ay = (ayRaw/32768.0)*CurieIMU.getAccelerometerRange() ;
 az = (azRaw/32768.0)*CurieIMU.getAccelerometerRange() ;
}

void convertGyrometerRawData(){
  gx = (gxRaw/32768.9)*CurieIMU.getGyroRange() ;
  gy = (gyRaw/32768.9)*CurieIMU.getGyroRange() ;
  gz = (gzRaw/32768.9)*CurieIMU.getGyroRange() ;
}

void getOrientation(){
  /*
    the below values are taken as large as possible so that,
    they do not get assumed to be same while applying various AI algo's
    */
  
    /*
      The orientations of the board:
      0000: flat, processor facing up
      1000: flat, processor facing down
      2000: landscape, analog pins down
      3000: landscape, analog pins up
      4000: portrait, USB connector up
      5000: portrait, USB connector down
    */
  // calculate the absolute values, to determine the largest
    int absX = abs(axRaw);
    int absY = abs(ayRaw);
    int absZ = abs(azRaw);

    if ( (absZ > absX) && (absZ > absY)) {
      // base orientation on Z
      if (azRaw > 0) {
        //"up"
        orientation = 0000;  
      } else {
        //"down"
        orientation = 1000;
      }
    } else if ( (absY > absX) && (absY > absZ)) {
      // base orientation on Y
      if (ayRaw > 0) {
        //"digital pins up"
        orientation = 2000;
      } else {
        //"analog pins up"
        orientation = 3000;
      }
    } else {
      // base orientation on X
      if (axRaw < 0) {
        //"connector up"
        orientation = 4000;
      } else {
        //"connector down"
        orientation = 5000;
      }
    }
}

 void getMotionAxis(){
  /*
    the below values are taken as large as possible so that,
    they do not get assumed to be same while applying various AI algo's
  */
    
  /*
      The motion values of the board 
      0000: Positive motion detected on X-axis
      1000: Negative motion detected on X-axis
      2000: Positive motion detected on Y-axis
      3000: Negative motion detected on Y-axis
      4000: Positive motion detected on Z-axis
      5000: Negative motion detected on Z-axis
  */
  //Detecting direction of motion, and sending an assumed value for that particular motion
      if (CurieIMU.motionDetected(X_AXIS, POSITIVE))
        motion = 0000;
      if (CurieIMU.motionDetected(X_AXIS, NEGATIVE))
        motion = 1000;
      if (CurieIMU.motionDetected(Y_AXIS, POSITIVE))
        motion = 2000;
      if (CurieIMU.motionDetected(Y_AXIS, NEGATIVE))
        motion = 3000;
      if (CurieIMU.motionDetected(Z_AXIS, POSITIVE))
        motion = 4000;
      if (CurieIMU.motionDetected(Z_AXIS, NEGATIVE))
        motion = 5000;  
 }

void calibrate(){
  // use the code below to calibrate accel/gyro offset values
  if (calibrateOffsets == 1) {
    Serial.println("Internal sensor offsets BEFORE calibration...");
    Serial.print(CurieIMU.getAccelerometerOffset(X_AXIS));
    Serial.print("\t"); // -76
    Serial.print(CurieIMU.getAccelerometerOffset(Y_AXIS));
    Serial.print("\t"); // -235
    Serial.print(CurieIMU.getAccelerometerOffset(Z_AXIS));
    Serial.print("\t"); // 168
    Serial.print(CurieIMU.getGyroOffset(X_AXIS));
    Serial.print("\t"); // 0
    Serial.print(CurieIMU.getGyroOffset(Y_AXIS));
    Serial.print("\t"); // 0
    Serial.println(CurieIMU.getGyroOffset(Z_AXIS));

    // To manually configure offset compensation values,
    // use the following methods instead of the autoCalibrate...() methods below
    //CurieIMU.setAccelerometerOffset(X_AXIS,495.3);
    //CurieIMU.setAccelerometerOffset(Y_AXIS,-15.6);
    //CurieIMU.setAccelerometerOffset(Z_AXIS,491.4);
    //CurieIMU.setGyroOffset(X_AXIS,7.869);
    //CurieIMU.setGyroOffset(Y_AXIS,-0.061);
    //CurieIMU.setGyroOffset(Z_AXIS,15.494);

    Serial.println("About to calibrate. Make sure your board is stable and upright");
    delay(5000);

    // The board must be resting in a horizontal position for
    // the following calibration procedure to work correctly!
    Serial.print("Starting Gyroscope calibration and enabling offset compensation...");
    CurieIMU.autoCalibrateGyroOffset();
    Serial.println(" Done");

    Serial.print("Starting Acceleration calibration and enabling offset compensation...");
    CurieIMU.autoCalibrateAccelerometerOffset(X_AXIS, 0);
    CurieIMU.autoCalibrateAccelerometerOffset(Y_AXIS, 0);
    CurieIMU.autoCalibrateAccelerometerOffset(Z_AXIS, 1);
    Serial.println(" Done");

    Serial.println("Internal sensor offsets AFTER calibration...");
    Serial.print(CurieIMU.getAccelerometerOffset(X_AXIS));
    Serial.print("\t"); // -76
    Serial.print(CurieIMU.getAccelerometerOffset(Y_AXIS));
    Serial.print("\t"); // -2359
    Serial.print(CurieIMU.getAccelerometerOffset(Z_AXIS));
    Serial.print("\t"); // 1688
    Serial.print(CurieIMU.getGyroOffset(X_AXIS));
    Serial.print("\t"); // 0
    Serial.print(CurieIMU.getGyroOffset(Y_AXIS));
    Serial.print("\t"); // 0
    Serial.println(CurieIMU.getGyroOffset(Z_AXIS));
  }
}

