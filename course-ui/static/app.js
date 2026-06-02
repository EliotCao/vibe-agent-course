/* ===== Vibe Agent Course UI - app.js ===== */
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

const state = {
  courses: [],
  current: { courseId: null, kind: null, path: null },
};

// marked + highlight（兜底：每次调用时即时检查全局对象，
// 避免脚本加载顺序异常时仍引用裸 `hljs` / `marked` 触发 ReferenceError）
const hasHljs   = () => typeof window !== 'undefined' && typeof window.hljs   !== 'undefined';
const hasMarked = () => typeof window !== 'undefined' && typeof window.marked !== 'undefined';

function hl(code, lang) {
  if (!hasHljs()) return escapeHtml(code);
  try {
    if (lang && window.hljs.getLanguage(lang)) {
      return window.hljs.highlight(code, { language: lang }).value;
    }
    return window.hljs.highlightAuto(code).value;
  } catch {
    return escapeHtml(code);
  }
}

function renderMarkdown(text) {
  if (!hasMarked()) {
    return `<pre style="white-space:pre-wrap;">${escapeHtml(text || '')}</pre>`;
  }
  window.marked.setOptions({ gfm: true, breaks: false, highlight: hl });
  return window.marked.parse(text || '');
}

function highlightAll(root) {
  if (!hasHljs()) return;
  $$('pre code', root).forEach((b) => {
    try { window.hljs.highlightElement(b); } catch {}
  });
}

function highlightOne(el) {
  if (!hasHljs() || !el) return;
  try { window.hljs.highlightElement(el); } catch {}
}

// ---------------- 启动 ----------------
init().catch((err) => {
  console.error(err);
  $('#content').innerHTML =
    `<div class="welcome"><h1>启动失败</h1><pre>${escapeHtml(String(err))}</pre></div>`;
});

async function init() {
  await checkBackend();
  const r = await fetch('/api/courses').then((r) => r.json());
  state.courses = r.courses;
  renderNav();

  // CTA：开始学习 → 进入第一节课
  const cta = $('#cta-start');
  if (cta) {
    cta.addEventListener('click', enterFirstLesson);
  }

  // 不再自动跳转，保留 hero 欢迎页
}

function enterFirstLesson() {
  if (!state.courses.length) return;
  const first = state.courses[0];
  const piece = first.lectures[0] || first.demos[0];
  if (!piece) return;
  const kind = first.lectures[0] ? 'lecture' : 'demo';
  // 展开第一节
  const navEl = $('.nav-course');
  if (navEl) navEl.classList.add('open');
  openPiece(first.id, kind, piece.path);
}

// 后端在线检测：状态变更
async function checkBackend() {
  try {
    const t = await fetch('/health').then((r) => r.text());
    $('#backend-status').textContent = t === 'ok' ? '在线' : t;
    $('#status-dot').classList.toggle('bad', t !== 'ok');
  } catch {
    $('#backend-status').textContent = '离线';
    $('#status-dot').classList.add('bad');
  }
}

// ---------------- 侧边栏导航 ----------------
function renderNav() {
  const nav = $('#nav');
  nav.innerHTML = '';
  state.courses.forEach((c, idx) => {
    const courseEl = document.createElement('div');
    courseEl.className = 'nav-course';
    courseEl.dataset.courseId = c.id;

    const num = c.id.slice(0, 2);
    const head = document.createElement('div');
    head.className = 'nav-course-header';
    head.innerHTML = `
      <div class="nav-course-index">${num}</div>
      <div class="nav-course-text">
        <div class="nav-course-title">${escapeHtml(c.title)}</div>
        <div class="nav-course-sub">${escapeHtml(c.subtitle)}</div>
      </div>
      <div class="nav-course-caret">›</div>
    `;
    head.addEventListener('click', () => {
      courseEl.classList.toggle('open');
    });

    const children = document.createElement('div');
    children.className = 'nav-children';

    if (c.lectures.length) {
      children.appendChild(navSectionLabel('讲义'));
      c.lectures.forEach((l) => {
        children.appendChild(navItem('md', l.title, () => openPiece(c.id, 'lecture', l.path)));
      });
    }
    if (c.demos.length) {
      children.appendChild(navSectionLabel('代码示例 · 可运行'));
      c.demos.forEach((d) => {
        children.appendChild(navItem('py', d.title, () => openPiece(c.id, 'demo', d.path)));
      });
    }
    if (c.readme) {
      children.appendChild(navSectionLabel('概览'));
      children.appendChild(
        navItem('md', '本节 README', () => openPiece(c.id, 'lecture', c.readme))
      );
    }
    if (c.lab_readme) {
      children.appendChild(
        navItem('md', 'Lab 说明', () => openPiece(c.id, 'lecture', c.lab_readme))
      );
    }

    courseEl.appendChild(head);
    courseEl.appendChild(children);
    if (idx === 0) courseEl.classList.add('open');
    nav.appendChild(courseEl);
  });
}

