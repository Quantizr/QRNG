const byte adcPin = 0;
volatile int adcReading;
volatile int adcPrev;
volatile boolean adcDone;
boolean adcStarted;

volatile boolean first;
volatile boolean triggered;
volatile unsigned long overflowCount;
volatile unsigned long elapsedTime;

// timer overflows (every 65536 counts)
ISR (TIMER1_OVF_vect) 
{
  overflowCount++;
}  // end of TIMER1_OVF_vect

void setup ()
{
  //baud rate 115200
  Serial.begin (115200);
  analogReference (INTERNAL);
  ADCSRA =  bit (ADEN);                      // turn ADC on

  //Set Prescaler value to 4
  ADCSRA |= bit (ADPS1);
  
  ADMUX  =  bit (REFS0) | (adcPin & 0x07);    // AVcc and select input port
  
  // reset Timer 1
  TCCR1A = 0;
  TCCR1B = 0;
  // Timer 1 - interrupt on overflow
  TIMSK1 = bit (TOIE1);   // enable Timer1 Interrupt
  // zero it
  TCNT1 = 0;  
  overflowCount = 0;  
  // start Timer 1
  TCCR1B =  bit (CS10);  //  no prescaling

  // set up for interrupts
  first = true;
  triggered = false;
}  // end of setup


// ADC complete ISR
ISR (ADC_vect)
  {
  adcReading = ADC;
  adcDone = true;  
  if (adcReading > 60 && adcPrev <= 60){
    unsigned int counter = TCNT1;  // quickly save it
    // wait until we noticed last one
    if (triggered)
      return;

    elapsedTime = (overflowCount << 16) + counter;
    //Reset Timer1 after elapsed time set to prevent eventual Timer1 overflow
    //Effective previous finish time becomes 0 and serves as the next start time
    TCNT1 = 0;  //zero Timer1
    overflowCount = 0;  //Zero overflowCount

    triggered = true;
  }
  }  // end of ADC_vect
  
void loop ()
{
  // if last reading finished, process it
  if (adcDone)
    {
    adcStarted = false;
    adcPrev = adcReading;
    adcDone = false;
    }
    
  // if we aren't taking a reading, start a new one
  if (!adcStarted)
    {
    adcStarted = true;
    // start the conversion
    ADCSRA |= bit (ADSC) | bit (ADIE);
    }    

  //process time between actions
  if (!triggered)
    return;

  if(first){
    first = false;
    triggered = false;  // re-arm for next time
    return;
  }

  if (elapsedTime >= 20000) {
    Serial.println(elapsedTime-20000); //print time only after 20000 clocks (1.25ms) to account for dead time and after pulsing
  }
  triggered = false;  // re-arm for next time 

}  // end of loop
