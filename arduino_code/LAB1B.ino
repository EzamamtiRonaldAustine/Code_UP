void setup(){ 
  // pinMode(3, OUTPUT);
  pinMode( 6, OUTPUT); // for our case the LED is an output 
  pinMode( 7, INPUT); // for our case the switch is an input 
} 
void loop(){ 
if ( digitalRead ( 7 ) == HIGH) // If switch is On 
{ 
  digitalWrite( 6, HIGH ); // when the LED is on 
  delay(300); // a delay for when it is on 
  digitalWrite( 6, LOW ); // when the LED is off 
  delay(300); // a delay for when it is off 
} else  { 
  digitalWrite ( 6, LOW);
  } 

  digitalWrite(3, HIGH); // turn LED on
  delay(1000);           // wait for 1 second
  digitalWrite(3, LOW);  // turn LED off
  delay(1000);           // wait for 1 second
} 

