#include <Wire.h>
#include <Adafruit_ADS1X15.h>
#include "Adafruit_SHT31.h"

#define SOLENOID_1_PIN  2
#define SOLENOID_2_PIN  3
#define SOLENOID_3_PIN  4
#define SOLENOID_4_PIN  5

#define PELTIER_PIN 9
#define LASER_PIN   13
#define PUMP_PIN    10

Adafruit_ADS1115 ads;
Adafruit_SHT31 sht31 = Adafruit_SHT31();

int mode = 0;

int Kp = 0;
int Ki = 0;
int Kd = 0;
int setPoint = 0;

unsigned long Ts;

int pumpSpeed = 0;

char buff[100];
String inputString = "";

bool sendData = false;

void setup() {
    inputString.reserve(200);
    Serial.begin(115200);
    sht31.begin();
    ads.begin();

    pinMode(SOLENOID_1_PIN, OUTPUT);
    pinMode(SOLENOID_2_PIN, OUTPUT);
    pinMode(SOLENOID_3_PIN, OUTPUT);
    pinMode(SOLENOID_4_PIN, OUTPUT);
    pinMode(LASER_PIN, OUTPUT);
}

void loop() {
    if(millis() - Ts >= 10) {
        if(sendData == true) {
            int16_t adc0 = random(0, 1024); // ads.readADC_SingleEnded(0);
            int16_t adc1 = random(0, 1024); // ads.readADC_SingleEnded(1);
            int16_t adc2 = random(0, 1024); // ads.readADC_SingleEnded(2);

            int temp = random(0, 100); // (int) (sht31.readTemperature() * 100);
            int humd = random(0, 100); // (int) (sht31.readHumidity() * 100);
            
            // sprintf(buff, "R%05dG%05dB%05dT%05dH%05d", adc0, adc1, adc2, temp, humd);
            sprintf(buff, "%05d %05d %05d %05d %05d", adc0, adc1, adc2, temp, humd);
            Serial.println(buff);
        }   
        Ts = millis();
    }
}

void serialEvent() {
    inputString = Serial.readStringUntil('\n');
    
    sscanf(inputString.c_str(), "M%dKp%dKi%dKd%dSP%d\n", &mode, &Kp, &Ki, &Kd, & setPoint); //kurang pump

    switch(mode) {

        // Cleaning Phase
        case 1:
            sendData = true;
            digitalWrite(LASER_PIN, HIGH);
            digitalWrite(SOLENOID_1_PIN, LOW);
            digitalWrite(SOLENOID_2_PIN, LOW);
            digitalWrite(SOLENOID_3_PIN, HIGH);
            digitalWrite(SOLENOID_4_PIN, HIGH);
            break;

        // Exposure Phase
        case 2:
            sendData = true;
            digitalWrite(LASER_PIN, HIGH);
            digitalWrite(SOLENOID_1_PIN, HIGH);
            digitalWrite(SOLENOID_2_PIN, HIGH);
            digitalWrite(SOLENOID_3_PIN, HIGH);
            digitalWrite(SOLENOID_4_PIN, LOW);
            break;

        // Stop Phase
        case 3:
            sendData = false;
            digitalWrite(LASER_PIN, HIGH);
            digitalWrite(SOLENOID_1_PIN, LOW);
            digitalWrite(SOLENOID_2_PIN, LOW);
            digitalWrite(SOLENOID_3_PIN, LOW);
            digitalWrite(SOLENOID_4_PIN, LOW);
            break;
    }

    inputString = "";
}
