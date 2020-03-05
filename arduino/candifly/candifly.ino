
int fsrReadingUp = 0;
int fsrReadingDown = 0;
int fsrReadingRight = 0;
int fsrReadingLeft = 0;
int fsrReadingYaw_clock = 0;
int fsrReadingYaw_no_clock = 0;
int fsrReadingFront = 0;
int fsrReadingBack = 0;

void setup() {
   Serial.begin(9600);
}

void loop() {
  fsrReadingDown = analogRead(0);
  fsrReadingUp = analogRead(1);
  fsrReadingYaw_no_clock = analogRead(2);
  fsrReadingYaw_clock= analogRead(3);
  fsrReadingBack = analogRead(4);
  fsrReadingFront = analogRead(5);
  fsrReadingLeft = analogRead(6);
  fsrReadingRight = analogRead(7);

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
  Serial.println("");

}
