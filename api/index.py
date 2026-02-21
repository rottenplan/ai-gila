from flask import Flask, render_template_string, request, jsonify
from pathlib import Path
from ai_gila.engine import Engine

app = Flask(__name__)

# Initialize engine with current directory as root
root = Path(__file__).resolve().parents[1]
eng = Engine(root)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI GILA - Generator Ide Bisnis</title>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Space Grotesk', sans-serif; background: #0b0f19; color: #e6e6e6; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { font-size: 2.5rem; background: linear-gradient(90deg, #4f8cff, #a0d2eb); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px; }
        .subtitle { color: #8899ac; margin-bottom: 30px; }
        .btn { background: #4f8cff; color: white; border: none; padding: 12px 24px; font-size: 1.1rem; border-radius: 8px; cursor: pointer; font-family: inherit; font-weight: bold; transition: all 0.2s; }
        .btn:hover { background: #3a7be0; transform: translateY(-2px); }
        .ideas-list { margin-top: 40px; }
        .idea-card { background: #111725; border: 1px solid #1f2738; padding: 20px; margin-bottom: 16px; border-radius: 12px; position: relative; overflow: hidden; transition: transform 0.2s; }
        .idea-card:hover { transform: translateY(-2px); border-color: #3a7be0; }
        .idea-card::before { content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: #2d3748; }
        .idea-card.hot::before { background: #ff4f4f; }
        .idea-header { display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px; }
        .idea-title { font-size: 1.25rem; font-weight: bold; margin: 0; }
        .idea-score { font-size: 0.9rem; color: #4f8cff; background: rgba(79, 140, 255, 0.1); padding: 4px 8px; border-radius: 4px; }
        .idea-desc { color: #cbd5e0; line-height: 1.5; }
        .meta { display: flex; gap: 12px; margin-top: 12px; font-size: 0.85rem; color: #8899ac; align-items: center; }
        .tag { background: #1a202c; padding: 4px 8px; border-radius: 4px; }
        .hot-badge { background: #ff4f4f; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; vertical-align: middle; margin-left: 8px; }
        
        .btn-analyze { background: transparent; border: 1px solid #4f8cff; color: #4f8cff; padding: 4px 12px; font-size: 0.8rem; border-radius: 4px; cursor: pointer; margin-left: auto; text-decoration: none; }
        .btn-analyze:hover { background: rgba(79, 140, 255, 0.1); }

        /* Modal Styles */
        .modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 1000; align-items: center; justify-content: center; }
        .modal-overlay.active { display: flex; }
        .modal-content { background: #111725; width: 90%; max-width: 600px; max-height: 90vh; overflow-y: auto; border-radius: 12px; border: 1px solid #2d3748; padding: 24px; position: relative; }
        .close-btn { position: absolute; top: 16px; right: 16px; background: none; border: none; color: #8899ac; font-size: 1.5rem; cursor: pointer; }
        .section-title { color: #4f8cff; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; margin-top: 24px; margin-bottom: 12px; font-weight: bold; border-bottom: 1px solid #1f2738; padding-bottom: 8px; }
        .feature-list, .hook-list { list-style: none; padding: 0; margin: 0; }
        .feature-list li { margin-bottom: 8px; padding-left: 20px; position: relative; }
        .feature-list li::before { content: '✓'; color: #48bb78; position: absolute; left: 0; }
        .hook-list li { margin-bottom: 8px; font-style: italic; color: #a0aec0; border-left: 3px solid #4a5568; padding-left: 12px; }
        .rev-table { width: 100%; border-collapse: collapse; margin-top: 12px; }
        .rev-table th { text-align: left; color: #8899ac; font-weight: normal; padding-bottom: 8px; border-bottom: 1px solid #2d3748; }
        .rev-table td { padding: 8px 0; border-bottom: 1px solid #1f2738; }
        .rev-val { color: #48bb78; font-family: monospace; font-size: 1.1rem; }
        footer { margin-top: 60px; text-align: center; color: #4a5568; font-size: 0.9rem; }
    </style>
    <script>
        async function analyzeIdea(ideaId) {
            const btn = document.getElementById(`btn-${ideaId}`);
            btn.innerText = "Menganalisis...";
            try {
                const res = await fetch(`/analyze/${ideaId}`);
                const data = await res.json();
                
                // Populate Modal
                document.getElementById('m-title').innerText = data.title;
                document.getElementById('m-desc').innerText = data.description;
                document.getElementById('m-strategy').innerText = data.plan.strategy;
                document.getElementById('m-comp').innerText = data.plan.competitor_sim;
                
                const featList = document.getElementById('m-features');
                featList.innerHTML = data.plan.mvp_features.map(f => `<li>${f}</li>`).join('');
                
                const hookList = document.getElementById('m-hooks');
                hookList.innerHTML = data.plan.marketing_hooks.map(h => `<li>"${h}"</li>`).join('');
                
                const revList = document.getElementById('m-rev');
                revList.innerHTML = data.plan.revenue_projection.map(r => 
                    `<tr><td>${r.users} User</td><td class="rev-val">${r.revenue_fmt} / bln</td></tr>`
                ).join('');

                document.getElementById('modal').classList.add('active');
            } catch (e) {
                alert("Gagal menganalisis. Coba lagi.");
            } finally {
                btn.innerText = "Bedah Bisnis ➜";
            }
        }
        
        function closeModal() {
            document.getElementById('modal').classList.remove('active');
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>AI GILA GENERATOR</h1>
        <p class="subtitle">Software penghasil ide bisnis micro-SaaS yang "tidak terpikirkan" & berkembang sendiri.</p>
        
        <form action="/" method="post">
            <button type="submit" class="btn">⚡ Generate Ide Baru</button>
        </form>

        {% if ideas %}
        <div class="ideas-list">
            <h2 style="font-size: 1.5rem; margin-bottom: 20px;">Hasil Analisis Pasar Terkini</h2>
            {% for idea, score in ideas %}
            <div class="idea-card {% if idea.trend_score > 0.7 %}hot{% endif %}">
                <div class="idea-header">
                    <h3 class="idea-title">
                        {{ idea.title }}
                        {% if idea.trend_score > 0.7 %}<span class="hot-badge">TRENDING</span>{% endif %}
                    </h3>
                    <span class="idea-score">Score: {{ "%.4f"|format(score) }}</span>
                </div>
                <p class="idea-desc">{{ idea.description }}</p>
                <div class="meta">
                    <span class="tag">{{ idea.model|title }}</span>
                    <span class="tag">Rp{{ "{:,}".format((idea.price * 15000)|int) }}</span>
                    <button id="btn-{{ idea.id }}" class="btn-analyze" onclick="analyzeIdea('{{ idea.id }}')">Bedah Bisnis ➜</button>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}

        <footer>
            <p>Ditenagai oleh AI Gila Engine v2.0 • Berjalan di Vercel</p>
        </footer>
    </div>

    <!-- Modal Analysis -->
    <div id="modal" class="modal-overlay" onclick="if(event.target === this) closeModal()">
        <div class="modal-content">
            <button class="close-btn" onclick="closeModal()">×</button>
            <h2 id="m-title" style="margin-top:0">Judul Ide</h2>
            <p id="m-desc" style="color:#a0aec0; margin-bottom:24px">Deskripsi singkat ide...</p>
            
            <div class="section-title">✨ Fitur MVP Wajib</div>
            <ul id="m-features" class="feature-list"></ul>
            
            <div class="section-title">📢 Viral Hooks (Marketing)</div>
            <ul id="m-hooks" class="hook-list"></ul>
            
            <div class="section-title">💰 Potensi Cuan (Estimasi)</div>
            <table class="rev-table">
                <thead><tr><th>Milestone</th><th>Pendapatan Bulanan</th></tr></thead>
                <tbody id="m-rev"></tbody>
            </table>
            
            <div class="section-title">⚔️ Strategi & Kompetisi</div>
            <p style="font-size:0.9rem; color:#cbd5e0; margin-bottom:8px"><strong>Strategi:</strong> <span id="m-strategy"></span></p>
            <p style="font-size:0.9rem; color:#cbd5e0"><strong>Situasi Pasar:</strong> <span id="m-comp"></span></p>
        </div>
    </div>
</body>
</html>
"""

# Store temporary ideas in memory for the session (simple cache for demo)
# In production, use a database or Redis
IDEA_CACHE = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    ideas_data = []
    if request.method == 'POST':
        # Generate and rank
        raw_ideas = eng.generate_ideas(limit=20)
        ranked = eng.rank(raw_ideas, top_k=5)
        ideas_data = ranked
        
        # Cache for analysis
        global IDEA_CACHE
        IDEA_CACHE = {i.id: i for i, _ in ranked}
    
    return render_template_string(HTML_TEMPLATE, ideas=ideas_data)

@app.route('/analyze/<idea_id>')
def analyze(idea_id):
    idea = IDEA_CACHE.get(idea_id)
    if not idea:
        return jsonify({"error": "Idea not found"}), 404
    
    plan = eng.generate_business_plan(idea)
    return jsonify({
        "id": idea.id,
        "title": idea.title,
        "description": idea.description,
        "plan": plan
    })


# Vercel requires the app to be named 'app'
