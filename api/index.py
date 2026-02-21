from flask import Flask, render_template_string, request, jsonify
from pathlib import Path
from dataclasses import asdict
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
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #050505;
            --glass-bg: rgba(255, 255, 255, 0.03);
            --glass-border: rgba(255, 255, 255, 0.08);
            --accent-primary: #00f2ff;
            --accent-secondary: #bd00ff;
            --text-main: #ffffff;
            --text-muted: #8899ac;
        }
        
        * { box-sizing: border-box; }
        
        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-dark);
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(189, 0, 255, 0.15) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(0, 242, 255, 0.15) 0%, transparent 40%);
            color: var(--text-main);
            margin: 0;
            padding: 0;
            min-height: 100vh;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        /* Header */
        header {
            text-align: center;
            margin-bottom: 60px;
            animation: fadeInDown 0.8s ease-out;
        }

        h1 {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 3.5rem;
            margin: 0 0 16px;
            background: linear-gradient(135deg, #fff 30%, var(--accent-primary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -1px;
        }

        .subtitle {
            font-size: 1.1rem;
            color: var(--text-muted);
            max-width: 600px;
            margin: 0 auto;
            line-height: 1.6;
        }

        /* Generator Button */
        .action-area {
            display: flex;
            justify-content: center;
            margin-bottom: 50px;
        }

        .btn-generate {
            position: relative;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
            color: #fff;
            border: none;
            padding: 16px 40px;
            font-size: 1.2rem;
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 0 20px rgba(0, 242, 255, 0.3);
            overflow: hidden;
        }

        .btn-generate::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: 0.5s;
        }

        .btn-generate:hover {
            transform: scale(1.05);
            box-shadow: 0 0 40px rgba(189, 0, 255, 0.5);
        }

        .btn-generate:hover::before {
            left: 100%;
        }

        /* Tabs */
        .tabs {
            display: flex;
            justify-content: center;
            gap: 16px;
            margin-bottom: 30px;
        }

        .tab-btn {
            background: transparent;
            border: 1px solid var(--glass-border);
            color: var(--text-muted);
            padding: 12px 24px;
            border-radius: 50px;
            cursor: pointer;
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 600;
            transition: all 0.3s;
        }

        .tab-btn.active {
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
            border-color: var(--accent-primary);
            box-shadow: 0 0 15px rgba(0, 242, 255, 0.2);
        }

        .tab-btn:hover {
            color: #fff;
            border-color: rgba(255, 255, 255, 0.5);
        }

        /* Cards */
        .ideas-grid {
            display: grid;
            gap: 24px;
        }

        .idea-card {
            background: var(--glass-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 24px;
            transition: all 0.3s ease;
            animation: slideUp 0.5s ease-out forwards;
            opacity: 0;
            transform: translateY(20px);
            position: relative;
        }

        .btn-save {
            position: absolute;
            top: 24px;
            right: 24px;
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--glass-border);
            color: var(--text-muted);
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;
            z-index: 10;
        }

        .btn-save:hover {
            background: rgba(255,255,255,0.1);
            transform: scale(1.1);
        }

        .btn-save.saved {
            background: var(--accent-secondary);
            color: #fff;
            border-color: var(--accent-secondary);
            box-shadow: 0 0 10px rgba(189, 0, 255, 0.4);
        }

        .idea-card:nth-child(1) { animation-delay: 0.1s; }
        .idea-card:nth-child(2) { animation-delay: 0.2s; }
        .idea-card:nth-child(3) { animation-delay: 0.3s; }
        .idea-card:nth-child(4) { animation-delay: 0.4s; }
        .idea-card:nth-child(5) { animation-delay: 0.5s; }

        .idea-card:hover {
            transform: translateY(-5px);
            border-color: rgba(255,255,255,0.2);
            background: rgba(255,255,255,0.05);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }

        .card-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        }

        .idea-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.4rem;
            font-weight: 700;
            margin: 0;
            color: #fff;
        }

        .score-badge {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 0.9rem;
            background: rgba(0, 242, 255, 0.1);
            color: var(--accent-primary);
            padding: 6px 12px;
            border-radius: 20px;
            border: 1px solid rgba(0, 242, 255, 0.2);
        }

        .idea-desc {
            color: #a0a0a0;
            line-height: 1.6;
            margin-bottom: 20px;
        }

        .card-stats {
            display: flex;
            gap: 16px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }

        .stat-pill {
            display: flex;
            align-items: center;
            gap: 6px;
            background: rgba(255,255,255,0.05);
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 0.85rem;
            color: #ccc;
        }

        .stat-icon { opacity: 0.7; }

        .btn-analyze {
            width: 100%;
            background: transparent;
            border: 1px solid var(--glass-border);
            color: #fff;
            padding: 12px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 8px;
        }

        .btn-analyze:hover {
            background: rgba(255,255,255,0.1);
            border-color: #fff;
        }

        /* Modal */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.85);
            backdrop-filter: blur(5px);
            z-index: 1000;
            display: none;
            justify-content: center;
            align-items: center;
            opacity: 0;
            transition: opacity 0.3s;
        }

        .modal-overlay.active {
            display: flex;
            opacity: 1;
        }

        .modal-content {
            background: #0f1218;
            border: 1px solid var(--glass-border);
            width: 90%;
            max-width: 650px;
            max-height: 90vh;
            border-radius: 20px;
            padding: 30px;
            overflow-y: auto;
            position: relative;
            transform: scale(0.9);
            transition: transform 0.3s;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        }

        .modal-overlay.active .modal-content {
            transform: scale(1);
        }

        .close-btn {
            position: absolute;
            top: 20px;
            right: 20px;
            background: none;
            border: none;
            color: #666;
            font-size: 1.5rem;
            cursor: pointer;
        }

        .close-btn:hover { color: #fff; }

        .modal-header { margin-bottom: 24px; border-bottom: 1px solid var(--glass-border); padding-bottom: 20px; }
        .modal-title { font-family: 'Space Grotesk'; font-size: 1.8rem; margin: 0 0 8px; }
        
        .section-header {
            color: var(--accent-primary);
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 0.8rem;
            font-weight: 700;
            margin-top: 24px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .feature-item {
            display: flex;
            gap: 12px;
            margin-bottom: 12px;
            background: rgba(255,255,255,0.03);
            padding: 12px;
            border-radius: 8px;
        }

        .check-icon { color: var(--accent-secondary); }

        .hook-box {
            background: linear-gradient(90deg, rgba(189,0,255,0.1), transparent);
            border-left: 3px solid var(--accent-secondary);
            padding: 12px;
            margin-bottom: 10px;
            font-style: italic;
            color: #ddd;
        }

        table { width: 100%; border-collapse: collapse; }
        td, th { padding: 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.05); }
        th { color: var(--text-muted); font-weight: 500; font-size: 0.9rem; }
        .money { font-family: 'Space Grotesk'; color: #48bb78; font-weight: 700; }

        /* Chat Widget */
        .chat-widget {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            transition: all 0.3s;
            z-index: 2000;
        }

        .chat-widget:hover {
            transform: scale(1.1);
        }

        .chat-icon {
            font-size: 28px;
            color: white;
        }

        .chat-window {
            position: fixed;
            bottom: 100px;
            right: 30px;
            width: 350px;
            height: 500px;
            max-width: calc(100% - 60px);
            max-height: 60vh;
            background: #111725;
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            display: none;
            flex-direction: column;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
            z-index: 2000;
            overflow: hidden;
            animation: slideUp 0.3s ease-out;
        }

        @media (max-width: 600px) {
            .chat-window {
                right: 20px;
                bottom: 90px;
                width: calc(100% - 40px);
            }
            
            .modal-content {
                width: 95%;
                padding: 20px;
            }
            
            h1 { font-size: 2.5rem; }
        }

        .chat-header {
            background: rgba(255,255,255,0.05);
            padding: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--glass-border);
        }

        .chat-body {
            flex: 1;
            padding: 16px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .chat-input-area {
            padding: 16px;
            border-top: 1px solid var(--glass-border);
            display: flex;
            gap: 10px;
        }

        .chat-input {
            flex: 1;
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 10px 16px;
            color: #fff;
            outline: none;
        }

        .chat-send {
            background: var(--accent-primary);
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            cursor: pointer;
            color: #000;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .msg {
            max-width: 80%;
            padding: 10px 14px;
            border-radius: 12px;
            font-size: 0.9rem;
            line-height: 1.4;
        }

        .msg-ai {
            background: rgba(255,255,255,0.1);
            align-self: flex-start;
            border-bottom-left-radius: 2px;
        }

        .msg-user {
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 2px;
        }

        /* Animations */
        @keyframes fadeInDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

        /* Trending Badge */
        .trending {
            background: linear-gradient(45deg, #ff4d4d, #f9cb28);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: bold;
            font-size: 0.8rem;
            margin-left: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    <script>
        async function analyzeIdea(btn) {
            // Get idea data from the parent card
            const card = btn.closest('.idea-card');
            let ideaData;
            try {
                // Handle potential string vs object issues in dataset
                const raw = card.dataset.idea;
                // If it's already an object (rare in dataset), use it, otherwise parse
                ideaData = typeof raw === 'string' ? JSON.parse(raw) : raw;
            } catch (e) {
                alert("Error data idea");
                return;
            }

            const originalText = btn.innerHTML;
            btn.innerHTML = `<span style="animation: spin 1s linear infinite">↻</span> Menganalisis...`;
            
            try {
                const res = await fetch('/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(ideaData)
                });
                
                if (!res.ok) throw new Error("Gagal analisis");
                
                const data = await res.json();
                
                document.getElementById('m-logo').innerHTML = data.plan.logo_svg;
                document.getElementById('m-title').innerText = data.title;
                document.getElementById('m-desc').innerText = data.description;
                document.getElementById('m-strategy').innerText = data.plan.strategy;
                document.getElementById('m-comp').innerText = data.plan.competitor_sim;
                
                // Render SWOT
                const swot = data.plan.swot;
                const swotHtml = `
                    <div style="background: rgba(72, 187, 120, 0.1); border: 1px solid rgba(72, 187, 120, 0.3); padding: 12px; border-radius: 8px;">
                        <strong style="color: #48bb78; display:block; margin-bottom:8px">STRENGTHS</strong>
                        <ul style="margin:0; padding-left:20px; color:#ccc; font-size:0.9em">${swot.strengths.map(s => `<li>${s}</li>`).join('')}</ul>
                    </div>
                    <div style="background: rgba(237, 137, 54, 0.1); border: 1px solid rgba(237, 137, 54, 0.3); padding: 12px; border-radius: 8px;">
                        <strong style="color: #ed8936; display:block; margin-bottom:8px">WEAKNESSES</strong>
                        <ul style="margin:0; padding-left:20px; color:#ccc; font-size:0.9em">${swot.weaknesses.map(s => `<li>${s}</li>`).join('')}</ul>
                    </div>
                    <div style="background: rgba(66, 153, 225, 0.1); border: 1px solid rgba(66, 153, 225, 0.3); padding: 12px; border-radius: 8px;">
                        <strong style="color: #4299e1; display:block; margin-bottom:8px">OPPORTUNITIES</strong>
                        <ul style="margin:0; padding-left:20px; color:#ccc; font-size:0.9em">${swot.opportunities.map(s => `<li>${s}</li>`).join('')}</ul>
                    </div>
                    <div style="background: rgba(245, 101, 101, 0.1); border: 1px solid rgba(245, 101, 101, 0.3); padding: 12px; border-radius: 8px;">
                        <strong style="color: #f56565; display:block; margin-bottom:8px">THREATS</strong>
                        <ul style="margin:0; padding-left:20px; color:#ccc; font-size:0.9em">${swot.threats.map(s => `<li>${s}</li>`).join('')}</ul>
                    </div>
                `;
                document.getElementById('m-swot').innerHTML = swotHtml;

                document.getElementById('m-features').innerHTML = data.plan.mvp_features.map(f => 
                    `<div class="feature-item"><span class="check-icon">✓</span> <span>${f}</span></div>`
                ).join('');
                
                document.getElementById('m-hooks').innerHTML = data.plan.marketing_hooks.map(h => 
                    `<div class="hook-box">"${h}"</div>`
                ).join('');
                
                document.getElementById('m-rev').innerHTML = data.plan.revenue_projection.map(r => 
                    `<tr><td>${r.users} User</td><td class="money">${r.revenue_fmt}</td></tr>`
                ).join('');

                // Update share links
                const text = encodeURIComponent(`Cek ide bisnis gila ini: ${data.title} - ${data.description}`);
                const url = encodeURIComponent(window.location.href);
                document.getElementById('share-twitter').href = `https://twitter.com/intent/tweet?text=${text}&url=${url}`;
                document.getElementById('share-wa').href = `https://wa.me/?text=${text} ${url}`;

                // Export PDF Handler
                document.getElementById('btn-pdf').onclick = () => {
                    const element = document.getElementById('modal-content');
                    const opt = {
                        margin: 10,
                        filename: `business-plan-${data.id}.pdf`,
                        image: { type: 'jpeg', quality: 0.98 },
                        html2canvas: { scale: 2, useCORS: true },
                        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
                    };
                    html2pdf().set(opt).from(element).save();
                };

                // Export Landing Page Handler
                document.getElementById('btn-landing').onclick = async () => {
                    const btnLand = document.getElementById('btn-landing');
                    const oldText = btnLand.innerHTML;
                    btnLand.innerHTML = "Generating...";
                    
                    try {
                        const res = await fetch('/generate-landing', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify(data) // Send full idea data
                        });
                        const json = await res.json();
                        if (json.error) throw new Error(json.error);
                        
                        // Create blob and download
                        const blob = new Blob([json.html], {type: 'text/html'});
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `landing-page-${data.id}.html`;
                        document.body.appendChild(a);
                        a.click();
                        a.remove();
                    } catch(e) {
                        alert("Gagal generate landing page: " + e.message);
                    } finally {
                        btnLand.innerHTML = oldText;
                    }
                };

                const modal = document.getElementById('modal');
                modal.style.display = 'flex';
                // Trigger reflow
                modal.offsetHeight; 
                modal.classList.add('active');
            } catch (e) {
                console.error(e);
                alert("Gagal memuat data. Silakan coba lagi.");
            } finally {
                btn.innerHTML = originalText;
            }
        }
        
        function closeModal() {
            const modal = document.getElementById('modal');
            modal.classList.remove('active');
            setTimeout(() => {
                modal.style.display = 'none';
            }, 300);
        }

        function toggleChat() {
            const chat = document.getElementById('chat-window');
            if (chat.style.display === 'flex') {
                chat.style.display = 'none';
            } else {
                chat.style.display = 'flex';
            }
        }

        async function sendChat() {
            const input = document.getElementById('chat-input');
            const msg = input.value.trim();
            if (!msg) return;

            // Add user message
            const body = document.getElementById('chat-body');
            body.innerHTML += `<div class="msg msg-user">${msg}</div>`;
            input.value = '';
            body.scrollTop = body.scrollHeight;

            // Simulate thinking
            const thinkingId = 'thinking-' + Date.now();
            body.innerHTML += `<div id="${thinkingId}" class="msg msg-ai">...</div>`;
            
            try {
                const res = await fetch('/consult', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: msg})
                });
                const data = await res.json();
                
                document.getElementById(thinkingId).remove();
                body.innerHTML += `<div class="msg msg-ai">${data.answer}</div>`;
                body.scrollTop = body.scrollHeight;
            } catch (e) {
                document.getElementById(thinkingId).innerText = "Maaf, error koneksi.";
            }
        }

        // Tabs & Saved Ideas System
        function switchTab(tab) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(`tab-${tab}`).classList.add('active');
            
            if (tab === 'explore') {
                document.getElementById('explore-view').style.display = 'block';
                document.getElementById('saved-view').style.display = 'none';
            } else {
                document.getElementById('explore-view').style.display = 'none';
                document.getElementById('saved-view').style.display = 'grid';
                renderSaved();
            }
        }

        function getSavedIdeas() {
            try {
                return JSON.parse(localStorage.getItem('saved_ideas') || '[]');
            } catch (e) {
                return [];
            }
        }

        function handleSaveClick(btn) {
            const card = btn.closest('.idea-card');
            // dataset.idea is a string, need to parse it
            // Note: In template we used |tojson|safe, which creates a JSON string.
            // But HTML attribute might have issues if not handled carefully.
            // Let's rely on JSON.parse.
            try {
                const idea = JSON.parse(card.dataset.idea);
                const score = card.dataset.score;
                toggleSave(idea, score, btn);
            } catch (e) {
                console.error("Error parsing idea data", e);
            }
        }

        function toggleSave(idea, score, btn) {
            let saved = getSavedIdeas();
            const index = saved.findIndex(i => i.idea.id === idea.id);
            
            if (index >= 0) {
                // Remove
                saved.splice(index, 1);
                btn.classList.remove('saved');
            } else {
                // Add
                saved.push({ idea, score });
                btn.classList.add('saved');
                
                // Animation
                btn.style.transform = "scale(1.4)";
                setTimeout(() => btn.style.transform = "scale(1)", 200);
            }
            
            localStorage.setItem('saved_ideas', JSON.stringify(saved));
            updateSavedCount();
            
            // If in saved view, refresh
            if (document.getElementById('saved-view').style.display !== 'none') {
                renderSaved();
            }
        }

        function updateSavedCount() {
            const count = getSavedIdeas().length;
            document.getElementById('saved-count').innerText = count;
        }

        function renderSaved() {
            const container = document.getElementById('saved-view');
            const saved = getSavedIdeas();
            
            if (saved.length === 0) {
                container.innerHTML = `<div style="text-align:center; color:#8899ac; grid-column:1/-1; padding:40px; border: 1px dashed var(--glass-border); border-radius: 16px;">Belum ada ide yang disimpan.</div>`;
                return;
            }
            
            container.innerHTML = saved.map(item => {
                const i = item.idea;
                const s = item.score;
                const price = new Intl.NumberFormat('id-ID').format(i.price * 15000);
                const audience = new Intl.NumberFormat('en-US').format(i.audience);
                const scoreFmt = (parseFloat(s) * 10).toFixed(1);
                
                // Capitalize model
                const model = i.model.charAt(0).toUpperCase() + i.model.slice(1);
                
                return `
                <div class="idea-card" data-idea="${JSON.stringify(i).replace(/"/g, '&quot;')}" data-score="${s}">
                    <button class="btn-save saved" onclick="handleSaveClick(this)">🔖</button>
                    <div class="card-top">
                        <h3 class="idea-title">
                            ${i.title}
                            ${i.trend_score > 0.7 ? '<span class="trending">🔥 Trending</span>' : ''}
                        </h3>
                        <span class="score-badge">${scoreFmt}/10</span>
                    </div>
                    <p class="idea-desc">${i.description}</p>
                    <div class="card-stats">
                        <div class="stat-pill"><span class="stat-icon">📦</span> ${model}</div>
                        <div class="stat-pill"><span class="stat-icon">💰</span> Rp${price}</div>
                        <div class="stat-pill"><span class="stat-icon">👥</span> ~${audience} Target</div>
                    </div>
                    <button id="btn-${i.id}" class="btn-analyze" onclick="analyzeIdea(this)">
                        🔍 Bedah Bisnis & Potensi Cuan
                    </button>
                </div>`;
            }).join('');
        }

        // Initialize saved status on load
        document.addEventListener('DOMContentLoaded', () => {
            updateSavedCount();
            const savedIds = new Set(getSavedIdeas().map(s => s.idea.id));
            
            document.querySelectorAll('#explore-view .idea-card').forEach(card => {
                try {
                    const idea = JSON.parse(card.dataset.idea);
                    if (savedIds.has(idea.id)) {
                        card.querySelector('.btn-save').classList.add('saved');
                    }
                } catch(e) {}
            });
            
            // Chat enter key
            document.getElementById('chat-input').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendChat();
            });
        });
    </script>
