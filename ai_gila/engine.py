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

    def generate_landing_page_html(self, idea: Idea) -> str:
        """Generates a complete single-file HTML landing page for the idea."""
        # Get richer data
        plan = self.generate_business_plan(idea)
        
        # Color palette generation based on niche hash
        h = hash(idea.niche)
        hue = h % 360
        primary_color = f"hsl({hue}, 70%, 50%)"
        secondary_color = f"hsl({(hue + 40) % 360}, 80%, 60%)"
        
        features_html = ""
        for f in plan['mvp_features']:
            features_html += f"""
            <div class="feature-card">
                <div class="icon">✨</div>
                <h3>{f}</h3>
                <p>Fitur andalan untuk {idea.niche}.</p>
            </div>"""
            
        hooks_html = ""
        for h in plan['marketing_hooks']:
             hooks_html += f"<li>✅ {h}</li>"

        return f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{idea.title} - Early Access</title>
    <style>
        :root {{
            --primary: {primary_color};
            --secondary: {secondary_color};
            --bg: #0f172a;
            --text: #f8fafc;
            --card-bg: #1e293b;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            line-height: 1.6;
        }}
        .container {{ max-width: 1000px; margin: 0 auto; padding: 20px; }}
        header {{ display: flex; justify-content: space-between; align-items: center; padding: 20px 0; }}
        .logo {{ font-weight: 800; font-size: 1.5rem; background: linear-gradient(to right, var(--primary), var(--secondary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        
        .hero {{ text-align: center; padding: 80px 20px; }}
        h1 {{ font-size: 3.5rem; line-height: 1.2; margin-bottom: 20px; background: linear-gradient(to right, #fff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .subtitle {{ font-size: 1.25rem; color: #94a3b8; max-width: 600px; margin: 0 auto 40px; }}
        
        .btn {{ display: inline-block; background: var(--primary); color: white; padding: 16px 32px; border-radius: 50px; text-decoration: none; font-weight: bold; font-size: 1.1rem; transition: transform 0.2s; border: none; cursor: pointer; }}
        .btn:hover {{ transform: translateY(-2px); box-shadow: 0 10px 20px -10px var(--primary); }}
        
        .features {{ padding: 80px 20px; background: #0b1120; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 30px; }}
        .feature-card {{ background: var(--card-bg); padding: 30px; border-radius: 16px; border: 1px solid #334155; }}
        .icon {{ font-size: 2rem; margin-bottom: 16px; }}
        
        .pricing {{ text-align: center; padding: 80px 20px; }}
        .price-card {{ background: linear-gradient(145deg, var(--card-bg), #0f172a); border: 1px solid var(--primary); padding: 40px; border-radius: 20px; max-width: 400px; margin: 0 auto; }}
        .price {{ font-size: 3rem; font-weight: 800; color: var(--primary); }}
        .period {{ color: #94a3b8; font-size: 1rem; }}
        .benefits {{ list-style: none; padding: 0; text-align: left; margin: 30px 0; }}
        .benefits li {{ margin-bottom: 12px; font-size: 1.1rem; }}
        
        footer {{ text-align: center; padding: 40px; color: #64748b; border-top: 1px solid #1e293b; }}
        
        @media (max-width: 768px) {{
            h1 {{ font-size: 2.5rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">{idea.title}</div>
            <nav>
                <a href="#features" style="color: #fff; text-decoration: none; margin-right: 20px">Fitur</a>
                <a href="#pricing" style="color: #fff; text-decoration: none">Harga</a>
            </nav>
        </header>
        
        <section class="hero">
            <h1>{idea.title}</h1>
            <p class="subtitle">{idea.description}</p>
            <a href="#pricing" class="btn">Mulai Sekarang 🚀</a>
            <p style="margin-top: 20px; font-size: 0.9rem; color: #64748b">Tanpa kartu kredit • Batalkan kapan saja</p>
        </section>
    </div>
    
    <section id="features" class="features">
        <div class="container">
            <h2 style="text-align: center; font-size: 2.5rem; margin-bottom: 50px">Solusi Cerdas untuk {idea.niche.title()}</h2>
            <div class="grid">
                {features_html}
            </div>
        </div>
    </section>
    
    <section id="pricing" class="pricing">
        <div class="container">
            <div class="price-card">
                <h3>Early Bird Offer</h3>
                <div class="price">Rp{int(idea.price * 15000):,}<span class="period">/{'bulan' if idea.model in ['langganan', 'saas'] else 'lifetime'}</span></div>
                <ul class="benefits">
                    {hooks_html}
                    <li>🔒 Jaminan Uang Kembali 30 Hari</li>
                    <li>📞 Support Prioritas 24/7</li>
                </ul>
                <button class="btn" style="width: 100%" onclick="alert('Terima kasih atas minat Anda! Kami sedang dalam tahap pengembangan.')">Ambil Promo Ini</button>
            </div>
        </div>
    </section>
    
    <footer>
        <p>&copy; 2024 {idea.title}. Generated by AI Gila.</p>
    </footer>
</body>
</html>"""

    def export_landing_page(self, idea: Idea, out_dir: Path, variant: str = "control") -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        html = self.generate_landing_page_html(idea)
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



