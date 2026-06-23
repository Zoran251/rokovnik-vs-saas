# Rokovnik VS Intuitivan softver — Live anketa za beauty salone

Live anketa za vlasnike salona u beauty industriji. Backend: **FastAPI + WebSocket**, frontend: **HTML/CSS (crno-zlatni premium dizajn)**.

## 🔗 Linkovi

- **Live app:** https://rokovnik-vs-saas.onrender.com
- **Admin panel:** https://rokovnik-vs-saas.onrender.com/admin
- **API (JSON):** https://rokovnik-vs-saas.onrender.com/data/submissions

## 🚀 Stack

- **Backend:** Python + FastAPI
- **Real-time:** WebSocket (svi klijenti vide ažuriranja trenutno)
- **Frontend:** HTML + CSS + Vanilla JS
- **存储anje:** JSON fajl (`poll_data.json`)
- **Hosting:** Fly.io

## 📋 Funkcionalnosti

- 5 pitanja za vlasnike beauty salona
- Svako pitanje na svojoj stranici (1/5 → 5/5)
- **Multi-select** (checkbox) — može se odabrati više odgovora
- **"Ostalo:"** opcija sa slobodnim unosom teksta na svakom pitanju
- **Registracija salona** — naziv + kontakt telefon prije ankete
- Progress bar sa brojem odgovorenih pitanja
- Navigacija naprijed/nazad
- Live rezultati koji se ažuriraju u realnom vremenu (WebSocket)
- Premium crno-zlatni dizajn

## 📊 API Endpointi

| Metoda | Putanja | Opis |
|--------|---------|------|
| `GET` | `/` | Frontend stranica |
| `GET` | `/admin` | Admin panel — tabela sa svim odgovorima |
| `GET` | `/data/questions` | 5 pitanja sa opcijama |
| `POST` | `/data/submit` | Slanje odgovora |
| `GET` | `/data/results` | Agregirani rezultati |
| `GET` | `/data/submissions` | Svi sirovi odgovori (JSON) |
| `WS` | `/ws` | WebSocket za live update |

## 🏠 Lokalno pokretanje

```bash
cd poll_app
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Otvori `http://localhost:8000`

## ☁️ Deployment

### Render.com (preporučeno — besplatno, WebSocket radi)

1. Poveži GitHub repo na https://render.com
2. **New +** → **Web Service** → izaberi ovaj repo
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Deploy

### Fly.io

```bash
flyctl launch
flyctl deploy
```

## 📁 Struktura

```
poll_app/
├── main.py              # FastAPI server
├── models.py            # Pydantic modeli
├── index.html           # Frontend
├── poll_data.json       # Podaci (perzistencija)
├── requirements.txt     # Python zavisnosti
├── Dockerfile           # Za Fly.io
├── fly.toml             # Fly.io konfiguracija
└── .gitignore
```