function navSectionLabel(text) {
  const el = document.createElement('div');
  el.className = 'nav-section-label';
  el.textContent = text;
  return el;
}

function navItem(kind, title, onClick) {
  const el = document.createElement('div');
  el.className = 'nav-item';
  el.dataset.title = title;
  el.innerHTML = `
    <span class="badge ${kind}">${kind === 'py' ? 'PY' : 'MD'}</span>
    <span class="nav-item-text">${escapeHtml(title)}</span>
  `;
  el.addEventListener('click', () => {
    $$('.nav-item').forEach((x) => x.classList.remove('active'));
    el.classList.add('active');
    onClick();
  });
  return el;
}

// ---------------- 打开内容 ----------------
async function openPiece(courseId, kind, path) {
  state.current = { courseId, kind, path };
  const course = state.courses.find((c) => c.id === courseId);
  if (!course) return;

  // 面包屑
  $('#crumb-course').textContent = `${course.id.slice(0, 2)} · ${course.title}`;
  $('#crumb-piece').textContent = path.split('/').pop();

  // 课程头
  const num = course.id.slice(0, 2);
  let header = `
    <div class="course-head">
      <div class="num">${num}</div>
      <div>
        <div class="title">${escapeHtml(course.title)}</div>
        <div class="subtitle">${escapeHtml(course.subtitle)}</div>
      </div>
    </div>
  `;

  // Tabs：讲义 / 代码示例
  const tabsHtml = `
    <div class="tabs">
      <div class="tab ${kind === 'lecture' ? 'active' : ''}" data-tab="lecture">
        📚 讲义 <span class="pill">${course.lectures.length}</span>
      </div>
      <div class="tab ${kind === 'demo' ? 'active' : ''}" data-tab="demo">
        🐍 代码示例 <span class="pill">${course.demos.length}</span>
      </div>
    </div>
  `;

  $('#content').innerHTML = header + tabsHtml + '<div id="tab-body"></div>';

  $$('.tab').forEach((t) =>
    t.addEventListener('click', () => {
      const newKind = t.dataset.tab;
      if (newKind === kind) return;
      const piece =
        newKind === 'lecture'
          ? course.lectures[0]
          : course.demos[0];
      if (piece) openPiece(courseId, newKind, piece.path);
    })
  );

  if (kind === 'lecture') {
    await renderLecture(path);
  } else {
    await renderDemos(course);
  }
}

// ---------------- 讲义渲染 ----------------
async function renderLecture(path) {
  const body = $('#tab-body');
  body.innerHTML = '<div class="markdown">加载中…</div>';
  try {
    const data = await fetch('/api/file?path=' + encodeURIComponent(path)).then((r) => r.json());
    const html = renderMarkdown(data.content || '');
    body.innerHTML = `<div class="markdown">${html}</div>`;
    // 修复相对图片路径
    $$('.markdown img').forEach((img) => {
      const src = img.getAttribute('src');
      if (src && !/^https?:\/\//.test(src) && !src.startsWith('/')) {
        const baseDir = path.split('/').slice(0, -1).join('/');
        img.src = '/api/asset?path=' + encodeURIComponent(`${baseDir}/${src}`);
      }
    });
    // 高亮代码块
    highlightAll($('.markdown', body));
  } catch (e) {
    body.innerHTML = `<div class="markdown">加载失败：${escapeHtml(String(e))}</div>`;
  }
}

// ---------------- Demo 列表（手风琴：单选展开） ----------------
async function renderDemos(course) {
  const body = $('#tab-body');
  if (!course.demos.length) {
    body.innerHTML = '<div class="markdown">本节没有可运行的 Python 示例。</div>';
    return;
  }
  const wrap = document.createElement('div');
  wrap.className = 'demos';
  body.innerHTML = '';
  body.appendChild(wrap);

  course.demos.forEach((demo, idx) => {
    const card = buildDemoCard(demo, idx + 1, wrap);
    wrap.appendChild(card);
    // 默认展开第一个 demo，便于一进来就看到完整源码
    if (idx === 0) toggleCard(card, wrap, true);
  });
}

