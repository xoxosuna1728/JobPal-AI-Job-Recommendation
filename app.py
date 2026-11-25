"""JobPal web application. Run with: python app.py"""

from flask import Flask, jsonify, request

from agent import Agent
from search import JobIndex

app = Flask(__name__)
index = JobIndex()
sessions = {}

PAGE = r'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="theme-color" content="#f7f8fc">
  <title>JobPal — Your career copilot</title>
  <style>
    :root {
      --ink: #172033; --muted: #718096; --line: #e8ebf2;
      --purple: #6558d3; --purple-dark: #5144bf; --lavender: #f0efff;
      --surface: #fff; --bg: #f7f8fc; --green: #16845b;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    * { box-sizing: border-box; }
    body { margin: 0; background: var(--bg); color: var(--ink); }
    button, input { font: inherit; }
    .app { min-height: 100vh; display: grid; grid-template-columns: 250px minmax(0, 1fr); }
    .sidebar { background: #fff; border-right: 1px solid var(--line); padding: 27px 18px; display: flex; flex-direction: column; gap: 28px; }
    .brand { display: flex; align-items: center; gap: 11px; padding: 0 7px; }
    .brand-mark { width: 39px; height: 39px; display: grid; place-items: center; border-radius: 13px; color: #fff; font-weight: 800; background: linear-gradient(135deg,#8176ed,#5548c8); box-shadow: 0 7px 16px #6558d333; }
    .brand-name { font-size: 19px; font-weight: 750; letter-spacing: -.5px; }
    .brand-sub { color: var(--muted); font-size: 11px; margin-top: 2px; }
    .side-label { color: #9aa3b4; font-size: 10px; letter-spacing: 1.4px; font-weight: 800; padding: 0 9px; text-transform: uppercase; }
    .nav-item { width: 100%; border: 0; text-align: left; background: transparent; color: #566176; padding: 11px 12px; border-radius: 10px; display: flex; gap: 11px; align-items: center; font-size: 13px; }
    .nav-item.active { color: var(--purple-dark); background: var(--lavender); font-weight: 700; }
    .nav-icon { width: 20px; text-align: center; font-size: 16px; }
    .side-card { margin-top: auto; border: 1px solid #e9e6ff; background: linear-gradient(145deg,#f8f7ff,#fff); border-radius: 15px; padding: 15px; }
    .side-card strong { font-size: 13px; }
    .side-card p { color: var(--muted); font-size: 11px; line-height: 1.55; margin: 7px 0 0; }
    .main { min-width: 0; display: flex; flex-direction: column; min-height: 100vh; }
    .topbar { height: 72px; padding: 0 34px; border-bottom: 1px solid var(--line); background: #ffffffd9; display: flex; align-items: center; justify-content: space-between; }
    .top-title { font-weight: 700; font-size: 14px; }
    .top-caption { color: var(--muted); font-size: 11px; margin-top: 3px; }
    .status { color: var(--green); background: #eaf8f1; border: 1px solid #d6f0e2; border-radius: 99px; padding: 7px 11px; font-size: 11px; font-weight: 700; }
    .content { width: min(920px, 100%); margin: 0 auto; padding: 38px 28px 24px; flex: 1; display: flex; flex-direction: column; }
    .welcome { margin: 8px 0 25px; }
    .eyebrow { color: var(--purple); text-transform: uppercase; letter-spacing: 1.6px; font-size: 10px; font-weight: 800; }
    h1 { font-size: clamp(26px,4vw,36px); letter-spacing: -1.2px; margin: 9px 0 8px; line-height: 1.15; }
    .welcome p { color: var(--muted); font-size: 14px; margin: 0; line-height: 1.6; }
    .suggestions { display: grid; grid-template-columns: repeat(3,1fr); gap: 11px; margin: 19px 0 22px; }
    .suggestion { background: #fff; border: 1px solid var(--line); border-radius: 13px; padding: 13px 14px; color: #4d5870; cursor: pointer; text-align: left; font-size: 12px; line-height: 1.45; transition: .18s ease; }
    .suggestion:hover { border-color: #bcb6f4; transform: translateY(-2px); box-shadow: 0 8px 20px #29205d0b; }
    .suggestion span { display: block; color: var(--purple); font-size: 17px; margin-bottom: 7px; }
    .chat-panel { flex: 1; min-height: 310px; background: #fff; border: 1px solid var(--line); border-radius: 18px; box-shadow: 0 10px 35px #28304a08; padding: 20px; display: flex; flex-direction: column; gap: 17px; }
    .chat-empty { margin: auto; text-align: center; max-width: 310px; padding: 25px 10px; }
    .empty-icon { width: 48px; height: 48px; display: grid; place-items: center; margin: 0 auto 12px; border-radius: 16px; background: var(--lavender); color: var(--purple); font-size: 22px; }
    .chat-empty strong { font-size: 14px; }
    .chat-empty p { font-size: 12px; line-height: 1.6; color: var(--muted); }
    .message { display: flex; gap: 10px; align-items: flex-start; max-width: 100%; }
    .message.user { flex-direction: row-reverse; }
    .avatar { flex: 0 0 30px; width: 30px; height: 30px; border-radius: 10px; display: grid; place-items: center; font-size: 11px; font-weight: 800; background: var(--lavender); color: var(--purple); }
    .user .avatar { background: #eaf0f8; color: #53627a; }
    .bubble { max-width: min(720px, calc(100% - 42px)); border-radius: 4px 14px 14px 14px; padding: 12px 15px; background: #f7f8fc; color: #354057; font-size: 13px; line-height: 1.65; overflow-wrap: anywhere; }
    .user .bubble { background: var(--purple); color: #fff; border-radius: 14px 4px 14px 14px; }
    .bubble p { margin: 0 0 8px; white-space: pre-wrap; }
    .bubble p:last-child { margin-bottom: 0; }
    .bubble ul { margin: 5px 0 0; padding-left: 19px; }
    .bubble li { margin: 5px 0; }
    .typing { color: var(--muted); font-size: 12px; padding-left: 40px; }
    .composer-wrap { margin-top: 15px; }
    .composer { display: flex; gap: 9px; padding: 8px; background: #fff; border: 1px solid #dfe3ed; border-radius: 14px; box-shadow: 0 7px 22px #28304a0a; }
    .composer:focus-within { border-color: #a9a1f0; box-shadow: 0 0 0 3px #6558d318; }
    .composer input { flex: 1; min-width: 0; border: 0; outline: 0; padding: 8px 10px; color: var(--ink); font-size: 13px; background: transparent; }
    .composer input::placeholder { color: #a0a8b7; }
    .send { border: 0; border-radius: 10px; padding: 0 19px; background: var(--purple); color: #fff; font-size: 12px; font-weight: 700; cursor: pointer; transition: .15s; }
    .send:hover { background: var(--purple-dark); }
    .send:disabled { opacity: .55; cursor: wait; }
    .fineprint { text-align: center; color: #a0a8b7; font-size: 10px; margin: 10px 0 0; }
    @media (max-width: 760px) {
      .app { grid-template-columns: 1fr; }
      .sidebar { display: none; }
      .topbar { height: 62px; padding: 0 18px; }
      .content { padding: 25px 15px 18px; }
      .suggestions { grid-template-columns: 1fr; }
      .suggestion { display: flex; align-items: center; gap: 10px; }
      .suggestion span { margin: 0; }
      .chat-panel { padding: 14px; }
      .status { font-size: 10px; }
    }
  </style>
</head>
<body>
<div class="app">
  <aside class="sidebar">
    <div class="brand"><div class="brand-mark">J</div><div><div class="brand-name">JobPal</div><div class="brand-sub">Your career copilot</div></div></div>
    <div>
      <div class="side-label">Workspace</div>
      <div style="height:9px"></div>
      <div class="nav-item active"><span class="nav-icon">⌕</span> Find opportunities</div>
      <div class="nav-item"><span class="nav-icon">♡</span> Saved jobs <span style="margin-left:auto;color:#a0a8b7;font-size:10px">Ask JobPal</span></div>
    </div>
    <div>
      <div class="side-label">Explore</div>
      <div style="height:9px"></div>
      <button class="nav-item" onclick="usePrompt('Find remote software engineering internships.')"><span class="nav-icon">⌘</span> Remote internships</button>
      <button class="nav-item" onclick="usePrompt('Find entry-level Python developer jobs.')"><span class="nav-icon">⌁</span> Python opportunities</button>
    </div>
    <div class="side-card"><strong>✨ A smarter job search</strong><p>Describe the role you want. JobPal searches your job database and helps you shortlist opportunities.</p></div>
  </aside>
  <main class="main">
    <header class="topbar"><div><div class="top-title">Job discovery</div><div class="top-caption">Search, explore and save opportunities</div></div><div class="status">● AI assistant ready</div></header>
    <section class="content">
      <div class="welcome">
        <div class="eyebrow">Your next opportunity starts here</div>
        <h1>Find a role that moves<br>you forward.</h1>
        <p>Tell JobPal what you're looking for. I'll help you discover relevant opportunities and keep track of the ones you like.</p>
      </div>
      <div class="suggestions" id="suggestions">
        <button class="suggestion" onclick="usePrompt('Find AI internships in Coimbatore.')"><span>✦</span>AI internships in Coimbatore</button>
        <button class="suggestion" onclick="usePrompt('Show me remote Python developer internships.')"><span>⌁</span>Remote Python internships</button>
        <button class="suggestion" onclick="usePrompt('Find entry-level software developer jobs.')"><span>↗</span>Entry-level software roles</button>
      </div>
      <div class="chat-panel" id="log" aria-live="polite">
        <div class="chat-empty" id="empty"><div class="empty-icon">✦</div><strong>What kind of opportunity are you looking for?</strong><p>Try a job title, skill, location or work preference. You can also ask for details or save a job.</p></div>
      </div>
      <div class="composer-wrap">
        <form class="composer" id="chat-form">
          <input id="message" autocomplete="off" placeholder="Ask about jobs, skills, locations..." aria-label="Your message">
          <button class="send" id="send" type="submit">Send&nbsp; ↗</button>
        </form>
        <div class="fineprint">JobPal can make mistakes. Check job details before applying.</div>
      </div>
    </section>
  </main>
</div>
<script>
  const sid = (window.crypto && crypto.randomUUID) ? crypto.randomUUID() : Math.random().toString(36).slice(2);
  const form = document.getElementById('chat-form');
  const input = document.getElementById('message');
  const log = document.getElementById('log');
  const send = document.getElementById('send');
  const suggestions = document.getElementById('suggestions');
  let busy = false;

  function addMessage(role, text) {
    document.getElementById('empty')?.remove();
    suggestions.style.display = 'none';
    const row = document.createElement('div');
    row.className = 'message ' + (role === 'user' ? 'user' : 'assistant');
    const avatar = document.createElement('div'); avatar.className = 'avatar'; avatar.textContent = role === 'user' ? 'You' : 'J';
    const bubble = document.createElement('div'); bubble.className = 'bubble';
    // Render text safely; format simple assistant bullet lists without injecting HTML.
    const lines = String(text).split('\n');
    let list = null;
    for (const raw of lines) {
      const line = raw.trim();
      if (!line) { list = null; continue; }
      if (role !== 'user' && (/^(\*|-)\s+/.test(line))) {
        if (!list) { list = document.createElement('ul'); bubble.appendChild(list); }
        const li = document.createElement('li'); li.textContent = line.replace(/^(\*|-)\s+/, '').replace(/\*\*/g, ''); list.appendChild(li);
      } else {
        list = null;
        const p = document.createElement('p'); p.textContent = line.replace(/\*\*/g, ''); bubble.appendChild(p);
      }
    }
    row.append(avatar, bubble); log.appendChild(row); log.scrollTop = log.scrollHeight;
  }

  function usePrompt(text) { input.value = text; input.focus(); form.requestSubmit(); }
  window.usePrompt = usePrompt;

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const text = input.value.trim();
    if (!text || busy) return;
    busy = true; send.disabled = true; send.textContent = 'Sending…';
    input.value = '';
    addMessage('user', text);
    const typing = document.createElement('div'); typing.className = 'typing'; typing.textContent = 'JobPal is thinking…'; log.appendChild(typing);
    try {
      const response = await fetch('/chat', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({session_id: sid, message: text})
      });
      const data = await response.json();
      typing.remove();
      if (!response.ok) throw new Error(data.error || 'Something went wrong. Please try again.');
      addMessage('assistant', data.reply || 'I could not generate a reply. Please try again.');
    } catch (error) {
      typing.remove(); addMessage('assistant', 'Sorry, I could not complete that request. ' + error.message);
    } finally {
      busy = false; send.disabled = false; send.innerHTML = 'Send&nbsp; ↗'; input.focus();
    }
  });
</script>
</body>
</html>'''


@app.get("/")
def home():
    return PAGE


@app.post("/chat")
def chat():
    data = request.get_json(force=True, silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify(error="message is required"), 400

    sid = (data.get("session_id") or "web").strip() or "web"
    if sid not in sessions:
        sessions[sid] = Agent(index, sid)

    try:
        return jsonify(reply=sessions[sid].chat(message))
    except Exception:
        app.logger.exception("JobPal chat request failed")
        return jsonify(error="JobPal couldn't process that message. Check the terminal for details."), 500


if __name__ == "__main__":
    app.run(debug=True)
