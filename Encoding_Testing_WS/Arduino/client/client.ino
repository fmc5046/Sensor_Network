// rf95_client.pde
// -*- mode: C++ -*-
// Example sketch showing how to create a simple messageing client
// with the RH_RF95 class. RH_RF95 class does not provide for addressing or
// reliability, so you should only use RH_RF95 if you do not need the higher
// level messaging abilities.
// It is designed to work with the other example rf95_server
// Tested with Anarduino MiniWirelessLoRa, Rocket Scream Mini Ultra Pro with
// the RFM95W, Adafruit Feather M0 with RFM95

#include <SPI.h>
#include <RH_RF95.h>
#include "RS-FEC.h"

//const int msglen = 40; 
//const int msglen = 74; 
//const uint8_t ECC_LENGTH = 2;  //Max message lenght, and "gurdian bytes", Max corrected bytes ECC_LENGTH/2
//uint8_t message[] = "Important message HI how are? I am good";

//const int msglen = 60; 
const int msglen = 26;  
const uint8_t ECC_LENGTH = 16;  //Max message lenght, and "gurdian bytes", Max corrected bytes ECC_LENGTH/2
uint8_t message[] = "ChaChe ChaCha ChaCha";

char message_frame[msglen]; // The message size would be different, so need a container
char encoded[msglen + ECC_LENGTH];

RS::ReedSolomon<msglen, ECC_LENGTH> rs;

// Singleton instance of the radio driver
RH_RF95 rf95(8, 7); // Adafruit Feather M0 with RFM95 

void setup() 
{
  Serial.begin(9600);
  if (!rf95.init())
    Serial.println("init failed");

  rf95.setFrequency(915);
  rf95.setModemConfig(RH_RF95::Bw125Cr45Sf128);
  rf95.setPayloadCRC(false);
  rf95.setTxPower(2, false);
}

float num_sent = 0;
float replies_got = 0;

void loop()
{
  memset(message_frame, 0, sizeof(message_frame));        // Clear the array
  for(int i = 0; i <= msglen; i++) {    
    message_frame[i] = message[i];     
  } // Fill with the message
 
  rs.Encode(message_frame, encoded); 
  //Serial.print("Original: "); Serial.println(message_frame);
  //Serial.print("Encoded:  ");        for(uint8_t i = 0; i < sizeof(encoded); i++) {    Serial.print(encoded[i]);    }    Serial.println("");  

  uint8_t send_data[sizeof(encoded)] = {'\0'};
  memset(send_data, 0, sizeof(encoded));        // Clear the array
  memcpy(send_data, encoded, sizeof(encoded));

  // Send a message to rf95_server
  num_sent += 1;

  //Serial.print("Sent Info: "); Serial.println((char*)send_data);

  rf95.send(send_data, sizeof(send_data));
  rf95.waitPacketSent();

  Serial.println(sizeof(send_data));
  
  // Now wait for a reply
  uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
  uint8_t len = sizeof(buf);

  if (rf95.waitAvailableTimeout(100))
  { 
    // Should be a reply message for us now   
    if (rf95.recv(buf, &len))
   {
      replies_got += 1;
    }
    else
    {
      Serial.println("recv failed");
    }
  }
  else
  { 
    if(num_sent < 100){
      Serial.println("No reply, is rf95_server running?");
    }
  }
  delay(1000);
  
  //if(num_sent < 100){
  if(true){
    //Serial.print("num_sent ");  Serial.print(" ratio "); 
    Serial.print(replies_got/num_sent);Serial.print(",");
    Serial.print(rf95.lastRssi());Serial.print(",");
    Serial.print(rf95.lastSNR());Serial.print(",");
    Serial.print(num_sent);Serial.print(",");
    Serial.print(replies_got);Serial.println(" ");
  }
}

