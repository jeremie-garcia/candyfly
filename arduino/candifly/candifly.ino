int buttonPin = 2;

int fsrReadingUp = 0;
int fsrReadingDown = 0;
int fsrReadingRight = 0;
int fsrReadingLeft = 0;
int fsrReadingYaw_clock = 0;
int fsrReadingYaw_no_clock = 0;
int fsrReadingFront = 0;
int fsrReadingBack = 0;
int buttonReading = 0;

void setup() {
   Serial.begin(9600);
   pinMode(buttonPin, INPUT);
}

void loop() {

  fsrReadingDown = analogRead(0);
  fsrReadingUp = analogRead(1);
  //fsrReadingYaw_no_clock = analogRead(6);
  //fsrReadingYaw_clock= analogRead(7);
  //fsrReadingBack = analogRead(4);
  //fsrReadingFront = analogRead(5);
  fsrReadingLeft = analogRead(2);
  fsrReadingRight = analogRead(3);
  
  //buttonReading = digitalRead(buttonPin);

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


}
