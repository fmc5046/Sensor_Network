// rf95_server.pde
// -*- mode: C++ -*-
// Example sketch showing how to create a simple messageing server
// with the RH_RF95 class. RH_RF95 class does not provide for addressing or
// reliability, so you should only use RH_RF95  if you do not need the higher
// level messaging abilities.
// It is designed to work with the other example rf95_client
// Tested with Anarduino MiniWirelessLoRa, Rocket Scream Mini Ultra Pro with
// the RFM95W, Adafruit Feather M0 with RFM95

#include <SPI.h>
#include <RH_RF95.h>
#include "RS-FEC.h"

// Singleton instance of the radio driver
RH_RF95 rf95(8, 7); // Adafruit Feather M0 with RFM95 

int led = 9;
const int msglen_low = 40;  
const int msglen_high = 26;  

const uint8_t ECC_low = 2;  //Max message lenght, and "gurdian bytes", Max corrected bytes ECC_low/2 
const uint8_t ECC_high = 16;
uint8_t message[] = "Important message Important message Important message Important message";
RS::ReedSolomon<msglen_low, ECC_low> rs_low;
RS::ReedSolomon<msglen_high, ECC_high> rs_high;

void setup() 
{
  delay(400);
  pinMode(led, HIGH);     
  Serial.begin(9600);
  if (!rf95.init())
    Serial.println("init failed");  

  rf95.setFrequency(915);
  rf95.setModemConfig(RH_RF95::Bw125Cr45Sf128);
  rf95.setTxPower(2, false);
  rf95.setPayloadCRC(false);
}

void loop()
{
  if (rf95.available())
  {
    Serial.println("0");
    // Should be a message for us now   
    uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
    Serial.println("01");
    uint8_t len = sizeof(buf);
    Serial.println("02");
    if (rf95.recv(buf, &len)) {

      Serial.println("03");

      digitalWrite(led, HIGH);

      Serial.println("1");

      ///Generate Test array and message frames for low and high
      //Generate test char array from the uint8_t buffer

      //For low
      char test_low[msglen_low + ECC_low];
      memset(test_low, 0, sizeof(test_low  + ECC_low));
      //memcpy(test_low,buf,msglen_low + ECC_low);

      //Serial.print("Test_Low: ");
      for(int i = 0;i < msglen_low + ECC_low; i++){
        test_low[i] = char(buf[i]);
        //Serial.print(test_low[i]);
      }
      //Serial.println();

      Serial.println("2");

      //For high
      char test_high[msglen_high + ECC_high];
      memset(test_high, 0, sizeof(test_high  + ECC_high));
      memcpy(test_high,buf,msglen_high + ECC_high);
      
      //Decoding
      //For ECC low
      char repaired_low[msglen_low]; 
      rs_low.Decode(test_low, repaired_low);
      //Serial.print("Repaired_low: "); Serial.println(repaired_low);

      Serial.println("3");

      //For ECC high
      char repaired_high[msglen_high]; 
      rs_high.Decode(test_high, repaired_high);
      //Serial.print("Repaired_high: "); Serial.println(repaired_high);

      Serial.println("4");

      int compare_low = 0;
      int compare_high = 0;

      if(strcmp(repaired_high,"ChaChe ChaCha ChaCha") == 0){
        compare_high = 1;
        Serial.println("ECC High");
      }

      if(strcmp(repaired_low,"Important message HI how are? I am good") == 0){
        compare_low = 1;
        Serial.println("ECC low");
      }
      Serial.println(RH_RF95_MAX_MESSAGE_LEN);
      Serial.println("5");

      if(compare_low == 1 || compare_high == 1){
        // Send a reply
        Serial.println("51");
        uint8_t data[] = "And hello back to you";
        rf95.send(data, sizeof(data));
        Serial.println("52");        
        rf95.waitPacketSent(1000);
        Serial.println("Sent a reply");
        digitalWrite(led, LOW);            
        Serial.println("53"); 
      }

      Serial.println("6");

    }
    else
    {
      Serial.println("recv failed");
    }
  }
}

