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
#include <Arduino.h>

// Singleton instance of the radio driver
RH_RF95 rf95(8, 7); // Adafruit Feather M0 with RFM95 

int led = 9;

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

int num_got = 0;
int replies_got = 23;

void loop()
{
  if (rf95.available())
  {

    // Should be a message for us now   
    uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
    uint8_t len = sizeof(buf);

    if (rf95.recv(buf, &len)) {

      digitalWrite(led, HIGH);      
      
      uint8_t expected_data[210] = "ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe"; // expected data to compare with
      
      const int ARRAY_SIZE = sizeof(expected_data); // size of the send_data array
      int numDifferences = countBitDifferences((char*)expected_data, (char*)buf, ARRAY_SIZE);

      int numbytediff = countByteDifferences((char*)expected_data, (char*)buf, ARRAY_SIZE);

      // Send a reply
      //uint8_t data[1] = {numbytediff};

      uint8_t data[210] = "ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe ChaChe"; // expected data to compare with
      data[0] = {numbytediff};

      rf95.send(data, sizeof(data));
      rf95.waitPacketSent(1000);
      
      //Serial.println("Sent a reply");
      digitalWrite(led, LOW);     

      num_got += 1;

      //Serial.print("num_sent ");  Serial.print(" ratio "); 
      Serial.print(replies_got/num_got);Serial.print(",");
      Serial.print(rf95.lastRssi());Serial.print(",");
      Serial.print(rf95.lastSNR());Serial.print(",");
      Serial.print(num_got);Serial.print(",");
      Serial.print(replies_got);Serial.print(",");
      Serial.print(numDifferences);Serial.print(",");
      Serial.print(numbytediff);Serial.println(" ");
    }
    else
    {
      Serial.println("recv failed");
    }
  }
}

int countBitDifferences(const char* array1, const char* array2, int arraySize) {
    int numDifferences = 0;
    for (int i = 0; i < arraySize; ++i) {
        for (int j = 0; j < 8; ++j) {
            if(bitRead(array1[i], j) != bitRead(array2[i], j)) {
                numDifferences++;
            }
        }
    }
    return numDifferences;
}

int countByteDifferences(const char* array1, const char* array2, int arraySize) {
    int numDifferences = 0;
    for (int i = 0; i < arraySize; ++i) {
        for (int j = 0; j < 8; ++j) {
            if(bitRead(array1[i], j) != bitRead(array2[i], j)) {
                numDifferences++;
                break;
            }
        }
    }
    return numDifferences;
}


int count_diff_bytes(uint8_t* array1, uint8_t* array2) {
  int length = sizeof(array1) / sizeof(array1[0]); // calculate length of arrays
  int num_diff_bytes = 0;

  for (int i = 0; i < length; i++) {
    if (array1[i] != array2[i]) {
      num_diff_bytes++;
    }
  }

  return num_diff_bytes;
}

