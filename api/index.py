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
        .idea-card { background: #111725; border: 1px solid #1f2738; padding: 20px; margin-bottom: 16px; border-radius: 12px; position: relative; overflow: hidden; }
        .idea-card::before { content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: #2d3748; }
        .idea-card.hot::before { background: #ff4f4f; }
        .idea-header { display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px; }
        .idea-title { font-size: 1.25rem; font-weight: bold; margin: 0; }
        .idea-score { font-size: 0.9rem; color: #4f8cff; background: rgba(79, 140, 255, 0.1); padding: 4px 8px; border-radius: 4px; }
        .idea-desc { color: #cbd5e0; line-height: 1.5; }
        .meta { display: flex; gap: 12px; margin-top: 12px; font-size: 0.85rem; color: #8899ac; }
        .tag { background: #1a202c; padding: 4px 8px; border-radius: 4px; }
        .hot-badge { background: #ff4f4f; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; vertical-align: middle; margin-left: 8px; }
        footer { margin-top: 60px; text-align: center; color: #4a5568; font-size: 0.9rem; }
    </style>
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
                    <span class="tag">~{{ "{:,}".format(idea.audience) }} Audiens</span>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}

        <footer>
            <p>Ditenagai oleh AI Gila Engine v1.0 • Berjalan di Vercel</p>
        </footer>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    ideas_data = []
    if request.method == 'POST':
        # Generate and rank
        raw_ideas = eng.generate_ideas(limit=20)
        ranked = eng.rank(raw_ideas, top_k=5)
        ideas_data = ranked
    
    return render_template_string(HTML_TEMPLATE, ideas=ideas_data)

# Vercel requires the app to be named 'app'
