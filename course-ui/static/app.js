/* ===== Vibe Agent Course UI - app.js ===== */
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

const state = {
  courses: [],
  current: { courseId: null, kind: null, path: null },
};

// marked + highlight
marked.setOptions({
  gfm: true,
  breaks: false,
  highlight(code, lang) {
    try {
      if (lang && hljs.getLanguage(lang)) {
        return hljs.highlight(code, { language: lang }).value;
      }
      return hljs.highlightAuto(code).value;
    } catch {
      return code;
    }
  },
});

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

  // 默认进入第一节课
  if (state.courses.length) {
    const first = state.courses[0];
    const piece = first.lectures[0] || first.demos[0];
    if (piece) {
      const kind = first.lectures[0] ? 'lecture' : 'demo';
      openPiece(first.id, kind, piece.path);
    }
  }
}

async function checkBackend() {
  try {
    const t = await fetch('/health').then((r) => r.text());
    $('#backend-status').textContent = t === 'ok' ? '在线' : t;
  } catch {
    $('#backend-status').textContent = '离线';
    $('.dot').classList.add('bad');
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
      <div style="min-width:0; flex:1;">
        <div class="nav-course-title">${escapeHtml(c.title)}</div>
        <div class="nav-course-sub">${escapeHtml(c.subtitle)}</div>
      </div>
      <div class="nav-course-caret">▸</div>
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
  el.innerHTML = `<span class="badge ${kind}">${kind === 'py' ? 'PY' : 'MD'}</span>${escapeHtml(
    title
  )}`;
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
    const html = marked.parse(data.content || '');
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
    $$('.markdown pre code').forEach((b) => hljs.highlightElement(b));
  } catch (e) {
    body.innerHTML = `<div class="markdown">加载失败：${escapeHtml(String(e))}</div>`;
  }
}

// ---------------- Demo 列表（代码示例 tab） ----------------
async function renderDemos(course) {
  const body = $('#tab-body');
  if (!course.demos.length) {
    body.innerHTML = '<div class="markdown">本节没有可运行的 Python 示例。</div>';
    return;
  }
  body.innerHTML = '';
  for (const demo of course.demos) {
    const card = await buildDemoCard(demo);
    body.appendChild(card);
  }
}

async function buildDemoCard(demo) {
  const card = document.createElement('div');
  card.className = 'demo-card';
  card.innerHTML = `
    <div class="demo-head">
      <div class="demo-title">
        <div class="name">${escapeHtml(demo.title)}</div>
        <div class="file">${escapeHtml(demo.path)}</div>
      </div>
      <button class="btn secondary" data-act="toggle-src">查看源码</button>
      <button class="btn primary" data-act="run">▶ 运行</button>
      <button class="btn danger" data-act="stop" style="display:none;">■ 停止</button>
    </div>
    <div class="demo-body">
      <div class="demo-source" style="display:none;"><pre><code class="language-python">加载中…</code></pre></div>
      <div class="terminal">
        <div class="terminal-head">
          <div class="lights"><span class="r"></span><span class="y"></span><span class="g"></span></div>
          <div class="label">terminal · ${escapeHtml(demo.path.split('/').pop())}</div>
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

  const btnSrc = $('[data-act=toggle-src]', card);
  const btnRun = $('[data-act=run]', card);
  const btnStop = $('[data-act=stop]', card);
  const srcWrap = $('.demo-source', card);
  const srcCode = $('.demo-source code', card);
  const out = $('.terminal-output', card);
  const status = $('.terminal-head .status', card);
  const inputBar = $('.terminal-input', card);
  const inputEl = $('input', inputBar);
  const sendBtn = $('button', inputBar);

  let runId = null;
  let evtSource = null;
  let srcLoaded = false;

  btnSrc.addEventListener('click', async () => {
    const isHidden = srcWrap.style.display === 'none';
    srcWrap.style.display = isHidden ? 'block' : 'none';
    btnSrc.textContent = isHidden ? '收起源码' : '查看源码';
    if (isHidden && !srcLoaded) {
      try {
        const data = await fetch('/api/file?path=' + encodeURIComponent(demo.path)).then((r) =>
          r.json()
        );
        srcCode.textContent = data.content || '';
        hljs.highlightElement(srcCode);
        srcLoaded = true;
      } catch (e) {
        srcCode.textContent = '加载失败：' + e;
      }
    }
  });

  btnRun.addEventListener('click', () => {
    out.innerHTML = '';
    appendMeta(out, `▶ 启动 ${demo.path} ...`);
    status.textContent = '运行中';
    status.className = 'status running';
    btnRun.disabled = true;
    btnStop.style.display = 'inline-flex';
    inputBar.classList.remove('disabled');

    evtSource = new EventSource('/api/run?path=' + encodeURIComponent(demo.path));
    evtSource.addEventListener('start', (e) => {
      const d = JSON.parse(e.data);
      runId = d.run_id;
      appendMeta(out, `[runner] python=${d.python}  pid=${d.run_id}`);
    });
    evtSource.addEventListener('stdout', (e) => {
      append(out, JSON.parse(e.data), 'stdout');
    });
    evtSource.addEventListener('stderr', (e) => {
      append(out, JSON.parse(e.data), 'stderr');
    });
    evtSource.addEventListener('exit', (e) => {
      const d = JSON.parse(e.data);
      const ok = d.code === 0;
      append(out, `\n[exit code ${d.code}]`, ok ? 'exit-ok' : 'exit-fail');
      status.textContent = ok ? '已完成' : `异常退出 (${d.code})`;
      status.className = 'status ' + (ok ? 'ok' : 'fail');
      cleanup();
    });
    evtSource.onerror = () => {
      append(out, '\n[连接已断开]', 'exit-fail');
      status.textContent = '已断开';
      status.className = 'status fail';
      cleanup();
    };
  });

  btnStop.addEventListener('click', async () => {
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
  sendBtn.addEventListener('click', send);
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

// 目录按钮：滚动到主区域顶部
$('#btn-toc').addEventListener('click', () => {
  $('.content').scrollIntoView({ behavior: 'smooth' });
});
