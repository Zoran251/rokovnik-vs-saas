import json
import os
from typing import List
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from models import PollSubmission

app = FastAPI(title="Live anketa - Rokovnik VS Intuitivan softver")

QUESTIONS = [
    {
        "id": 0,
        "text": "Kako trenutno vodite evidenciju termina u salonu?",
        "options": [
            "Rokovnik / notes",
            "Desktop softver",
            "Mobilna aplikacija",
            "Kombinacija više načina",
        ],
    },
    {
        "id": 1,
        "text": "Šta vam je najveći izazov u svakodnevnom vođenju salona?",
        "options": [
            "Dogovaranje / zakazivanje termina",
            "Praćenje klijenata",
            "Upravljanje osobljem",
            "Naplata / finansije",
        ],
    },
    {
        "id": 2,
        "text": "Koliko vremena sedmično potrošite na administrativne poslove?",
        "options": ["0 – 2h", "2 – 5h", "5 – 10h", "10h+"],
    },
    {
        "id": 3,
        "text": "Da li biste razmislili o prelasku na intuitivan softver za upravljanje salonom?",
        "options": [
            "Da, već tražim",
            "Da, ako je jednostavan za korištenje",
            "Možda",
            "Ne, zadovoljan/na sam",
        ],
    },
    {
        "id": 4,
        "text": "Koja funkcija softvera bi vam bila najkorisnija?",
        "options": [
            "Online zakazivanje 24/7",
            "Automatski podsjetnici",
            "Praćenje zarade i statistika",
            "CRM baza klijenata",
        ],
    },
]

DATA_FILE = os.path.join(os.path.dirname(__file__), "poll_data.json")
HTML_FILE = os.path.join(os.path.dirname(__file__), "index.html")


def load_data() -> dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"submissions": []}


def save_data(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def compute_results() -> dict:
    data = load_data()
    submissions = data["submissions"]
    total = len(submissions)

    results = []
    for q in QUESTIONS:
        qid = q["id"]
        option_counts = [0] * len(q["options"])
        other_responses = []

        for sub in submissions:
            for answer in sub.get("answers", []):
                if answer["question_id"] == qid:
                    for idx in answer.get("option_indexes", []):
                        if 0 <= idx < len(option_counts):
                            option_counts[idx] += 1
                    if answer.get("other_text"):
                        other_responses.append(answer["other_text"])

        results.append({
            "question_id": qid,
            "question_text": q["text"],
            "options": q["options"],
            "option_counts": option_counts,
            "other_count": len(other_responses),
            "other_responses": other_responses[-20:],
            "total_votes": total,
        })
    return {"results": results, "total_participants": total}


class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: str):
        dead = []
        for ws in self.active:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()


@app.get("/", response_class=HTMLResponse)
async def index():
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/api/questions")
async def get_questions():
    return {"questions": QUESTIONS}


@app.post("/api/submit")
async def submit_poll(submission: PollSubmission):
    data = load_data()
    record = submission.model_dump()
    record["timestamp"] = datetime.utcnow().isoformat()
    data["submissions"].append(record)
    save_data(data)
    result = compute_results()
    await manager.broadcast(json.dumps({"type": "update", **result}))
    return {"status": "ok", "total_participants": len(data["submissions"])}


@app.get("/api/results")
async def get_results():
    return compute_results()


@app.get("/api/submissions")
async def get_submissions():
    data = load_data()
    return {"submissions": data["submissions"]}


@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    data = load_data()
    submissions = data["submissions"]

    def fmt_answers(ans_list):
        parts = []
        for a in ans_list:
            q = next((q for q in QUESTIONS if q["id"] == a["question_id"]), None)
            if not q:
                continue
            selected = [q["options"][i] for i in a.get("option_indexes", [])]
            if a.get("other_text"):
                selected.append(f'Ostalo: "{a["other_text"]}"')
            parts.append(f"<strong>Q{a['question_id']+1}:</strong> {', '.join(selected) if selected else '—'}")
        return "<br>".join(parts)

    rows = ""
    for i, sub in enumerate(reversed(submissions), 1):
        rows += f"""<tr>
            <td>{i}</td>
            <td>{sub.get('salon_name', '—')}</td>
            <td>{sub.get('phone', '—')}</td>
            <td>{sub.get('timestamp', '—')[:19].replace('T', ' ')}</td>
            <td>{fmt_answers(sub.get('answers', []))}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="bs">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Admin — Odgovori ankete</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
    font-family: 'Inter', sans-serif;
    background: #070708;
    color: #e0e0e0;
    padding: 40px 24px;
}}
h1 {{
    font-size: 20px;
    font-weight: 600;
    color: #D4AF37;
    margin-bottom: 4px;
}}
p {{ color: #888; font-size: 13px; margin-bottom: 32px; }}
table {{
    width: 100%;
    max-width: 1100px;
    border-collapse: collapse;
    font-size: 13px;
}}
th {{
    text-align: left;
    padding: 12px 14px;
    border-bottom: 1px solid #1e1e22;
    color: #D4AF37;
    font-weight: 600;
    font-size: 11px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}}
td {{
    padding: 14px;
    border-bottom: 1px solid #1a1a1e;
    vertical-align: top;
    line-height: 1.5;
}}
tr:hover td {{ background: rgba(212,175,55,0.03); }}
.row-num {{ color: #555; font-size: 12px; }}
.salon {{ color: #fff; font-weight: 500; }}
.phone {{ color: #999; }}
.time {{ color: #666; font-size: 12px; }}
.answers {{ color: #ccc; }}
.answers strong {{ color: #D4AF37; font-weight: 500; }}
.no-data {{ color: #555; text-align:center; padding:60px 0; }}
.no-data span {{ font-size: 40px; display:block; margin-bottom:12px; }}
</style>
</head>
<body>
<h1>📋 Odgovori ankete</h1>
<p>Ukupno učesnika: <strong style="color:#D4AF37">{len(submissions)}</strong></p>

<table>
<thead>
<tr>
    <th style="width:36px">#</th>
    <th>Salon</th>
    <th style="width:140px">Telefon</th>
    <th style="width:150px">Vrijeme</th>
    <th>Odgovori</th>
</tr>
</thead>
<tbody>
{f"<tr><td colspan='5' class='no-data'><span>&#128203;</span>Još nema prikupljenih odgovora.</td></tr>" if not submissions else rows}
</tbody>
</table>
</body>
</html>"""
    return html


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)
    except Exception:
        manager.disconnect(ws)


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
