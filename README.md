# Jarvis Sesli Kontrol & Otomasyon Sistemi

Bu proje, Python üzerinden sesli komutlar alarak hem bilgisayar üzerinden işlemler yapan (Telegram mesajı gönderme, hava durumu, saat vb.) hem de Arduino üzerinden fiziksel donanımı (LED/Sinyal) kontrol eden kişisel bir asistan uygulamasıdır.

## 🚀 Özellikler

* **Sesli Komut Tanıma:** Google Speech Recognition API ile Türkçe sesli komut desteği.
* **Donanım Kontrolü:** Seri port üzerinden Arduino'ya bağlı LED'leri (sinyal ve far simülasyonu) kontrol etme.
* **Telegram Entegrasyonu:** Belirlenen kişilere sesli komutla Telegram üzerinden otomatik mesaj gönderme.
* **Anlık Bilgi:** Hava durumu, tarih ve saat bilgilerini sesli olarak paylaşma.
* **Güvenli Yapı:** API anahtarları ve kişisel ayarlar `.env` dosyası ile korunmaktadır.

---

## 🛠️ Kurulum

### 1. Python Gereksinimleri

Öncelikle bilgisayarınızda Python 3.x yüklü olduğundan emin olun. Ardından projeyi indirip ana dizinde terminali açarak gerekli kütüphaneleri yükleyin:
```bash
pip install -r requirements.txt
```

> **Not:** PyAudio kütüphanesinin kurulumunda hata alırsanız, Linux tabanlı sistemlerde aşağıdaki komutu kullanın:
>
> ```bash
> sudo apt-get install python3-pyaudio
> ```

### 2. Ortam Değişkenleri (.env) Ayarları

Projenin API anahtarlarını, konum bilgilerini ve port ayarlarını kendi sisteminize göre yapılandırmanız gerekmektedir:

1. Proje klasöründeki `.env.example` dosyasının adını `.env` olarak değiştirin (veya kopyasını oluşturup adını `.env` yapın).
2. Oluşturduğunuz `.env` dosyasını bir metin editörüyle açın ve kendi bilgilerinizi (Telegram Token, Chat ID, Arduino Portu vb.) ilgili alanlara girin.

### 3. Donanım Bağlantısı (Arduino)

1. `main.ino` dosyasını Arduino IDE ile kartınıza yükleyin.
2. LED'lerinizi şu pinlere bağlayın:
   - **LED 1 (Sol Sinyal):** Pin 11
   - **LED 2 (Farlar):** Pin 12
   - **LED 3 (Sağ Sinyal):** Pin 13
3. `.env` dosyanızdaki `ARDUINO_PORT` değişkenini kendi Arduino portunuza göre güncelleyin.
   - Windows: `COM3`
   - Linux: `/dev/ttyUSB0`

---

## 🎙️ Örnek Komutlar

Sistem çalıştıktan sonra mikrofonunuzdan şu tarz komutlar verebilirsiniz:

| Komut | Açıklama |
|---|---|
| "Farları aç" / "Farları kapat" | Far LED'ini kontrol eder |
| "Sol sinyal ver" / "Sağ sinyal ver" | Sinyal LED'ini kontrol eder |
| "Hava durumu nasıl?" | Anlık hava durumunu sesli okur |
| "Şu an saat kaç?" | Güncel saati sesli bildirir |
| "Telegramdan Mevlüt'e naber yaz" | Telegram üzerinden mesaj gönderir |
| "Sistemleri kapat" | Programdan güvenli çıkış yapar |

---

## 📁 Dosya Yapısı
```
├── main.py            # Ana Python asistan uygulaması
├── komutlar.json      # Sesli komut anahtarları ve sistem cevapları
├── main.ino           # Arduino LED kontrol kodları
├── requirements.txt   # Gerekli Python kütüphaneleri listesi
└── .env.example       # Örnek ortam değişkenleri şablonu
```