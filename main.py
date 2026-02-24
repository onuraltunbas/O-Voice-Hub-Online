# Copyright (c) 2026 Remzican Onur Altunbaş
# Non-Commercial License
# Commercial use prohibited without permission

import json
import os
import random
import requests
from datetime import datetime
from gtts import gTTS
import pygame
import serial
import time
import speech_recognition as sr
import warnings
from dotenv import load_dotenv

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

load_dotenv()

pygame.mixer.init()

# --- AYARLAR VE KİMLİK BİLGİLERİ (.env'den çekiliyor) ---
LATITUDE = os.getenv("LATITUDE")
LONGITUDE = os.getenv("LONGITUDE")
SEHIR = os.getenv("SEHIR")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
VARSAYILAN_CHAT_ID = os.getenv("VARSAYILAN_CHAT_ID")
ARDUINO_PORT = os.getenv("ARDUINO_PORT", "/dev/ttyACM0")

# --- REHBER (.env'den JSON olarak çekiliyor) ---
try:
    # .env içindeki REHBER satırını okur ve Python sözlüğüne çevirir
    REHBER = json.loads(os.getenv("REHBER", "{}"))
    # Eğer .env'de 'kendim' unutulursa varsayılan chat ID'yi otomatik ekler
    if "kendim" not in REHBER:
        REHBER["kendim"] = VARSAYILAN_CHAT_ID
except json.JSONDecodeError:
    print("HATA: .env dosyasındaki REHBER formatı hatalı! JSON formatında olmalı.")
    REHBER = {"kendim": VARSAYILAN_CHAT_ID}

# --- ARDUINO BAĞLANTISI ---
try:
    arduino = serial.Serial(ARDUINO_PORT, 9600, timeout=1)
    time.sleep(2) 
    print("Arduino bağlantısı başarılı!")
except Exception as e:
    arduino = None
    print("Arduino bulunamadı, donanım kontrolleri devre dışı bırakıldı.")


def hava_durumu_getir():
    url = (f"https://api.open-meteo.com/v1/forecast?"
           f"latitude={LATITUDE}&longitude={LONGITUDE}&"
           f"current=temperature_2m,weather_code&"
           f"timezone=Europe%2FMoscow&" 
           f"forecast_days=1") 
    try:
        response = requests.get(url)
        data = response.json()
        sicaklik = data['current']['temperature_2m']
        weather_code = data['current']['weather_code']
        
        aciklama_sozlugu = {
            0: "açık ve güneşli", 1: "çoğunlukla açık", 2: "parçalı bulutlu", 
            3: "tamamen bulutlu", 45: "sisli", 61: "hafif yağmurlu", 
            95: "gök gürültülü fırtına"
        }
        aciklama = aciklama_sozlugu.get(weather_code, "belirsiz")
        return f"{SEHIR}'da hava şu an {sicaklik:.1f} derece ve {aciklama}."
    except:
        return "Hava durumu verilerine şu an ulaşamıyorum."

def telegram_mesaj_gonder(komut):
    if not TELEGRAM_TOKEN or not VARSAYILAN_CHAT_ID:
        return "Telegram API bilgileri eksik. Lütfen .env dosyasını kontrol et."

    hedef_id = VARSAYILAN_CHAT_ID
    hedef_isim = "sana"
    
    for isim, id_no in REHBER.items():
        if id_no and isim in komut.lower():
            hedef_id = id_no
            hedef_isim = isim.capitalize()
            break

    icerik = komut.lower().replace("telegramdan", "").replace("mesaj gönder", "").replace("e ", "").replace("a ", "").strip()
    if not icerik:
        icerik = "Jarvis üzerinden otomatik mesaj."

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        response = requests.post(url, data={"chat_id": hedef_id, "text": icerik})
        if response.status_code == 200:
            return f"Mesajını {hedef_isim} kişisine başarıyla ilettim."
        else:
            return "Telegram mesajı gönderilirken bir hata oluştu, Token'ı kontrol et."
    except:
        return "Bağlantı hatası: İnternetini kontrol et."

def konus(metin):
    print("Jarvis:", metin)
    tts = gTTS(text=metin, lang='tr')
    dosya = "ses.mp3"
    tts.save(dosya)
    
    try:
        pygame.mixer.music.load(dosya)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    finally:
        pygame.mixer.music.stop()
        try:
            pygame.mixer.music.unload()
        except AttributeError:
            pass
        if os.path.exists(dosya):
            try:
                os.remove(dosya)
            except OSError:
                pass

def dinle():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n🎙️ Seni dinliyorum Onur (TR/EN)...")
        r.adjust_for_ambient_noise(source, duration=0.5) 
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5) 
            
            metin = r.recognize_whisper(audio, model="base")
            print(f"Sen söyledin: {metin}")
            return metin.lower().strip()
            
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            print(f"Ses algılama hatası: {e}")
            return ""

def cevapla(komut, komutlar):
    komut = komut.lower()

    if "mesaj gönder" in komut or "telegram" in komut:
        return telegram_mesaj_gonder(komut)

    for kategori, veri in komutlar.items():
        for anahtar in veri.get("anahtarlar", []):
            if anahtar in komut:
                
                if kategori == "led_1_ac":
                    if arduino: arduino.write(b'1')
                    else: return "Donanım bağlantısı yok ama komutu algıladım."
                elif kategori == "led_1_kapat":
                    if arduino: arduino.write(b'2')
                    else: return "Donanım bağlantısı yok ama komutu algıladım."
                elif kategori == "led_2_ac":
                    if arduino: arduino.write(b'3')
                    else: return "Donanım bağlantısı yok ama komutu algıladım."
                elif kategori == "led_2_kapat":
                    if arduino: arduino.write(b'4')
                    else: return "Donanım bağlantısı yok ama komutu algıladım."
                elif kategori == "led_3_ac":
                    if arduino: arduino.write(b'5')
                    else: return "Donanım bağlantısı yok ama komutu algıladım."
                elif kategori == "led_3_kapat":
                    if arduino: arduino.write(b'6')
                    else: return "Donanım bağlantısı yok ama komutu algıladım."

                cevap = random.choice(veri["cevap"]) if isinstance(veri["cevap"], list) else veri["cevap"]
                cevap = cevap.replace("{saat}", datetime.now().strftime("%H:%M"))
                cevap = cevap.replace("{tarih}", datetime.now().strftime("%d %B %Y"))
                if "{hava}" in cevap:
                    cevap = cevap.replace("{hava}", hava_durumu_getir())
                return cevap

    return ""

def jarvis_calistir():
    if os.path.exists('komutlar.json'):
        with open('komutlar.json', 'r', encoding='utf-8') as f:
            komutlar = json.load(f)
    else:
        komutlar = {}

    konus("Sistemler aktif Onur, emirlerini bekliyorum. Systems are online.")

    while True:
        try:
            komut = dinle()
            
            if not komut: 
                continue 
            
            if any(x in komut for x in ["kapat", "görüşürüz", "shut down", "goodbye", "exit"]):
                konus("Görüşürüz, sistemleri kapatıyorum. Shutting down.")
                break
            
            yanit = cevapla(komut, komutlar)
            if yanit: 
                konus(yanit)
                
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    jarvis_calistir()