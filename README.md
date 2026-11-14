# Bass Music Auto Post (YouTube Daily Pipeline) 🚗🎵

Har kuni Toshkent vaqti bilan soat **16:00** da YouTube kanaliga avtomatik ravishda yuqori sifatli bas musiqa va mashinalar ishtirokidagi videoni montaj qilib yuklovchi bulutli tizim (GitHub Actions).

---

## ⚡ Tizim qanday ishlaydi?

1. **Bas musiqa:** Avtomatik tarzda mualliflik huquqisiz kuchli bas / phonk / trap musiqa olinadi.
2. **Mashina videolari:** Pexels API orqali yuqori sifatli (1080p/4K) tungi shahar, drift va superkarlar videolari yuklab olinadi.
3. **FFmpeg Montaj:** Videolar musiqa davomiyligiga moslab ulanadi, ranglar va kontrast sozlanadi.
4. **Gemini AI:** Video uchun yuqori ko'rishlar keltiruvchi (High-CTR) sarlavha, tavsif va teglar yozib beradi.
5. **YouTube Upload:** Tayyor video avtomatik ravishda YouTube kanalga yuklanadi.

---

## 🔑 GitHub Secrets sozlamalari

GitHub repozitoriyangizda: **Settings** -> **Secrets and variables** -> **Actions** bo'limiga kiring va quyidagi 4 ta sirni qo'shing:

| Secret Nomi | Tavsif | Qayerdan olinadi? |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | Gemini AI kaliti | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `PEXELS_API_KEY` | Mashina videolari uchun API | [Pexels API](https://www.pexels.com/api/) (bepul) |
| `YOUTUBE_CLIENT_SECRET_JSON` | Google Cloud OAuth JSON | Google Cloud Console (YouTube Data API v3) |
| `YOUTUBE_REFRESH_TOKEN` | Doimiy yuklash ruxsati | `setup_youtube_auth.py` orqali olinadi |

---

## ⏰ Jadval

GitHub Actions fayli (`.github/workflows/daily_bass_video.yml`):
- Har kuni **11:00 UTC** da ishga tushadi (Toshkent vaqti bilan aynan **16:00**).
- Xohlagan paytda GitHub'dagi **"Actions"** tabidan **"Run workflow"** tugmasini bosib darhol sinab ko'rish mumkin.
