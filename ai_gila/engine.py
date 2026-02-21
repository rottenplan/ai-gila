import json
import math
import os
import random
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Tuple


@dataclass
class Idea:
    id: str
    title: str
    description: str
    niche: str
    model: str
    price: float
    audience: int
    trend_score: float = 0.5  # New field for trend alignment


class Engine:
    def __init__(self, root: Path):
        self.root = root
        self.state_path = self.root / "ai_gila" / "data" / "state.json"
        self.feedback_path = self.root / "ai_gila" / "data" / "feedback.json"
        self.rng = random.Random()
        self.weights = {
            "tam": 0.45,
            "recurring": 0.25,
            "complexity": -0.2,
            "saturation": -0.15,
            "price_fit": 0.15,
        }
        self.saturated = {"task manager", "todo", "chatbot umum", "notebook ai", "qr menu"}
        self.recurring_models = {"langganan", "saas", "api metered"}
        self.complexity_map = {
            "ekstraksi data": 0.6,
            "otomasi dokumen": 0.4,
            "deteksi penipuan": 0.9,
            "pencarian semantik": 0.5,
            "penjadwalan": 0.3,
            "personalizer": 0.7,
        }
        self.price_bands = [(5, 15), (19, 49), (59, 199), (299, 999)]
        self.trends = {
            "ai_automation": 0.8,
            "privacy_first": 0.5,
            "local_commerce": 0.6,
            "creator_economy": 0.7,
            "sustainability": 0.4
        }
        self._load_state()

    def simulate_market(self):
        """Simulate changing market trends to affect scoring."""
        for k in self.trends:
            change = self.rng.uniform(-0.1, 0.1)
            self.trends[k] = max(0.1, min(1.0, self.trends[k] + change))
        self.weights["trend_alignment"] = 0.2  # Enable trend weight

    def _load_state(self):
        try:
            if self.state_path.exists():
                with open(self.state_path, "r", encoding="utf-8") as f:
                    s = json.load(f)
                    self.weights.update(s.get("weights", {}))
            else:
                self.state_path.parent.mkdir(parents=True, exist_ok=True)
                # Try writing defaults if possible, else ignore
                try:
                    with open(self.state_path, "w", encoding="utf-8") as f:
                        json.dump({"weights": self.weights}, f)
                except OSError:
                    pass
        except Exception:
            # Fallback to defaults if filesystem is read-only or error occurs
            pass

    def _save_state(self):
        try:
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump({"weights": self.weights}, f)
        except OSError:
            # Silently fail on read-only systems (like Vercel runtime)
            pass

    def seed(self, seed: int):
        self.rng.seed(seed)

    def generate_ideas(self, limit: int = 20) -> List[Idea]:
        niches = [
            "akuntansi ukm", "toko online niche", "bengkel motor", "klinik gigi",
            "developer indie", "agri hidroponik", "event organizer", "kursus online",
            "real estat lokal", "kreator konten", "peternak lele", "laundry kiloan",
            "salon kecantikan", "konsultan pajak", "guru privat", "fotografer pernikahan"
        ]
        wildcards = [
            "untuk metaverse", "berbasis suara", "tanpa internet", "gamifikasi",
            "otomatis penuh", "privasi total", "kolaborasi tim", "analitik prediktif"
        ]
        pains = [
            ("ekstraksi data", "menarik data dari file dan chat", "ai_automation"),
            ("otomasi dokumen", "membuat dan memvalidasi dokumen legal", "ai_automation"),
            ("deteksi penipuan", "mengidentifikasi pola risiko", "privacy_first"),
            ("pencarian semantik", "menemukan info dari arsip", "ai_automation"),
            ("penjadwalan", "mengoptimalkan jadwal dan pengingat", "local_commerce"),
            ("personalizer", "menyesuaikan konten dan harga", "creator_economy"),
            ("audit lingkungan", "melacak jejak karbon", "sustainability"),
            ("manajemen stok", "prediksi kebutuhan barang", "local_commerce"),
        ]
        models = ["langganan", "saas", "sekali beli", "marketplace", "api metered"]
        
        ideas: List[Idea] = []
        # Update trends slightly each generation to simulate time passing
        self.simulate_market()
        
        for _ in range(limit * 5):
            niche = self.rng.choice(niches)
            pain_key, pain_desc, trend_key = self.rng.choice(pains)
            model = self.rng.choice(models)
            
            # 20% chance to add a wildcard modifier
            modifier = ""
            if self.rng.random() < 0.2:
                modifier = f" {self.rng.choice(wildcards)}"
            
            audience = int(self.rng.triangular(2000, 500000, 80000))
            band = self.rng.choice(self.price_bands)
            price = round(self.rng.uniform(band[0], band[1]), 2)
            
            title = f"{pain_key.title()}{modifier} untuk {niche.title()}"
            desc = f"Solusi {pain_desc} bagi {niche} dengan pendekatan{modifier}."
            idea_id = f"{abs(hash((niche, pain_key, model, band, modifier)))}"
            
            # Calculate trend alignment
            trend_val = self.trends.get(trend_key, 0.5)
            # Add some randomness to trend score
            trend_score = trend_val * self.rng.uniform(0.8, 1.2)
            
            ideas.append(Idea(idea_id, title, desc, niche, model, price, audience, trend_score))
            
        return self._unique_by_id(ideas)[:limit]

    def _unique_by_id(self, items: List[Idea]) -> List[Idea]:
        seen = set()
        out = []
        for it in items:
            if it.id in seen:
                continue
            seen.add(it.id)
            out.append(it)
        return out

    def score(self, idea: Idea) -> float:
        w = self.weights
        tam = math.log10(max(idea.audience, 10))
        recurring = 1.0 if idea.model in self.recurring_models else 0.0
        comp = self.complexity_map.get(self._infer_capability(idea), 0.5)
        sat = 1.0 if self._is_saturated(idea) else 0.0
        price_fit = self._price_fit(idea.price, idea.audience, idea.model)
        trend = idea.trend_score
        s = (
            w["tam"] * tam
            + w["recurring"] * recurring
            + w["complexity"] * comp
            + w["saturation"] * sat
            + w["price_fit"] * price_fit
            + w.get("trend_alignment", 0.0) * trend
        )
        return round(s, 6)

    def rank(self, ideas: List[Idea], top_k: int = 5) -> List[Tuple[Idea, float]]:
        scored = [(i, self.score(i)) for i in ideas]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def _infer_capability(self, idea: Idea) -> str:
        t = idea.title.lower()
        for k in self.complexity_map:
            if k in t:
                return k
        return "personalizer"

    def _is_saturated(self, idea: Idea) -> bool:
        t = idea.title.lower()
        for k in self.saturated:
            if k in t:
                return True
        return False

    def _price_fit(self, price: float, audience: int, model: str) -> float:
        arpu = price if model in self.recurring_models else price / 12.0
        target = 19 if audience < 10000 else 49 if audience < 100000 else 99
        diff = abs(arpu - target)
        fit = max(0.0, 1.0 - diff / (target + 1))
        return fit

    def evolve_from_feedback(self):
        if not self.feedback_path.exists():
            return
        with open(self.feedback_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not data:
            return
        avg = sum(x.get("rating", 0) for x in data) / max(1, len(data))
        if avg < 3:
            self.weights["tam"] = min(self.weights["tam"] + 0.05, 0.8)
            self.weights["recurring"] = min(self.weights["recurring"] + 0.05, 0.5)
            self.weights["complexity"] = max(self.weights["complexity"] - 0.05, -0.6)
            self.weights["saturation"] = min(self.weights["saturation"] + 0.05, 0.0)
        else:
            self.weights["tam"] = max(self.weights["tam"] - 0.02, 0.2)
            self.weights["price_fit"] = min(self.weights["price_fit"] + 0.03, 0.4)
        self._save_state()

    def export_landing_page(self, idea: Idea, out_dir: Path, variant: str = "control") -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        html = self._landing_template(idea, variant)
        p = out_dir / f"{idea.id}_{variant}.html"
        with open(p, "w", encoding="utf-8") as f:
            f.write(html)
        return p
    
    def generate_business_plan(self, idea: Idea) -> Dict:
        """Generates a detailed business analysis for the idea."""
        # MVP Features based on pain
        pain_to_features = {
            "ekstraksi data": ["Parser dokumen otomatis", "API export JSON/CSV", "Integrasi WhatsApp/Telegram"],
            "otomasi dokumen": ["Template editor drag-and-drop", "Tanda tangan digital", "Version control dokumen"],
            "deteksi penipuan": ["Real-time alert system", "Risk scoring dashboard", "Integrasi data historis"],
            "pencarian semantik": ["Search bar natural language", "Indexing dokumen PDF/Word", "Highlight jawaban otomatis"],
            "penjadwalan": ["Sinkronisasi Google Calendar", "Booking page custom", "Reminder WhatsApp otomatis"],
            "personalizer": ["Tracking behavior user", "Rekomendasi produk dinamis", "A/B testing tools"],
            "audit lingkungan": ["Kalkulator jejak karbon", "Scan struk/invoice", "Laporan compliance standar"],
            "manajemen stok": ["Prediksi demand AI", "Alert stok menipis", "Integrasi POS"],
        }
        
        # Determine base pain key from title/desc (simplified logic)
        mvp_features = ["Dashboard Analytics", "User Management", "Payment Gateway"] # Defaults
        for key, feats in pain_to_features.items():
            if key in idea.title.lower() or key in idea.description.lower():
                mvp_features = feats
                break
        
        # Marketing Hooks
        hooks = [
            f"Cara termudah untuk {idea.niche} mengelola {idea.title.split('untuk')[0].strip()}.",
            f"Lupakan cara lama. Ini revolusi {idea.niche} berbasis AI.",
            f"Hemat 10+ jam per minggu dengan {idea.title}."
        ]
        
        # Revenue Projection (Simulation)
        price_idr = int(idea.price * 15000)
        users_milestone = [10, 100, 1000]
        revenue_proj = []
        for u in users_milestone:
            rev = u * price_idr
            revenue_proj.append({"users": u, "revenue": rev, "revenue_fmt": f"Rp{rev:,}"})
            
        return {
            "mvp_features": mvp_features,
            "marketing_hooks": hooks,
            "revenue_projection": revenue_proj,
            "strategy": f"Fokus pada komunitas {idea.niche} di Facebook/LinkedIn. Tawarkan trial gratis untuk 10 user pertama sebagai validasi.",
            "competitor_sim": "Market leader saat ini generik & mahal. Peluang masuk lewat harga terjangkau & fitur spesifik."
        }

    def consult(self, question: str) -> str:
        """Simple rule-based consultant for business questions."""
        q = question.lower()
        if "modal" in q or "biaya" in q:
            return "Untuk tahap awal, fokus pada MVP tanpa kode (No-Code) atau gunakan API murah. Estimasi modal awal bisa ditekan di bawah Rp 1 juta jika Anda mengerjakan sendiri teknis dasarnya."
        elif "pemasaran" in q or "marketing" in q or "promosi" in q:
            return "Gunakan strategi 'Cold DM' di LinkedIn atau Instagram ke target niche spesifik. Buat konten edukasi pendek di TikTok/Reels tentang masalah yang dihadapi niche tersebut."
        elif "validasi" in q or "ide" in q:
            return "Jangan buat produk dulu! Buat landing page sederhana (seperti yang diexport alat ini), sebar ke komunitas, dan lihat apakah ada yang klik tombol 'Beli' atau daftar waitlist."
        elif "harga" in q or "pricing" in q:
            return "Jangan jual terlalu murah. Niche market berani bayar mahal untuk solusi spesifik. Mulai dari harga yang membuat Anda sedikit tidak nyaman (sedikit mahal), lalu berikan diskon untuk early adopter."
        elif "teknis" in q or "coding" in q:
            return "Gunakan stack yang Anda kuasai. Python/Flask (seperti ini) sudah cukup. Jangan terjebak memilih teknologi canggih tapi tidak ada user."
        else:
            return "Pertanyaan menarik. Fokus utama Anda saat ini seharusnya adalah: Validasi -> Distribusi -> Produk. Apakah Anda sudah memvalidasi ide ke calon user?"

    def _landing_template(self, idea: Idea, variant: str) -> str:
        # Variant logic
        cta_text = "Dapatkan Akses Awal"
        headline_prefix = ""
        bg_color = "#0b0f19"
        
        if variant == "urgent":
            cta_text = "Amankan Slot Terbatas"
            headline_prefix = "<span style='color:#ff4f4f;font-size:0.6em;display:block;text-transform:uppercase;letter-spacing:1px'>Segera Hadir</span>"
        elif variant == "minimal":
            bg_color = "#ffffff"
            text_color = "#111"
        
        # Base styles
        is_light = variant == "minimal"
        body_bg = bg_color
        body_col = "#111" if is_light else "#e6e6e6"
        card_bg = "#f5f5f5" if is_light else "#111725"
        card_border = "#e0e0e0" if is_light else "#1f2738"
        lead_col = "#666" if is_light else "#bdbdbd"

        return f"""<!doctype html>
<html lang="id">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{idea.title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
body{{font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;margin:0;padding:0;background:{body_bg};color:{body_col}}}
.wrap{{max-width:880px;margin:0 auto;padding:48px 24px}}
.hero{{padding:24px 0 8px}}
h1{{font-size:40px;line-height:1.1;margin:0 0 12px}}
p.lead{{font-size:18px;color:{lead_col};margin:0 0 16px}}
.card{{background:{card_bg};border:1px solid {card_border};border-radius:12px;padding:20px;margin:20px 0}}
.cta{{display:inline-block;background:#4f8cff;border:none;border-radius:8px;padding:14px 18px;color:#fff;font-weight:700;text-decoration:none;cursor:pointer}}
.cta:hover{{background:#3a7be0}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.muted{{color:#9aa4b2}}
.badge{{display:inline-block;padding:4px 8px;border-radius:4px;background:#2d3748;font-size:12px;color:#cbd5e0;margin-bottom:8px}}
</style>
<div class="wrap">
  <div class="hero">
    <div class="badge">{variant.upper()} VARIANT</div>
    {headline_prefix}
    <h1>{idea.title}</h1>
    <p class="lead">{idea.description}</p>
    <a href="#" class="cta">{cta_text}</a>
  </div>
  
  <div class="grid">
    <div class="card">
        <h3>Model Bisnis</h3>
        <p>{idea.model.title()}</p>
    </div>
    <div class="card">
        <h3>Estimasi Harga</h3>
        <p>Rp{int(idea.price * 15000):,}</p>
    </div>
  </div>

  <div class="card">
    <h3>Mengapa ini dibutuhkan?</h3>
    <p>Target pasar <strong>{idea.niche}</strong> berjumlah sekitar {idea.audience:,} orang yang potensial membutuhkan solusi ini.</p>
  </div>
  
  <footer style="margin-top:48px;border-top:1px solid {card_border};padding-top:24px;color:{lead_col};font-size:14px">
    &copy; 2024 AI Gila Generator. Konsep ID: {idea.id}
  </footer>
</div>
</html>"""

