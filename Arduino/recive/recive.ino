// rf69 demo tx rx.pde
// -*- mode: C++ -*-
// Example sketch showing how to create a simple messageing client
// with the RH_RF69 class. RH_RF69 class does not provide for addressing or
// reliability, so you should only use RH_RF69  if you do not need the higher
// level messaging abilities.
// It is designed to work with the other example rf69_server.
// Demonstrates the use of AES encryption, setting the frequency and modem 
// configuration

#include <SPI.h>
#include <RH_RF69.h>

/************ Radio Setup ***************/

// Change to 434.0 or other frequency, must match RX's freq!
#define RF69_FREQ 915.0

#if defined (__AVR_ATmega32U4__) // Feather 32u4 w/Radio
  #define RFM69_CS      8
  #define RFM69_INT     7
  #define RFM69_RST     4
  #define LED           13
  
#elif defined(ADAFRUIT_FEATHER_M0) || defined(ADAFRUIT_FEATHER_M0_EXPRESS) || defined(ARDUINO_SAMD_FEATHER_M0)
  // Feather M0 w/Radio
  #define RFM69_CS      8
  #define RFM69_INT     3
  #define RFM69_RST     4
  #define LED           13
  
#elif defined (__AVR_ATmega328P__)  // Feather 328P w/wing
  #define RFM69_INT     3  // 
  #define RFM69_CS      4  //
  #define RFM69_RST     2  // "A"
  #define LED           13

#elif defined(ESP8266)    // ESP8266 feather w/wing
  #define RFM69_CS      2    // "E"
  #define RFM69_IRQ     15   // "B"
  #define RFM69_RST     16   // "D"
  #define LED           0

#elif defined(ARDUINO_ADAFRUIT_FEATHER_ESP32S2) || defined(ARDUINO_NRF52840_FEATHER) || defined(ARDUINO_NRF52840_FEATHER_SENSE)
  #define RFM69_INT     9  // "A"
  #define RFM69_CS      10  // "B"
  #define RFM69_RST     11  // "C"
  #define LED           13

#elif defined(ESP32)    // ESP32 feather w/wing
  #define RFM69_RST     13   // same as LED
  #define RFM69_CS      33   // "B"
  #define RFM69_INT     27   // "A"
  #define LED           13

#elif defined(ARDUINO_NRF52832_FEATHER)
  /* nRF52832 feather w/wing */
  #define RFM69_RST     7   // "A"
  #define RFM69_CS      11   // "B"
  #define RFM69_INT     31   // "C"
  #define LED           17

#endif


/* Teensy 3.x w/wing
#define RFM69_RST     9   // "A"
#define RFM69_CS      10   // "B"
#define RFM69_IRQ     4    // "C"
#define RFM69_IRQN    digitalPinToInterrupt(RFM69_IRQ )
*/
 
/* WICED Feather w/wing 
#define RFM69_RST     PA4     // "A"
#define RFM69_CS      PB4     // "B"
#define RFM69_IRQ     PA15    // "C"
#define RFM69_IRQN    RFM69_IRQ
*/

// Singleton instance of the radio driver
RH_RF69 rf69(RFM69_CS, RFM69_INT);

int16_t packetnum = 0;  // packet counter, we increment per xmission

void setup() 
{
  Serial.begin(1000000);
  //while (!Serial) { delay(1); } // wait until serial console is open, remove if not tethered to computer

  pinMode(LED, OUTPUT);     
  pinMode(RFM69_RST, OUTPUT);
  digitalWrite(RFM69_RST, LOW);

  Serial.println("Feather RFM69 TX Test!");
  Serial.println();

  // manual reset
  digitalWrite(RFM69_RST, HIGH);
  delay(10);
  digitalWrite(RFM69_RST, LOW);
  delay(10);
  
  if (!rf69.init()) {
    Serial.println("RFM69 radio init failed");
    while (1);
  }
  Serial.println("RFM69 radio init OK!");
  // Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM (for low power module)
  // No encryption
  if (!rf69.setFrequency(RF69_FREQ)) {
    Serial.println("setFrequency failed");
  }

  // If you are using a high power RF69 eg RFM69HW, you *must* set a Tx power with the
  // ishighpowermodule flag set like this:
  rf69.setTxPower(20, true);  // range from 14-20 for power, 2nd arg must be true for 69HCW
  pinMode(LED, OUTPUT);

  Serial.print("RFM69 radio @");  Serial.print((int)RF69_FREQ);  Serial.println(" MHz");

}

int size_max = 240;
uint8_t incomingByte[240] = {}; // for incoming serial data

void loop() {
  delay(1);  // Wait 1 second between transmits, could also 'sleep' here!

  // send data only when you receive data:
  if (Serial.available() > 0) {
    // read the incoming byte:
    Serial.println("Start");
    //for(int i = 0;i < size_max; i++){
    //  incomingByte[i] = Serial.read();
    //}

    //rf69.send(incomingByte,sizeof(incomingByte));    
    //rf69.waitPacketSent();
    
    uint8_t a[60] = {};
    uint8_t b[60] = {};
    uint8_t c[60] = {};
    uint8_t d[60] = {};
    int index = 0;

    for(int i = 0;i < size_max; i++){
      if(i < 59){
        a[i] = Serial.read();
      } else if(i < 118 && i >= 59){
        index = i - 59;
        b[index] = Serial.read();        
      } else if(i < 177 && i >= 118){
        index = i - 118;
        c[index] = Serial.read();        
      } else if (i < 236){
        index = i - 177;
        d[index] = Serial.read();
      }
    }

    a[59] = 1;
    b[59] = 2;
    c[59] = 3;
    d[59] = 4;

    rf69.send(a,60);    
    rf69.waitPacketSent();
    delay(10);

    rf69.send(b,60);    
    rf69.waitPacketSent();
    delay(10);

    rf69.send(c,60);    
    rf69.waitPacketSent();
    delay(10);

    rf69.send(d,60);    
    rf69.waitPacketSent();
    delay(10);

    uint8_t incomingByte[240] = {}; // for incoming serial data
  }
}
