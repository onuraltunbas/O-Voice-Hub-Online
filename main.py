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

# --- ALSA (LINUX SES) UYARILARINI GİZLEME SİHRİ ---
try:
    ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
    def py_error_handler(filename, line, function, err, fmt):
        pass
    c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
    asound = cdll.LoadLibrary('libasound.so.2')
    asound.snd_lib_error_set_handler(c_error_handler)
except:
    pass

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
ARDUINO_PORT = os.getenv("ARDUINO_PORT", "/dev/ttyUSB0")

# --- REHBER (.env'den JSON olarak çekiliyor) ---
try:
    REHBER = json.loads(os.getenv("REHBER", "{}"))
    if "kendim" not in REHBER:
        REHBER["kendim"] = VARSAYILAN_CHAT_ID
except json.JSONDecodeError:
    print("ERROR: The REHBER format in the .env file is incorrect! It must be in JSON format.")
    REHBER = {"kendim": VARSAYILAN_CHAT_ID}

# --- ARDUINO BAĞLANTISI ---
try:
    arduino = serial.Serial(ARDUINO_PORT, 9600, timeout=1)
    time.sleep(2) 
    print("Arduino connection successful!")
except Exception as e:
    arduino = None
    print("Arduino not found, hardware controls are disabled.")


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
            0: "clear and sunny", 1: "mostly clear", 2: "partly cloudy", 
            3: "overcast", 45: "foggy", 61: "light rain", 
            95: "thunderstorm"
        }
        aciklama = aciklama_sozlugu.get(weather_code, "unclear")
        return f"The weather in {SEHIR} is currently {sicaklik:.1f} degrees and {aciklama}."
    except:
        return "I cannot access the weather data right now."

def telegram_mesaj_gonder(komut):
    if not TELEGRAM_TOKEN or not VARSAYILAN_CHAT_ID:
        return "Telegram API information is missing. Please check the .env file."

    hedef_id = VARSAYILAN_CHAT_ID
    hedef_isim = "you"
    
    for isim, id_no in REHBER.items():
        if id_no and isim in komut.lower():
            hedef_id = id_no
            hedef_isim = isim.capitalize()
            break

    # İngilizce "send message to [name]" kalıplarını temizleme
    icerik = komut.lower().replace("send a message", "").replace("send message", "").replace("telegram", "").replace("to", "").replace(hedef_isim.lower(), "").strip()
    
    if not icerik:
        icerik = "Automated message via Assistant."

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        response = requests.post(url, data={"chat_id": hedef_id, "text": icerik})
        if response.status_code == 200:
            return f"I have successfully sent your message to {hedef_isim}."
        else:
            return "An error occurred while sending the Telegram message, check your Token."
    except:
        return "Connection error: Check your internet connection."

def konus(metin):
    print("Assistant:", metin)
    # gTTS motoru artık tamamen İngilizce (en) aksanıyla konuşacak
    tts = gTTS(text=metin, lang='en')
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
    
    # HIZLANDIRMA AYARLARI BURADA
    r.pause_threshold = 0.4  # Cümle bittikten sonra bekleme süresini yarı yarıya düşürdük
    r.non_speaking_duration = 0.2 # Sessizlik algılama hassasiyeti artırıldı
    
    with sr.Microphone() as source:
        print("\n🎙️ Listening to you (EN)...")
        r.adjust_for_ambient_noise(source, duration=0.5) 
        try:
            # timeout: Asistanın senin konuşmaya başlamanı bekleyeceği maksimum süre
            # phrase_time_limit: Senin maksimum konuşma süren (Çok uzun tutmamak hızı artırır)
            audio = r.listen(source, timeout=3, phrase_time_limit=4) 
            
            print("Processing audio...")
            metin = r.recognize_whisper(audio, model="base", language="english")
            print(f"You said: {metin}")
            return metin.lower().strip()
            
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            print(f"Audio recognition error: {e}")
            return ""

def cevapla(komut, komutlar):
    komut = komut.lower()

    if "send message" in komut or "telegram" in komut:
        return telegram_mesaj_gonder(komut)

    for kategori, veri in komutlar.items():
        for anahtar in veri.get("anahtarlar", []):
            if anahtar in komut:
                
                if kategori == "led_1_ac":
                    if arduino: arduino.write(b'1')
                    else: return "I detected the command, but there is no hardware connection."
                elif kategori == "led_1_kapat":
                    if arduino: arduino.write(b'2')
                    else: return "I detected the command, but there is no hardware connection."
                elif kategori == "led_2_ac":
                    if arduino: arduino.write(b'3')
                    else: return "I detected the command, but there is no hardware connection."
                elif kategori == "led_2_kapat":
                    if arduino: arduino.write(b'4')
                    else: return "I detected the command, but there is no hardware connection."
                elif kategori == "led_3_ac":
                    if arduino: arduino.write(b'5')
                    else: return "I detected the command, but there is no hardware connection."
                elif kategori == "led_3_kapat":
                    if arduino: arduino.write(b'6')
                    else: return "I detected the command, but there is no hardware connection."

                cevap = random.choice(veri["cevap"]) if isinstance(veri["cevap"], list) else veri["cevap"]
                cevap = cevap.replace("{saat}", datetime.now().strftime("%H:%M"))
                cevap = cevap.replace("{tarih}", datetime.now().strftime("%d %B %Y"))
                if "{hava}" in cevap:
                    cevap = cevap.replace("{hava}", hava_durumu_getir())
                return cevap

    return ""

def asistan_calistir():
    if os.path.exists('komutlar.json'):
        with open('komutlar.json', 'r', encoding='utf-8') as f:
            komutlar = json.load(f)
    else:
        komutlar = {}

    konus("Systems are online, waiting for your commands.")

    while True:
        try:
            komut = dinle()
            
            if not komut: 
                continue 
            
            if any(x in komut for x in ["shut down", "goodbye", "exit", "turn off"]):
                konus("Goodbye, shutting down systems.")
                break
            
            yanit = cevapla(komut, komutlar)
            if yanit: 
                konus(yanit)
                
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    asistan_calistir()