/** 让目标 card 展开/收起，handles 单选互斥 */
function toggleCard(card, scope, forceOpen) {
  const willOpen = forceOpen ?? !card.classList.contains('open');
  if (willOpen) {
    // 关闭其他卡片，停掉它们的运行
    $$('.demo-card.open', scope).forEach((other) => {
      if (other !== card) {
        other.classList.remove('open');
        other.dispatchEvent(new CustomEvent('demo:closed'));
      }
    });
    card.classList.add('open');
    card.dispatchEvent(new CustomEvent('demo:opened'));
  } else {
    card.classList.remove('open');
    card.dispatchEvent(new CustomEvent('demo:closed'));
  }
}

function buildDemoCard(demo, indexNum, scope) {
  // 从文件名抓出 demo_XX 的数字
  const m = demo.filename.match(/demo[_-]?(\d+)/i);
  const numLabel = m ? m[1].padStart(2, '0') : String(indexNum).padStart(2, '0');

  const card = document.createElement('div');
  card.className = 'demo-card';
  card.innerHTML = `
    <div class="demo-head">
      <div class="index-chip">${numLabel}</div>
      <div class="live-pulse" title="运行状态"></div>
      <div class="demo-title">
        <div class="name">${escapeHtml(demo.title)}</div>
        <div class="file">${escapeHtml(demo.path)}</div>
      </div>
      <div class="demo-actions">
        <button class="btn primary" data-act="run" title="运行 (Cmd/Ctrl+Enter)">▶ <span class="btn-label">运行</span></button>
        <button class="btn danger" data-act="stop" style="display:none;" title="停止">■ <span class="btn-label">停止</span></button>
      </div>
      <div class="caret">›</div>
    </div>
    <div class="demo-body">
      <div class="vscode-banner">
        <div class="vsc-icon">VS</div>
        <div class="vsc-text">
          <b>想完整阅读这份代码？</b>
          <small>切换到 VSCode 网页编辑器，享受跳转定义/全文搜索/Git diff</small>
        </div>
        <a class="vsc-cta" data-act="open-vscode">在 VSCode 中打开</a>
      </div>
      <div class="demo-source">
        <div class="src-head">
          <span class="pyicon"></span>
          <span class="mono">${escapeHtml(demo.path)}</span>
          <span class="meta-tag">SAVED</span>
          <div class="src-actions">
            <span class="hint">点击 ✎ 编辑代码</span>
            <button class="iconbtn" data-act="edit"  title="进入编辑模式">✎ 编辑</button>
            <button class="iconbtn primary" data-act="save"   title="保存修改 (Cmd/Ctrl+S)" style="display:none;">⌘S 保存</button>
            <button class="iconbtn"          data-act="cancel" title="取消编辑" style="display:none;">取消</button>
            <button class="iconbtn"          data-act="reset"  title="重置到磁盘内容" style="display:none;">↺ 重置</button>
          </div>
        </div>
        <div class="editor-wrap">
          <pre><code class="language-python">加载中…</code></pre>
          <textarea class="editor mono" spellcheck="false"></textarea>
        </div>
      </div>
      <div class="terminal">
        <div class="terminal-head">
          <div class="lights"><span class="r"></span><span class="y"></span><span class="g"></span></div>
          <div class="label">terminal · ${escapeHtml(demo.filename)}</div>
          <div class="status">就绪</div>
        </div>
        <div class="terminal-output"></div>
        <div class="terminal-input disabled">
          <input type="text" placeholder="向 demo 发送一行输入（运行后可用，回车提交）" />
          <button>发送</button>
        </div>
      </div>
    </div>
  `;

  const head      = $('.demo-head', card);
  const btnRun    = $('[data-act=run]', card);
  const btnStop   = $('[data-act=stop]', card);
  const srcWrap   = $('.demo-source', card);
  const srcHead   = $('.demo-source .src-head', card);
  const srcCode   = $('.demo-source code', card);
  const editor    = $('.demo-source .editor', card);
  const btnEdit   = $('[data-act=edit]',   card);
  const btnSave   = $('[data-act=save]',   card);
  const btnCancel = $('[data-act=cancel]', card);
  const btnReset  = $('[data-act=reset]',  card);
  const btnVscode = $('[data-act=open-vscode]', card);
  const out      = $('.terminal-output', card);
  const status   = $('.terminal-head .status', card);
  const inputBar = $('.terminal-input', card);
  const inputEl  = $('input', inputBar);
  const sendBtn  = $('button', inputBar);

  let runId = null;
  let evtSource = null;
  let srcLoaded = false;
  let lastSaved = '';   // 上次磁盘内容，用于 dirty 标记 / 重置

  // ---- 头部点击 = 手风琴展开/收起 ----
  head.addEventListener('click', (e) => {
    if (e.target.closest('.btn')) return;
    toggleCard(card, scope);
  });

  // 展开时按需加载源码
  card.addEventListener('demo:opened', async () => {
    if (srcLoaded) return;
    try {
      const data = await fetch('/api/file?path=' + encodeURIComponent(demo.path)).then((r) =>
        r.json()
      );
      const text = data.content || '';
      srcCode.textContent = text;
      editor.value = text;
      lastSaved = text;
      highlightOne(srcCode);
      srcLoaded = true;
    } catch (err) {
      srcCode.textContent = '加载失败：' + err;
    }
  });

  // ---- 进入编辑模式 ----
  btnEdit.addEventListener('click', (e) => {
    e.stopPropagation();
    srcWrap.classList.add('editing');
    btnEdit.style.display = 'none';
    btnSave.style.display   = 'inline-flex';
    btnCancel.style.display = 'inline-flex';
    btnReset.style.display  = 'inline-flex';
    $('.hint', srcHead).style.display = 'none';
    // 自适应高度
    const rows = (editor.value.match(/\n/g) || []).length + 2;
    editor.style.height = Math.min(Math.max(rows * 22, 240), 720) + 'px';
    editor.focus();
  });

  // ---- 取消 ----
  btnCancel.addEventListener('click', (e) => {
    e.stopPropagation();
    editor.value = lastSaved;
    exitEditMode();
  });

  // ---- 重置 ----
  btnReset.addEventListener('click', (e) => {
    e.stopPropagation();
    editor.value = lastSaved;
    markDirty(false);
    toast('已重置为最近一次磁盘内容', 'info');
  });

  // ---- 保存 ----
  async function save() {
    const content = editor.value;
    try {
      const r = await fetch('/api/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: demo.path, content }),
      });
      const data = await r.json();
      if (!r.ok || !data.ok) {
        toast('保存失败：' + (data.error || r.statusText), 'error');
        return false;
      }
      lastSaved = content;
      srcCode.textContent = content;
      highlightOne(srcCode);
      markDirty(false);
      toast('已保存', 'success');
      return true;
    } catch (e) {
      toast('保存失败：' + e, 'error');
      return false;
    }
  }
  btnSave.addEventListener('click', async (e) => {
    e.stopPropagation();
    if (await save()) exitEditMode();
  });

  // 编辑器内 Cmd/Ctrl+S 保存
  editor.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 's') {
      e.preventDefault();
      save();
    } else if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault();
      save().then((ok) => { if (ok) { exitEditMode(); btnRun.click(); } });
    } else if (e.key === 'Escape') {
      btnCancel.click();
    }
  });
  editor.addEventListener('input', () => {
    markDirty(editor.value !== lastSaved);
  });

  function markDirty(dirty) {
    srcHead.classList.toggle('dirty', dirty);
    const tag = $('.meta-tag', srcHead);
    if (tag) tag.textContent = dirty ? 'UNSAVED' : 'SAVED';
  }
  function exitEditMode() {
    srcWrap.classList.remove('editing');
    btnEdit.style.display = 'inline-flex';
    btnSave.style.display = 'none';
    btnCancel.style.display = 'none';
    btnReset.style.display = 'none';
    const hint = $('.hint', srcHead);
    if (hint) hint.style.display = '';
    markDirty(false);
  }

  // ---- VSCode 引导 ----
  btnVscode.addEventListener('click', (e) => {
    e.stopPropagation();
    e.preventDefault();
    openInVscode();
  });

  // 收起时如果还在运行，发停止并清理
  card.addEventListener('demo:closed', () => {
    if (runId) {
      try { fetch('/api/stop/' + runId, { method: 'POST' }); } catch {}
    }
    if (evtSource) {
      evtSource.close();
      evtSource = null;
    }
  });

  // ---- 运行 ----
  btnRun.addEventListener('click', async (e) => {
    e.stopPropagation();
    // 没展开就先展开
    if (!card.classList.contains('open')) toggleCard(card, scope, true);

    // 如果处在编辑模式且有 dirty，先尝试保存
    if (srcWrap.classList.contains('editing') && srcHead.classList.contains('dirty')) {
      const ok = await save();
      if (!ok) return;
      exitEditMode();
    }

    out.innerHTML = '';
    appendMeta(out, `▶ 启动 ${demo.path} ...`);
    status.textContent = '运行中';
    status.className = 'status running';
    btnRun.disabled = true;
    btnStop.style.display = 'inline-flex';
    inputBar.classList.remove('disabled');
    card.classList.add('running');
    card.classList.remove('error');
    progress(true);
    inputEl.focus();

    evtSource = new EventSource('/api/run?path=' + encodeURIComponent(demo.path));
    evtSource.addEventListener('start', (ev) => {
      const d = JSON.parse(ev.data);
      runId = d.run_id;
      appendMeta(out, `[runner] python=${d.python}  pid=${d.run_id}`);
    });
    evtSource.addEventListener('stdout', (ev) => append(out, JSON.parse(ev.data), 'stdout'));
    evtSource.addEventListener('stderr', (ev) => append(out, JSON.parse(ev.data), 'stderr'));
    evtSource.addEventListener('exit', (ev) => {
      const d = JSON.parse(ev.data);
      const ok = d.code === 0;
      append(out, `\n[exit code ${d.code}]`, ok ? 'exit-ok' : 'exit-fail');
      status.textContent = ok ? '已完成' : `异常退出 (${d.code})`;
      status.className = 'status ' + (ok ? 'ok' : 'fail');
      card.classList.remove('running');
      card.classList.toggle('error', !ok);
      progress(false);
      cleanup();
    });
    evtSource.onerror = () => {
      append(out, '\n[连接已断开]', 'exit-fail');
      status.textContent = '已断开';
      status.className = 'status fail';
      card.classList.remove('running');
      card.classList.add('error');
      progress(false);
      cleanup();
    };
  });

  btnStop.addEventListener('click', async (e) => {
    e.stopPropagation();
    if (!runId) return;
    await fetch('/api/stop/' + runId, { method: 'POST' });
    appendMeta(out, '\n[已发送停止信号]');
  });

  function send() {
    const text = inputEl.value;
    if (!runId) return;
    fetch('/api/stdin/' + runId, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    append(out, `> ${text}\n`, 'meta');
    inputEl.value = '';
  }
  sendBtn.addEventListener('click', (e) => { e.stopPropagation(); send(); });
  inputEl.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      send();
    }
  });

  function cleanup() {
    if (evtSource) {
      evtSource.close();
      evtSource = null;
    }
    runId = null;
    btnRun.disabled = false;
    btnStop.style.display = 'none';
    inputBar.classList.add('disabled');
  }

  return card;
}

