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
from dotenv import load_dotenv


load_dotenv()


pygame.mixer.init()

# --- AYARLAR VE KİMLİK BİLGİLERİ (.env'den çekiliyor) ---

LATITUDE = os.getenv("LATITUDE")
LONGITUDE = os.getenv("LONGITUDE")
SEHIR = os.getenv("SEHIR")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
VARSAYILAN_CHAT_ID = os.getenv("VARSAYILAN_CHAT_ID")
MEVLUT_CHAT_ID = os.getenv("MEVLUT_CHAT_ID")
ARDUINO_PORT = os.getenv("ARDUINO_PORT", "/dev/ttyUSB0")

# --- REHBER ---
REHBER = {
    "mevlüt": MEVLUT_CHAT_ID,
    "kendim": VARSAYILAN_CHAT_ID
}

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
        print("\n🎙️ Seni dinliyorum Onur...")
        r.adjust_for_ambient_noise(source, duration=0.5) 
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5) 
            metin = r.recognize_google(audio, language="tr-TR")
            print(f"Sen söyledin: {metin}")
            return metin.lower()
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            print("Google Ses API'sine ulaşılamıyor. İnternetini kontrol et.")
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

    konus("Sistemler aktif Onur, emirlerini bekliyorum.")

    while True:
        try:
            komut = dinle()
            
            if not komut: 
                continue 
            
            if "kapat" in komut.lower() and "sistemleri" in komut.lower() or "görüşürüz" in komut.lower():
                konus("Görüşürüz, sistemleri kapatıyorum.")
                break
            
            yanit = cevapla(komut, komutlar)
            if yanit: 
                konus(yanit)
                
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    jarvis_calistir()