</head>
<body>
    <div class="container">
        <header>
            <h1>AI GILA GENERATOR</h1>
            <p class="subtitle">Mesin penghasil ide bisnis micro-SaaS yang "tidak terpikirkan" manusia. Biarkan AI merancang jalan menuju kebebasan finansial Anda.</p>
        </header>
        
        <form action="/" method="post" class="action-area">
            <button type="submit" class="btn-generate">
                ✨ Generate Ide Baru
            </button>
        </form>

        <div class="tabs">
            <button class="tab-btn active" id="tab-explore" onclick="switchTab('explore')">🚀 Explore</button>
            <button class="tab-btn" id="tab-saved" onclick="switchTab('saved')">🔖 Saved (<span id="saved-count">0</span>)</button>
        </div>

        <div id="explore-view">
            {% if ideas %}
            <div class="ideas-grid">
                {% for idea, score in ideas %}
                <div class="idea-card" data-idea="{{ idea|tojson|forceescape }}" data-score="{{ score }}">
                    <button class="btn-save" onclick="handleSaveClick(this)">🔖</button>
                    <div class="card-top">
                        <h3 class="idea-title">
                            {{ idea.title }}
                            {% if idea.trend_score > 0.7 %}
                            <span class="trending">🔥 Trending</span>
                            {% endif %}
                        </h3>
                        <span class="score-badge">{{ "%.1f"|format(score * 10) }}/10</span>
                    </div>
                    
                    <p class="idea-desc">{{ idea.description }}</p>
                    
                    <div class="card-stats">
                        <div class="stat-pill">
                            <span class="stat-icon">📦</span> {{ idea.model|title }}
                        </div>
                        <div class="stat-pill">
                            <span class="stat-icon">💰</span> Rp{{ "{:,}".format((idea.price * 15000)|int) }}
                        </div>
                        <div class="stat-pill">
                            <span class="stat-icon">👥</span> ~{{ "{:,}".format(idea.audience) }} Target
                        </div>
                    </div>

                    <button id="btn-{{ idea.id }}" class="btn-analyze" onclick="analyzeIdea(this)">
                        🔍 Bedah Bisnis & Potensi Cuan
                    </button>
                </div>
                {% endfor %}
            </div>
            {% else %}
            <div style="text-align: center; color: #666; padding: 40px; border: 1px dashed var(--glass-border); border-radius: 16px;">
                <p>Belum ada ide yang digenerate. Klik tombol di atas!</p>
            </div>
            {% endif %}
        </div>

        <div id="saved-view" class="ideas-grid" style="display: none;"></div>
    </div>

    <!-- Chat Widget -->
    <div class="chat-widget" onclick="toggleChat()">
        <span class="chat-icon">💬</span>
    </div>

    <div id="chat-window" class="chat-window">
        <div class="chat-header">
            <span style="font-weight:bold; color:var(--accent-primary)">AI Consultant</span>
            <span style="cursor:pointer" onclick="toggleChat()">×</span>
        </div>
        <div id="chat-body" class="chat-body">
            <div class="msg msg-ai">Halo! Saya konsultan bisnis AI Anda. Ada yang bisa saya bantu tentang ide, validasi, atau teknis?</div>
        </div>
        <div class="chat-input-area">
            <input type="text" id="chat-input" class="chat-input" placeholder="Tanya sesuatu...">
            <button class="chat-send" onclick="sendChat()">➤</button>
        </div>
    </div>

    <!-- Modal -->
    <div id="modal" class="modal-overlay" onclick="if(event.target === this) closeModal()">
        <div class="modal-content" id="modal-content">
            <button class="close-btn" onclick="closeModal()">×</button>
            
            <div class="modal-header">
                <div style="display: flex; gap: 20px; align-items: center;">
                    <div id="m-logo"></div>
                    <div>
                        <h2 id="m-title" class="modal-title">Title</h2>
                        <p id="m-desc" style="color: #8899ac; margin:0">Description</p>
                    </div>
                </div>
            </div>

            <div class="section-header">🔍 Analisis SWOT</div>
            <div id="m-swot" style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;"></div>

            <div class="section-header">✨ Fitur MVP Wajib</div>
            <div id="m-features"></div>

            <div class="section-header">📢 Marketing Hooks</div>
            <div id="m-hooks"></div>

            <div class="section-header">💰 Proyeksi Pendapatan</div>
            <table>
                <thead><tr><th>Milestone Pengguna</th><th>Estimasi / Bulan</th></tr></thead>
                <tbody id="m-rev"></tbody>
            </table>

            <div class="section-header">⚔️ Strategi Eksekusi</div>
            <div style="background: rgba(255,255,255,0.03); padding: 16px; border-radius: 8px; line-height: 1.6; color: #ccc;">
                <p style="margin-bottom: 10px"><strong style="color: #fff">Go-to-Market:</strong> <span id="m-strategy"></span></p>
                <p style="margin: 0"><strong style="color: #fff">Celah Kompetitor:</strong> <span id="m-comp"></span></p>
            </div>

            <div style="margin-top: 24px; display: flex; gap: 12px; flex-wrap: wrap;">
                <a id="share-twitter" target="_blank" style="flex: 1; text-align: center; background: #1da1f2; color: white; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; cursor: pointer;">Share Twitter</a>
                <a id="share-wa" target="_blank" style="flex: 1; text-align: center; background: #25d366; color: white; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; cursor: pointer;">Share WA</a>
                <button id="btn-pdf" style="flex: 1; background: #ff4757; color: white; border: none; padding: 12px; border-radius: 8px; font-weight: bold; cursor: pointer;">Download PDF</button>
                <button id="btn-landing" style="flex: 1; background: #5a4fcf; color: white; border: none; padding: 12px; border-radius: 8px; font-weight: bold; cursor: pointer;">Export Web</button>
            </div>
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
        ideas_data = [(asdict(i), s) for i, s in ranked]
        
        # Cache for analysis
        global IDEA_CACHE
        IDEA_CACHE = {i.id: i for i, _ in ranked}
    
    return render_template_string(HTML_TEMPLATE, ideas=ideas_data)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    try:
        from ai_gila.engine import Idea
        # Reconstruct idea
        idea = Idea(
            id=data.get('id'),
            title=data.get('title'),
            description=data.get('description'),
            niche=data.get('niche'),
            model=data.get('model'),
            price=float(data.get('price')),
            audience=int(data.get('audience')),
            trend_score=float(data.get('trend_score', 0.5))
        )
        
        plan = eng.generate_business_plan(idea)
        
        # Return everything needed for frontend
        response = asdict(idea)
        response['plan'] = plan
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/consult', methods=['POST'])
def consult():
    data = request.get_json()
    q = data.get('question', '')
    answer = eng.consult(q)
    return jsonify({"answer": answer})

@app.route('/generate-landing', methods=['POST'])
def generate_landing():
    data = request.get_json()
    # Reconstruct Idea object from JSON data
    try:
        # We need to ensure we have all fields. If not, use defaults or fail.
        # The client sends what's in 'idea' object.
        # Idea class: id, title, description, niche, model, price, audience, trend_score
        from ai_gila.engine import Idea
        idea = Idea(
            id=data.get('id', 'unknown'),
            title=data.get('title', 'Untitled'),
            description=data.get('description', ''),
            niche=data.get('niche', 'General'),
            model=data.get('model', 'SaaS'),
            price=float(data.get('price', 10)),
            audience=int(data.get('audience', 1000)),
            trend_score=float(data.get('trend_score', 0.5))
        )
        html = eng.generate_landing_page_html(idea)
        return jsonify({"html": html})
    except Exception as e:
        return jsonify({"error": str(e)}), 400



# Vercel requires the app to be named 'app'
