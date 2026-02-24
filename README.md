# O-Voice-Hub-Online — Jarvis Sesli Kontrol & Otomasyon Sistemi

Bu proje, Python üzerinden sesli komutlar alarak hem bilgisayar üzerinden işlemler yapan (Telegram mesajı gönderme, hava durumu, saat vb.) hem de Arduino üzerinden fiziksel donanımı (LED/Sinyal) kontrol eden kişisel bir asistan uygulamasıdır.

Ses tanıma motoru olarak OpenAI Whisper modeli kullanılmakta; metin okuma ise Google Text-to-Speech (`gTTS`) ile gerçekleştirilmektedir. İnternet bağlantısı zorunludur.

---

## 🌟 Özellikler

* **Çift Dilli Sesli Komut Tanıma:** OpenAI Whisper modeli (`base`) ile hem Türkçe hem de İngilizce komutları otomatik olarak algılar.
* **Donanım Kontrolü:** Seri port üzerinden Arduino'ya bağlı 3 ayrı LED'i (sol sinyal, farlar, sağ sinyal) bağımsız olarak kontrol eder.
* **Telegram Entegrasyonu:** Belirlenen kişilere sesli komutla Telegram üzerinden otomatik mesaj gönderir.
* **Anlık Bilgi:** Open-Meteo API üzerinden hava durumu, tarih ve saat bilgilerini sesli olarak paylaşır.
* **Güvenli Yapı:** API anahtarları ve kişisel ayarlar `.env` dosyası ile korunmaktadır.

---

## ⚙️ Kurulum

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
2. Oluşturduğunuz `.env` dosyasını bir metin editörüyle açın ve aşağıdaki alanları doldurun:

| Değişken | Açıklama |
|---|---|
| `LATITUDE` | Hava durumu için konumunuzun enlemi |
| `LONGITUDE` | Hava durumu için konumunuzun boylamı |
| `SEHIR` | Hava durumu bildiriminde kullanılacak şehir adı |
| `TELEGRAM_TOKEN` | BotFather'dan aldığınız Telegram bot token'ı |
| `VARSAYILAN_CHAT_ID` | Varsayılan mesaj alıcısının Telegram Chat ID'si |
| `ARDUINO_PORT` | Arduino'nun bağlı olduğu seri port (varsayılan: `/dev/ttyUSB0`) |
| `REHBER_<ISIM>` | Rehberdeki her kişi için ayrı bir satır. Örnek: `REHBER_MEVLUT=<chat_id>`. Sesli komutta geçen isim bu değişken adıyla eşleştirilir. |

### 3. Donanım Bağlantısı (Arduino)

1. `main.ino` dosyasını Arduino IDE ile kartınıza yükleyin.
2. LED'lerinizi şu pinlere bağlayın:
   - **LED 1 (Sol Sinyal):** Pin 11
   - **LED 2 (Farlar):** Pin 12
   - **LED 3 (Sağ Sinyal):** Pin 13
3. `.env` dosyanızdaki `ARDUINO_PORT` değişkenini kendi Arduino portunuza göre güncelleyin.
   - Windows: `COM3`
   - Linux: `/dev/ttyUSB0`

### 4. Asistanı Çalıştırma

```bash
python3 main.py
```

---

## 🎙️ Örnek Komutlar

Sistem çalıştıktan sonra mikrofonunuzdan şu tarz komutlar verebilirsiniz:

| Komut | Açıklama |
|---|---|
| "Farları aç" / "Farları kapat" | Far LED'ini (Pin 12) kontrol eder |
| "Sol sinyal ver" / "Sol sinyali kapat" | Sol sinyal LED'ini (Pin 11) kontrol eder |
| "Sağ sinyal ver" / "Sağ sinyali kapat" | Sağ sinyal LED'ini (Pin 13) kontrol eder |
| "Hava durumu nasıl?" | Open-Meteo API'den anlık hava durumunu sesli okur |
| "Şu an saat kaç?" | Güncel saati sesli bildirir |
| "Telegramdan Mevlüt'e naber yaz" | Telegram üzerinden mesaj gönderir |
| "Kapat" / "Shut down" / "Goodbye" | Programdan güvenli çıkış yapar |

> **Not:** Tüm komut anahtar kelimeleri ve sistem yanıtları `komutlar.json` dosyasından yönetilmektedir. Yeni komutlar bu dosyaya eklenerek sistemin davranışı özelleştirilebilir.

---

## 📁 Dosya Yapısı

```
├── main.py            # Ana Python asistan uygulaması
├── komutlar.json      # Sesli komut anahtarları ve sistem cevapları
├── main.ino           # Arduino LED kontrol kodları
├── requirements.txt   # Gerekli Python kütüphaneleri listesi
└── .env.example       # Örnek ortam değişkenleri şablonu
```

---

## 📄 License

This project is licensed under a **Non-Commercial License**.

You may use, modify, and share this project for **personal, educational, and non-commercial purposes only**.

🚫 **Commercial use is strictly prohibited** without prior written permission from the author.

For commercial licensing inquiries, please contact the author.
See the LICENSE file for full details.