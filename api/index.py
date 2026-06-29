from __future__ import annotations

import json
import os
import re
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from pydantic import BaseModel, Field

app = FastAPI(title="HoaxCheck API")

# Frontend dan API berada pada domain yang sama saat di Vercel.
# CORS ini tetap mengizinkan pengujian frontend dari localhost.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


class BeritaRequest(BaseModel):
    teks: str = Field(..., max_length=2000)


SYSTEM_PROMPT = """
Kamu adalah sistem deteksi hoaks berbasis AI untuk Bahasa Indonesia.
Tugasmu adalah menganalisis teks berita atau klaim yang diberikan dan menentukan apakah itu HOAKS atau FAKTA.

Berikan respons HANYA dalam format JSON berikut, tanpa markdown dan tanpa backtick:
{
  "label": "HOAKS" atau "FAKTA",
  "confidence": angka antara 0.0 hingga 1.0,
  "alasan": "Penjelasan singkat 2-3 kalimat mengapa kamu menyimpulkan ini hoaks atau fakta",
  "indikator": ["indikator 1", "indikator 2", "indikator 3"],
  "saran": "Saran singkat untuk pembaca"
}

Panduan analisis:
- Perhatikan klaim yang tidak masuk akal atau berlebihan.
- Cari tanda-tanda judul clickbait atau sensasional.
- Pertimbangkan konteks dan logika informasi.
- Perhatikan penggunaan bahasa emosional berlebihan.
- confidence 0.9+ = sangat yakin, 0.7-0.9 = cukup yakin, 0.5-0.7 = kurang yakin.
- Jangan mengklaim kepastian faktual bila informasi tidak dapat diverifikasi dari teks. Gunakan saran untuk memeriksa sumber primer atau pemeriksa fakta tepercaya.
"""


def get_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY belum diatur pada Environment Variables.")
    return Groq(api_key=api_key)


def parse_model_json(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\s*```$", "", raw)
    result = json.loads(raw)
    if not isinstance(result, dict):
        raise ValueError("Output model bukan objek JSON.")
    return result


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/deteksi")
async def deteksi_hoaks(req: BeritaRequest) -> dict[str, Any]:
    teks = req.teks.strip()

    if not teks:
        return {"error": "Teks tidak boleh kosong."}
    if len(teks) < 20:
        return {"error": "Teks terlalu pendek. Masukkan minimal 20 karakter."}

    try:
        response = get_client().chat.completions.create(
            model=os.getenv("GROQ_MODEL", "qwen/qwen3.6-27b"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Analisis teks berikut:\n\"{teks}\""},
            ],
            temperature=0.2,
            max_tokens=700,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content or "{}"
        result = parse_model_json(raw)

        label = str(result.get("label", "")).upper().strip()
        if label not in {"HOAKS", "FAKTA"}:
            return {"error": "Model menghasilkan label yang tidak valid. Coba lagi."}

        try:
            confidence = float(result.get("confidence", 0))
        except (TypeError, ValueError):
            confidence = 0.0

        confidence = max(0.0, min(1.0, confidence))
        indikator = result.get("indikator", [])
        if not isinstance(indikator, list):
            indikator = []

        return {
            "label": label,
            "confidence": confidence,
            "alasan": str(result.get("alasan", "Analisis tidak tersedia.")),
            "indikator": [str(item) for item in indikator[:5]],
            "saran": str(result.get("saran", "Periksa kembali sumber informasi tepercaya.")),
        }

    except json.JSONDecodeError:
        return {"error": "Respons AI tidak dapat dibaca. Coba analisis kembali."}
    except Exception:
        # Jangan menampilkan detail internal atau kunci layanan kepada pengguna.
        return {"error": "Analisis belum dapat diproses. Periksa konfigurasi API atau coba beberapa saat lagi."}
