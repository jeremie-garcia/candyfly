
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
  fsrReadingUp = analogRead(1);
  fsrReadingDown = analogRead(0);
  fsrReadingRight = analogRead(3);
  fsrReadingLeft = analogRead(2);
  
  Serial.print(fsrReadingUp);
  Serial.print(" ");
  Serial.print(fsrReadingDown);
  Serial.print(" ");
  Serial.print(fsrReadingYaw_clock);
  Serial.print(" ");
  Serial.print(fsrReadingYaw_no_clock);
  Serial.print(" ");
  Serial.print(fsrReadingFront);
  Serial.print(" ");
  Serial.print(fsrReadingBack);
  Serial.print(" ");
  Serial.print(fsrReadingRight); 
  Serial.print(" ");
  Serial.print(fsrReadingLeft);
  Serial.println("");
}
