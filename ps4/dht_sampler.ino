// Example testing sketch for various DHT humidity/temperature sensors
// Written by ladyada, public domain

#include "DHT.h"

#define DHTPIN 12     // what digital pin we're connected to
#define LEDPIN 11

#define LED_THRES 90.0

// Uncomment whatever type you're using!
#define DHTTYPE DHT11   // DHT 11
//#define DHTTYPE DHT22   // DHT 22  (AM2302), AM2321
//#define DHTTYPE DHT21   // DHT 21 (AM2301)

// Connect pin 1 (on the left) of the sensor to +5V
// NOTE: If using a board with 3.3V logic like an Arduino Due connect pin 1
// to 3.3V instead of 5V!
// Connect pin 2 of the sensor to whatever your DHTPIN is
// Connect pin 4 (on the right) of the sensor to GROUND
// Connect a 10K resistor from pin 2 (data) to pin 1 (power) of the sensor

// Initialize DHT sensor.
// Note that older versions of this library took an optional third parameter to
// tweak the timings for faster processors.  This parameter is no longer needed
// as the current DHT reading algorithm adjusts itself to work on faster procs.
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  // To USB
  Serial.begin(9600);

  // To OpenWRT
  Serial1.begin(57600);

  pinMode(LEDPIN, OUTPUT);
  
  // To Pins
  dht.begin();
}

void printToCOM(float humidity, float tempCel, float tempFar, float heatIndexCel, float heatIndexFar) {
  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.print("%\t");
  Serial.print("Temperature: ");
  Serial.print(tempCel);
  Serial.print(" *C ");
  Serial.print(tempFar);
  Serial.print(" *F\t");
  Serial.print("Heat index: ");
  Serial.print(heatIndexCel);
  Serial.print(" *C ");
  Serial.print(heatIndexFar);
  Serial.println(" *F");
}

void printToWRT(float humidity, float tempCel, float tempFar, float heatIndexCel, float heatIndexFar) {
  Serial1.print(humidity);
  Serial1.print("\t");
  Serial1.print(tempCel);
  Serial1.print("\t");
  Serial1.print(tempFar);
  Serial1.print("\t");
  Serial1.print(heatIndexCel);
  Serial1.print("\t");
  Serial1.print(heatIndexFar);
  Serial1.println("");
}

void loop() {
  // Wait a few seconds between measurements.
  delay(2000);

  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  float h = dht.readHumidity();
  // Read temperature as Celsius (the default)
  float t = dht.readTemperature();
  // Read temperature as Fahrenheit (isFahrenheit = true)
  float f = dht.readTemperature(true);

  // Check if any reads failed and exit early (to try again).
  if (isnan(h) || isnan(t) || isnan(f)) {
    Serial.println("Failed to read from DHT sensor!");
    Serial1.println("-");
    return;
  }

  // Compute heat index in Fahrenheit (the default)
  float hif = dht.computeHeatIndex(f, h);
  // Compute heat index in Celsius (isFahreheit = false)
  float hic = dht.computeHeatIndex(t, h, false);
  
  if (f > LED_THRES) {
    Serial.println("higher than 75 farenheit");
    digitalWrite(LEDPIN, HIGH);
  } else {
    digitalWrite(LEDPIN, LOW);
  }
  
  printToCOM(h, t, f, hic, hif);
  printToWRT(h, t, f, hic, hif);
}
