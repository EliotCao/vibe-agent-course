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
    <div class="tabs-row">
      <div class="tabs">
        <div class="tab ${kind === 'lecture' ? 'active' : ''}" data-tab="lecture">
          📚 讲义 <span class="pill">${course.lectures.length}</span>
        </div>
        <div class="tab ${kind === 'demo' ? 'active' : ''}" data-tab="demo">
          🐍 代码示例 <span class="pill">${course.demos.length}</span>
        </div>
      </div>
    </div>
  `;

  $('#content').innerHTML = header + tabsHtml + '<div id="tab-body"></div>';
  $('#content').dataset.kind = kind;

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

// ---------------- 讲义渲染（三栏：TOC + Markdown + 笔记） ----------------
async function renderLecture(path) {
  const body = $('#tab-body');
  body.innerHTML = '<div class="markdown">加载中…</div>';
  try {
    const data = await fetch('/api/file?path=' + encodeURIComponent(path)).then((r) => r.json());
    const html = renderMarkdown(data.content || '');

    // 三栏布局
    body.innerHTML = `
      <div class="lecture-layout">
        <aside class="toc" id="toc">
          <div class="toc-head">
            <span class="toc-title">本节大纲</span>
            <span class="toc-count" id="toc-count">0</span>
          </div>
          <div class="toc-list" id="toc-list"></div>
        </aside>

        <article class="markdown" id="lecture-md">${html}</article>

        <aside class="notes" id="notes">
          <div class="notes-head">
            <div class="notes-title">
              <span>我的笔记</span>
              <span class="notes-key mono">${escapeHtml(path.split('/').pop())}</span>
            </div>
            <div class="notes-actions">
              <button class="iconbtn primary" data-act="notes-sync"  title="把所有笔记写到仓库 notes/ 并 git commit">☁ 同步到仓库</button>
              <button class="iconbtn" data-act="notes-export" title="导出全部笔记为 Markdown">↓ 导出</button>
              <button class="iconbtn" data-act="notes-clear"  title="清空当前页笔记">✕</button>
            </div>
          </div>
          <textarea
            class="notes-area mono"
            id="notes-area"
            spellcheck="false"
            placeholder="在这里随手记录想法 / 课堂要点 / 待办…&#10;&#10;支持 Markdown，自动按页面保存到浏览器，关闭也不会丢。"
          ></textarea>
          <div class="notes-foot">
            <span class="notes-status" id="notes-status">已保存</span>
            <span class="notes-meta mono" id="notes-meta">0 字</span>
          </div>
        </aside>
      </div>
    `;

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

    // 构建大纲 / 滚动联动
    buildTOC($('#lecture-md'), $('#toc-list'), $('#toc-count'));
    // 启用笔记
    setupNotes(path);
  } catch (e) {
    body.innerHTML = `<div class="markdown">加载失败：${escapeHtml(String(e))}</div>`;
  }
}

// 自动生成本节大纲，并接入滚动联动
function buildTOC(mdRoot, listEl, countEl) {
  if (!mdRoot || !listEl) return;
  const heads = $$('h1, h2, h3', mdRoot);
  // 给每个标题加 id
  const used = new Set();
  const items = heads.map((h, i) => {
    let id = h.id;
    if (!id) {
      id = (h.textContent || `sec-${i}`)
        .toLowerCase()
        .replace(/[^a-z0-9\u4e00-\u9fa5\s-]/g, '')
        .trim()
        .replace(/\s+/g, '-')
        .slice(0, 60) || `sec-${i}`;
      while (used.has(id)) id += '-x';
      h.id = id;
    }
    used.add(id);
    return { id, level: parseInt(h.tagName.slice(1), 10), text: h.textContent || '' };
  });
  countEl.textContent = items.length;

  listEl.innerHTML = items
    .map(
      (it) =>
        `<a class="toc-item lvl-${it.level}" href="#${it.id}" data-id="${it.id}">${escapeHtml(
          it.text
        )}</a>`
    )
    .join('');

  $$('.toc-item', listEl).forEach((a) => {
    a.addEventListener('click', (e) => {
      e.preventDefault();
      const id = a.getAttribute('data-id');
      const tgt = document.getElementById(id);
      if (tgt) {
        tgt.scrollIntoView({ behavior: 'smooth', block: 'start' });
        // 高亮 1.2s
        tgt.classList.add('hl-flash');
        setTimeout(() => tgt.classList.remove('hl-flash'), 1200);
      }
    });
  });

  // 滚动监听：根据视口最上方第一个标题更新 active
  if (items.length === 0) return;
  const onScroll = () => {
    const top = 80;
    let active = items[0].id;
    for (const it of items) {
      const el = document.getElementById(it.id);
      if (!el) continue;
      const r = el.getBoundingClientRect();
      if (r.top - top <= 0) active = it.id;
      else break;
    }
    $$('.toc-item', listEl).forEach((a) =>
      a.classList.toggle('active', a.dataset.id === active)
    );
  };
  // 节流
  let raf = null;
  const handler = () => {
    if (raf) return;
    raf = requestAnimationFrame(() => { raf = null; onScroll(); });
  };
  // 主滚动容器是 window
  window.addEventListener('scroll', handler, { passive: true });
  onScroll();
}

// 笔记面板：localStorage 按 path 持久化
function setupNotes(path) {
  const key = 'vibe-notes::' + path;
  const ta = $('#notes-area');
  const status = $('#notes-status');
  const meta = $('#notes-meta');
  const exportBtn = $('[data-act=notes-export]');
  const clearBtn = $('[data-act=notes-clear]');

  let timer = null;
  const saved = localStorage.getItem(key) || '';
  ta.value = saved;
  updateMeta();

  ta.addEventListener('input', () => {
    if (status) { status.textContent = '编辑中…'; status.classList.add('dirty'); }
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => {
      localStorage.setItem(key, ta.value);
      if (status) { status.textContent = '已保存'; status.classList.remove('dirty'); }
      updateMeta();
    }, 350);
  });

  ta.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 's') {
      e.preventDefault();
      localStorage.setItem(key, ta.value);
      if (status) { status.textContent = '已保存'; status.classList.remove('dirty'); }
      toast('笔记已保存', 'success', 1200);
    }
  });

  if (exportBtn) {
    exportBtn.addEventListener('click', () => exportAllNotes());
  }
  const syncBtn = $('[data-act=notes-sync]');
  if (syncBtn) {
    syncBtn.addEventListener('click', () => syncNotesToRepo(syncBtn));
  }
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      if (!confirm('确认清空当前页笔记？')) return;
      ta.value = '';
      localStorage.removeItem(key);
      updateMeta();
      toast('已清空当前页笔记', 'info', 1200);
    });
  }

  function updateMeta() {
    const len = (ta.value || '').length;
    if (meta) meta.textContent = `${len} 字`;
  }
}

// 收集所有 localStorage 中的笔记（按 path 区分）
function collectAllNotes() {
  const all = [];
  for (let i = 0; i < localStorage.length; i++) {
    const k = localStorage.key(i);
    if (!k || !k.startsWith('vibe-notes::')) continue;
    const path = k.slice('vibe-notes::'.length);
    const v = localStorage.getItem(k) || '';
    if (v.trim()) all.push({ path, content: v });
  }
  return all;
}

// 把所有笔记写到仓库 notes/ 目录并 git commit；可选 push
async function syncNotesToRepo(btn) {
  const all = collectAllNotes();
  if (!all.length) { toast('还没有任何笔记', 'info'); return; }
  const wantPush = confirm(`将把 ${all.length} 份笔记写入仓库 notes/ 目录并 git commit。\n\n是否同时推送到远程？\n点「确定」同时 push；点「取消」只本地 commit。`);

  const orig = btn.textContent;
  btn.disabled = true;
  btn.textContent = '⏳ 同步中…';
  try {
    const r = await fetch('/api/notes/sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ notes: all, push: wantPush }),
    });
    const data = await r.json();
    if (!r.ok || !data.ok) {
      toast('同步失败：' + (data.error || r.statusText), 'error', 4000);
      console.error(data);
      return;
    }
    let msg = `已写入 ${data.written.length} 份笔记`;
    if (data.committed) msg += ' · 已 commit';
    if (data.pushed)    msg += ' · 已 push';
    toast(msg, 'success', 3500);
    console.log('[notes-sync]', data.log);
  } catch (e) {
    toast('同步失败：' + e, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = orig;
  }
}

function exportAllNotes() {
  const all = [];
  for (let i = 0; i < localStorage.length; i++) {
    const k = localStorage.key(i);
    if (!k || !k.startsWith('vibe-notes::')) continue;
    const path = k.slice('vibe-notes::'.length);
    const v = localStorage.getItem(k) || '';
    if (v.trim()) all.push({ path, content: v });
  }
  if (!all.length) {
    toast('还没有任何笔记', 'info');
    return;
  }
  const ts = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
  const md = [
    `# Vibe Agent · 我的课程笔记`,
    `> 导出时间：${new Date().toLocaleString()}    共 ${all.length} 条`,
    '',
    ...all.map(
      (n) => `## \`${n.path}\`\n\n${n.content.trim()}\n`
    ),
  ].join('\n');
  const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `vibe-agent-notes-${ts}.md`;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => {
    URL.revokeObjectURL(a.href);
    a.remove();
  }, 0);
  toast(`已导出 ${all.length} 条笔记`, 'success');
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
        <button class="btn icon-btn" data-act="layout" title="切换源码与终端的并排/上下布局" aria-label="切换布局">⫴</button>
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
  const btnLayout = $('[data-act=layout]', card);
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

  // ---- 布局切换：单栏 / 并排 ----
  const LAYOUT_KEY = 'vibe-demo-layout';
  // 优先读偏好；否则在宽视口默认 split
  const initialLayout =
    localStorage.getItem(LAYOUT_KEY) ||
    (window.innerWidth >= 1280 ? 'split' : 'stack');
  applyLayout(initialLayout);

  btnLayout.addEventListener('click', (e) => {
    e.stopPropagation();
    const cur = card.classList.contains('split') ? 'split' : 'stack';
    const next = cur === 'split' ? 'stack' : 'split';
    applyLayout(next);
    localStorage.setItem(LAYOUT_KEY, next);
    // 全部 demo 卡片同步
    $$('.demo-card', scope).forEach((c) => c.classList.toggle('split', next === 'split'));
    toast(next === 'split' ? '已切换：源码 / 终端 并排' : '已切换：单栏布局', 'info', 1200);
  });

  function applyLayout(mode) {
    card.classList.toggle('split', mode === 'split');
    btnLayout.textContent = mode === 'split' ? '⫴' : '☰';
    btnLayout.title = mode === 'split' ? '当前：并排 · 点击切换为单栏' : '当前：单栏 · 点击切换为并排';
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

  // pin 按钮：钉住/解除侧栏（写入 localStorage）
  const pinBtn = document.getElementById('pin-btn');
  const app = document.querySelector('.app');
  const pinned = localStorage.getItem('vibe-sidebar-pinned') === '1';
  if (app && pinned) app.classList.add('sidebar-pinned');
  if (pinBtn && app) {
    pinBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      app.classList.toggle('sidebar-pinned');
      const now = app.classList.contains('sidebar-pinned');
      localStorage.setItem('vibe-sidebar-pinned', now ? '1' : '0');
      toast(now ? '侧栏已钉住' : '侧栏已收起', 'info', 1200);
    });
  }
});