// ---------------- 工具 ----------------
function append(el, text, cls = '') {
  const span = document.createElement('span');
  if (cls) span.className = cls;
  span.textContent = text;
  el.appendChild(span);
  el.scrollTop = el.scrollHeight;
}
function appendMeta(el, text) {
  append(el, text + '\n', 'meta');
}
function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]
  );
}

// ---------------- Toast / 进度条 ----------------
function toast(msg, type = 'info', dur = 2200) {
  const host = $('#toast-host');
  if (!host) return;
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = msg;
  host.appendChild(el);
  setTimeout(() => {
    el.classList.add('fade-out');
    setTimeout(() => el.remove(), 320);
  }, dur);
}
function progress(active) {
  const el = $('#progress-line');
  if (el) el.classList.toggle('active', !!active);
}

// ---------------- 切换到 VSCode 模式 ----------------
function openInVscode() {
  // 在 CNB only-preview 模式下，运行时通常会注入这些环境变量；
  // 浏览器侧无法直接读，但 CNB 工作区右上角有"启动远程开发"按钮可切。
  // 我们尝试两种方式：
  // 1) 如果 URL 包含 cnb only-preview 的 token，可以直接跳到 vscode 子路径
  // 2) 否则提示用户手动点击"启动远程开发"
  const host = location.host;
  const isCNB = /cnb\.cool|cnb-rto|cnb\./.test(host);
  if (isCNB) {
    // CNB 会把 ?vscode=1 视为请求切换；不可识别则忽略，所以不会出错
    const target = new URL(location.href);
    target.searchParams.set('vscode', '1');
    window.open(target.toString(), '_top');
    toast('正在请求切换到 VSCode 远程开发…', 'info');
  } else {
    toast('请在 CNB 工作区右上角点击「启动远程开发」', 'info', 3500);
  }
}

// ---------------- 启动钩子 ----------------
document.addEventListener('DOMContentLoaded', () => {
  const heroVsc = document.getElementById('hero-vscode');
  if (heroVsc) heroVsc.addEventListener('click', openInVscode);
});
