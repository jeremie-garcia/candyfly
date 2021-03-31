#include <FastLED.h>

#define NUM_LEDS_PER_STRIP 3

CRGB UpLeds[NUM_LEDS_PER_STRIP];
CRGB DownLeds[NUM_LEDS_PER_STRIP];
CRGB Yaw_no_clockLeds[NUM_LEDS_PER_STRIP];
CRGB Yaw_clockLeds[NUM_LEDS_PER_STRIP];
CRGB FrontLeds[NUM_LEDS_PER_STRIP];
CRGB BackLeds[NUM_LEDS_PER_STRIP];
CRGB LeftLeds[NUM_LEDS_PER_STRIP];
CRGB RightLeds[NUM_LEDS_PER_STRIP];


int buttonPin = 10;

int fsrReadingUp = 0;
int fsrReadingDown = 0;
int fsrReadingYaw_no_clock = 0;
int fsrReadingYaw_clock = 0;
int fsrReadingFront = 0;
int fsrReadingBack = 0;
int fsrReadingLeft = 0;
int fsrReadingRight = 0;
int buttonReading = 0;

void setup() {
    
   // void setup for LED strips
    FastLED.addLeds<WS2812B, 2, GRB>(UpLeds, NUM_LEDS_PER_STRIP);
    FastLED.addLeds<WS2812B, 3, GRB>(DownLeds, NUM_LEDS_PER_STRIP);
    FastLED.addLeds<WS2812B, 4, GRB>(Yaw_no_clockLeds, NUM_LEDS_PER_STRIP);
    FastLED.addLeds<WS2812B, 5, GRB>(Yaw_clockLeds, NUM_LEDS_PER_STRIP);
    FastLED.addLeds<WS2812B, 6, GRB>(FrontLeds, NUM_LEDS_PER_STRIP);
    FastLED.addLeds<WS2812B, 7, GRB>(BackLeds, NUM_LEDS_PER_STRIP);
    FastLED.addLeds<WS2812B, 8, GRB>(LeftLeds, NUM_LEDS_PER_STRIP);
    FastLED.addLeds<WS2812B, 9, GRB>(RightLeds, NUM_LEDS_PER_STRIP);
    FastLED.setMaxPowerInVoltsAndMilliamps(5, 500);
    FastLED.clear();
    FastLED.show();
    // void setup reading
    Serial.begin(9600);
    pinMode(buttonPin, INPUT);
}



void loop() {

  //Reading of FSR sensor
  fsrReadingUp = analogRead(7);
  fsrReadingDown = analogRead(6);
  //fsrReadingYaw_no_clock = analogRead(5);
  //fsrReadingYaw_clock= analogRead(4);
  //fsrReadingFront = analogRead(3);
  //fsrReadingBack = analogRead(2);
  fsrReadingLeft = analogRead(1);
  fsrReadingRight = analogRead(0);

  //Reading of the switch
  //buttonReading = digitalRead(buttonPin);

  // display data from the sensors and switch in the monitor
  Serial.print(fsrReadingDown);
  Serial.print(" ");
  Serial.print(fsrReadingUp);
  Serial.print(" ");
  Serial.print(fsrReadingYaw_no_clock);
  Serial.print(" ");
  Serial.print(fsrReadingYaw_clock);
  Serial.print(" ");
  Serial.print(fsrReadingBack);
  Serial.print(" ");
  Serial.print(fsrReadingFront);
  Serial.print(" ");
  Serial.print(fsrReadingLeft);
  Serial.print(" ");
  Serial.print(fsrReadingRight);
  Serial.print(" ");
  Serial.print(buttonReading);
  Serial.println("");


  // allumer les LED quand on appuie sur fsr_down
  if (fsrReadingDown > 500){
    for (int i=0; i<NUM_LEDS_PER_STRIP; i++){
    DownLeds[i] = CRGB(0, 255, 0 );
    FastLED.setBrightness(150);
    FastLED.show();
   
  }
  }
  else{
   for (int i=0; i<NUM_LEDS_PER_STRIP; i++){
    DownLeds[i] = CRGB(0, 0, 0 );
    FastLED.setBrightness(150);
    FastLED.show();
  }
  }

  // allumer les LED quand on appuie sur fsr_up
  if (fsrReadingUp > 500){
    for (int i=0; i<NUM_LEDS_PER_STRIP; i++){
    UpLeds[i] = CRGB(0, 0, 255 );
    FastLED.setBrightness(150);
    FastLED.show();
   
  }
  }
  else{
   for (int i=0; i<NUM_LEDS_PER_STRIP; i++){
    UpLeds[i] = CRGB(0, 0, 0 );
    FastLED.setBrightness(150);
    FastLED.show();
    delay(50);
  }
  }

// allumer les LED quand on appuie sur fsr_right
  if (fsrReadingRight > 500){
    for (int i=0; i<NUM_LEDS_PER_STRIP; i++){
    RightLeds[i] = CRGB(255, 0, 0 );
    FastLED.setBrightness(150);
    FastLED.show();
   
  }
  }
  else{
   for (int i=0; i<NUM_LEDS_PER_STRIP; i++){
    RightLeds[i] = CRGB(0, 0, 0 );
    FastLED.setBrightness(150);
    FastLED.show();
  }
  }


  // allumer les LED quand on appuie sur fsr_left
  if (fsrReadingLeft > 500){
    for (int i=0; i<NUM_LEDS_PER_STRIP; i++){
    LeftLeds[i] = CRGB(255, 255, 0 );
    FastLED.setBrightness(150);
    FastLED.show();
   
  }
  }
  else{
   for (int i=0; i<NUM_LEDS_PER_STRIP; i++){
    LeftLeds[i] = CRGB(0, 0, 0 );
    FastLED.setBrightness(150);
    FastLED.show();
  }
  }



}
