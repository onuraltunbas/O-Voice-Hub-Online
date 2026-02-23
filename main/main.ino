// Copyright (c) 2026 Onur
// Non-Commercial License
// Commercial use prohibited without permission

int led1Pin = 11;
int led2Pin = 12;
int led3Pin = 13;

void setup() {
  Serial.begin(9600);
  // Pinleri çıkış olarak ayarla
  pinMode(led1Pin, OUTPUT);
  pinMode(led2Pin, OUTPUT);
  pinMode(led3Pin, OUTPUT);
  
  // Başlangıçta tüm LED'leri kapalı tut
  digitalWrite(led1Pin, LOW);
  digitalWrite(led2Pin, LOW);
  digitalWrite(led3Pin, LOW);
}

void loop() {
  if (Serial.available() > 0) {
    char komut = Serial.read();

    // LED 1 Kontrolü (1 açar, 2 kapatır)
    if (komut == '1') { digitalWrite(led1Pin, HIGH); } 
    else if (komut == '2') { digitalWrite(led1Pin, LOW); }
    
    // LED 2 Kontrolü (3 açar, 4 kapatır)
    else if (komut == '3') { digitalWrite(led2Pin, HIGH); } 
    else if (komut == '4') { digitalWrite(led2Pin, LOW); }
    
    // LED 3 Kontrolü (5 açar, 6 kapatır)
    else if (komut == '5') { digitalWrite(led3Pin, HIGH); } 
    else if (komut == '6') { digitalWrite(led3Pin, LOW); }
  }
}
