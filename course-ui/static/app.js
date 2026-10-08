/* ===== Vibe Agent Course UI - app.js ===== */
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

const state = {
  courses: [],
  current: { courseId: null, kind: null, path: null },
  // 跨 tab 记忆：切换 讲义/代码示例 后回到之前看的位置
  lastLecturePath: null,
  lastDemoPath: null,
  // 由 server /api/courses 注入的运行时 env，比如 cnb_web_url
  env: { cnb_web_url: '' },
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
  // hljs 在第一次高亮后会给元素打上 data-highlighted="yes" 并加 hljs/语言 class，
  // 第二次直接调 highlightElement 会被它跳过（导致保存后只显示纯文本）。
  // 这里先把状态清掉，再重新高亮。
  try {
    el.removeAttribute('data-highlighted');
    const keepLangClass = Array.from(el.classList).find(c => c.startsWith('language-'));
    el.className = keepLangClass || '';
    window.hljs.highlightElement(el);
  } catch {}
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
  state.env = r.env || { cnb_web_url: '' };
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

// 从文件路径里抠出第一个数字段（讲义/demo 的编号）
function extractNumFromPath(p) {
  const fname = (p || '').split('/').pop() || '';
  const m = fname.match(/(\d+)/);
  return m ? m[1].replace(/^0+/, '') : null;
}
function findMatchingDemo(course, lecturePath) {
  const num = extractNumFromPath(lecturePath);
  if (!num) return null;
  return (
    course.demos.find((d) => {
      const dn = extractNumFromPath(d.path);
      return dn === num;
    }) || null
  );
}
function findMatchingLecture(course, demoPath) {
  const num = extractNumFromPath(demoPath);
  if (!num) return null;
  return (
    course.lectures.find((l) => {
      const ln = extractNumFromPath(l.path);
      return ln === num;
    }) || null
  );
}

// ---------------- 打开内容 ----------------
async function openPiece(courseId, kind, path) {
  // 记忆当前位置（方便跨 tab 跳转时回到原小节）
  if (kind === 'lecture') {
    state.lastLecturePath = path;
  } else if (kind === 'demo') {
    state.lastDemoPath = path;
  }
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

  // Tabs：讲义 / 代码示例 / 随堂练习
  // 「随堂练习」仅在 server 发现 exercises/<同名> 目录时才显示（用 course.exercises 判定），
  // 没有就只渲染前两个 tab，避免出现「点进去空白」的尴尬。
  const exTab = course.exercises
    ? `<div class="tab ${kind === 'exercise' ? 'active' : ''}" data-tab="exercise">
         📝 随堂练习 <span class="pill">${course.exercises.items.length}</span>
       </div>`
    : '';
  const tabsHtml = `
    <div class="tabs-row">
      <div class="tabs">
        <div class="tab ${kind === 'lecture' ? 'active' : ''}" data-tab="lecture">
          📚 讲义 <span class="pill">${course.lectures.length}</span>
        </div>
        <div class="tab ${kind === 'demo' ? 'active' : ''}" data-tab="demo">
          🐍 代码示例 <span class="pill">${course.demos.length}</span>
        </div>
        ${exTab}
      </div>
    </div>
  `;

  $('#content').innerHTML = header + tabsHtml + '<div id="tab-body"></div>';
  $('#content').dataset.kind = kind;

  $$('.tab').forEach((t) =>
    t.addEventListener('click', () => {
      const newKind = t.dataset.tab;
      if (newKind === kind) return;
      // 「随堂练习」tab：固定切到本章练习视图，不依赖 piece（练习不是讲义/demo 那种条目）。
      // 用一个伪 path（目录路径）放进 state.current 仅用于面包屑显示。
      if (newKind === 'exercise') {
        if (!course.exercises) return;
        openPiece(courseId, 'exercise', course.exercises.dir);
        return;
      }
      let piece;
      if (newKind === 'lecture') {
        // 切到讲义：① 当前 demo 对应的讲义 > ② 上次看的讲义 > ③ 第一篇
        piece =
          (kind === 'demo' ? findMatchingLecture(course, path) : null) ||
          (state.lastLecturePath
            ? course.lectures.find((l) => l.path === state.lastLecturePath)
            : null) ||
          course.lectures[0];
      } else {
        // 切到 demo：① 当前讲义对应的 demo > ② 上次看的 demo > ③ 第一个
        piece =
          (kind === 'lecture' ? findMatchingDemo(course, path) : null) ||
          (state.lastDemoPath
            ? course.demos.find((d) => d.path === state.lastDemoPath)
            : null) ||
          course.demos[0];
      }
      if (piece) openPiece(courseId, newKind, piece.path);
    })
  );

  if (kind === 'lecture') {
    await renderLecture(path);
  } else if (kind === 'exercise') {
    await renderExercises(course);
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

    // 跨 tab 跳转：讲义 → Demo（精准到对应小节）
  // 改造点：原本 demo 跳转 banner 放在讲义正文「顶部」，按用户要求挪到「末尾」，
  // 同时格式从横条 banner 升级为「随堂练习」tab 同款卡片（.ex-card），
  // 通过修饰类 .ex-card--demo 切到蓝调（代码示例语义）。
  const course = state.courses.find((c) => c.id === state.current.courseId);
  const matchedDemo = course ? findMatchingDemo(course, path) : null;
  const fallbackDemo = course && course.demos.length ? course.demos[0] : null;
  const demoTarget = matchedDemo || fallbackDemo;
  const num = extractNumFromPath(path);
  const demoTitle = matchedDemo && num
    ? `第 ${num.padStart(2, '0')} 节代码示例`
    : (fallbackDemo ? '本节代码示例' : '');
  const demoJumpCard = demoTarget
    ? `<div class="ex-card ex-card--demo"
            data-demo="${escapeHtml(demoTarget.path)}"
            title="跳转到对应代码示例">
         <div class="ex-card-no">🐍</div>
         <div class="ex-card-main">
           <div class="ex-card-title">${escapeHtml(demoTitle)}</div>
           <div class="ex-card-file">
             <span class="badge py">PY</span>
             <code>${escapeHtml(demoTarget.path)}</code>
           </div>
         </div>
         <div class="ex-card-cta">在代码示例 tab 中打开 →</div>
       </div>`
    : '';

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

        <article class="markdown" id="lecture-md">
          ${html}
          ${demoJumpCard}
        </article>

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

    // 改造 markdown 里的「随堂练习」链接为卡片样式，并劫持跳转走 openFolderInIDE
    //
    // 为什么要在前端做、而不是改 markdown？
    //   讲义里有 30+ 处 `🧪 [xxx](https://cnb.cool/.../exercises/<chapter>/<file or dir>)`
    //   形式的链接，原本跳的是 CNB 仓库网页 —— **打不开云端 IDE、也定位不到目录**。
    //   逐个改 markdown 工作量大且容易漏，所以统一在渲染后做 DOM 改写。
    //
    // 识别规则：链接 href 匹配 .../exercises/<rest> 即视为「练习链接」。
    //   - 如果 <rest> 末尾是 .py，文件名作为 toast 提示，folder 取其父目录
    //   - 否则 <rest> 直接作为目标目录
    rewriteExerciseLinks($('.markdown', body));

    // 构建大纲 / 滚动联动
    buildTOC($('#lecture-md'), $('#toc-list'), $('#toc-count'));
    // 启用笔记
    setupNotes(path);

    // 跨 tab 跳转：讲义末尾的「代码示例」卡片整体可点
    const jumpLink = $('.ex-card--demo[data-demo]', body);
    if (jumpLink) {
      jumpLink.addEventListener('click', (e) => {
        e.preventDefault();
        const demoPath = jumpLink.dataset.demo;
        if (demoPath && state.current.courseId) {
          state.lastDemoPath = demoPath;
          openPiece(state.current.courseId, 'demo', demoPath);
        }
      });
    }
  } catch (e) {
    body.innerHTML = `<div class="markdown">加载失败：${escapeHtml(String(e))}</div>`;
  }
}

/**
 * 把讲义 markdown 内的「随堂练习」链接改写为统一的 .ex-card 卡片。
 *
 * 识别规则：<a href> 里包含 `/exercises/<chapter>/<rest>` 子串（兼容 CNB 仓库
 * URL 与相对路径两种来源）。匹配到后做两件事：
 *   1) 用一个 <div class="ex-card"> 卡片替换 <a>，外观与随堂练习 tab 一致
 *   2) 卡片 click 调 openFolderInIDE(targetDir, hintFilename) —— 让所有讲义内
 *      练习入口都走与 tab 卡片相同的跳转路径（带 encodeURIComponent，能正确
 *      定位到指定目录，不再依赖 CNB 仓库网页）
 *
 * 容错点：
 *   - 仓库 URL 带前缀（cnb.cool/<owner>/<repo>/-/blob/<branch>/exercises/...
 *     或 .../-/tree/<branch>/exercises/...）；用正则只抓 `/exercises/` 之后的
 *     部分。
 *   - 末尾 .py 的文件名作为 toast 「请在左侧打开 xxx」的提示，folder 取其父目录。
 */
function rewriteExerciseLinks(scope) {
  if (!scope) return;
  // 命中 .../exercises/<rest>，捕获 <rest>（去掉可能的 query/hash）
  const RE = /\/exercises\/([^?#]+?)\/?(?:$|[?#])/;
  $$('a[href]', scope).forEach((a) => {
    const href = a.getAttribute('href') || '';
    const m = href.match(RE);
    if (!m) return;
    const rest = m[1]; // 形如 "02-tools-and-agent-loop" 或 "02-tools-and-agent-loop/ex_2_1.py"
    const parts = rest.split('/');
    const last = parts[parts.length - 1];
    const isFile = /\.[a-z0-9]+$/i.test(last);
    const targetDir = isFile ? parts.slice(0, -1).join('/') : rest;
    const hintFile = isFile ? last : null;

    const label = (a.textContent || '').replace(/^🧪\s*/, '').trim() || (hintFile || targetDir);
    const card = document.createElement('div');
    card.className = 'ex-card ex-card--exercise';
    card.dataset.targetDir = 'exercises/' + targetDir;
    if (hintFile) card.dataset.hintFile = hintFile;
    card.innerHTML = `
      <div class="ex-card-no">🧪</div>
      <div class="ex-card-main">
        <div class="ex-card-title">${escapeHtml(label)}</div>
        <div class="ex-card-file">
          <span class="badge py">${escapeHtml(hintFile ? 'PY' : 'DIR')}</span>
          <code>exercises/${escapeHtml(rest)}</code>
        </div>
      </div>
      <div class="ex-card-cta">在云端 IDE 打开 →</div>
    `;
    card.addEventListener('click', () => {
      openFolderInIDE(card.dataset.targetDir, card.dataset.hintFile || null);
    });

    // 如果原 <a> 单独占一段（外层是 <p> 且只有这一个有效子节点），直接替换段落，
    // 这样卡片不会卡在 <p> 的行内排版里。否则就地替换 <a>。
    const parent = a.parentElement;
    if (parent && parent.tagName === 'P' && parent.childNodes.length === 1) {
      parent.replaceWith(card);
    } else {
      a.replaceWith(card);
    }
  });
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

  // 决定展开哪一张：优先用 state.current.path（来自侧栏/跨 tab 跳转），
  // 否则默认展开第一张
  const targetPath = state.current && state.current.kind === 'demo'
    ? state.current.path
    : null;
  let targetIdx = course.demos.findIndex((d) => d.path === targetPath);
  if (targetIdx < 0) targetIdx = 0;

  course.demos.forEach((demo, idx) => {
    const card = buildDemoCard(demo, idx + 1, wrap, course);
    wrap.appendChild(card);
    if (idx === targetIdx) toggleCard(card, wrap, true);
  });

  // 滚动到展开的卡片
  const openCard = $('.demo-card.open', wrap);
  if (openCard && targetIdx > 0) {
    setTimeout(() => openCard.scrollIntoView({ behavior: 'smooth', block: 'start' }), 60);
  }
}

// ---------------- 随堂练习（独立 tab） ----------------
// 渲染本章练习题：顶部一段说明 banner + 章节 README（题目介绍）+ 每题一张卡片。
// 任何位置点击都跳云端 IDE 的练习目录（code-server 只能开目录，不能直接开单文件）。
async function renderExercises(course) {
  const body = $('#tab-body');
  if (!course.exercises) {
    body.innerHTML = '<div class="markdown">本章暂无练习题。</div>';
    return;
  }
  const ex = course.exercises;

  // 1) 加载本章 README（题目说明）
  let readmeHtml = '';
  if (ex.readme) {
    try {
      const data = await fetch('/api/file?path=' + encodeURIComponent(ex.readme)).then((r) => r.json());
      readmeHtml = renderMarkdown(data.content || '');
    } catch (e) {
      readmeHtml = `<p class="ex-readme-err">README 加载失败：${escapeHtml(String(e))}</p>`;
    }
  }

  // 2) 拼整体结构
  body.innerHTML = `
    <div class="exercises-layout">
      <div class="ex-banner">
        <div class="ex-banner-icon">📝</div>
        <div class="ex-banner-text">
          <div class="ex-banner-title">本章随堂练习</div>
          <div class="ex-banner-sub">
            目录 <code>${escapeHtml(ex.dir)}/</code> · 共 ${ex.items.length} 题 ·
            点击任意题目跳到云端 IDE，补全 <code>TODO</code> 后运行看到 <code>✅ PASSED</code> 即完成
          </div>
        </div>
        <button class="ex-open-all" data-act="open-dir">☁ 在云端 IDE 打开整个目录 →</button>
      </div>

      ${readmeHtml ? `<article class="markdown ex-readme">${readmeHtml}</article>` : ''}

      <div class="ex-list">
        ${ex.items.map((it, i) => `
          <div class="ex-card" data-path="${escapeHtml(it.path)}">
            <div class="ex-card-no">${String(i + 1).padStart(2, '0')}</div>
            <div class="ex-card-main">
              <div class="ex-card-title">${escapeHtml(it.title)}</div>
              <div class="ex-card-file">
                <span class="badge py">PY</span>
                <code>${escapeHtml(it.path)}</code>
              </div>
            </div>
            <div class="ex-card-cta">在云端 IDE 打开 →</div>
          </div>
        `).join('')}
      </div>
    </div>
  `;

  // 修复 README 里的相对图片路径（同 renderLecture 的处理）
  if (ex.readme) {
    const baseDir = ex.readme.split('/').slice(0, -1).join('/');
    $$('.ex-readme img').forEach((img) => {
      const src = img.getAttribute('src');
      if (src && !/^https?:\/\//.test(src) && !src.startsWith('/')) {
        img.src = '/api/asset?path=' + encodeURIComponent(`${baseDir}/${src}`);
      }
    });
    highlightAll($('.ex-readme', body));
  }

  // 3) 交互：整目录按钮 + 每题卡片点击都跳 IDE
  // 备注：CNB code-server 不支持 ?file= 打开单文件，所以每题点击实际也是打开目录，
  // 用户在 IDE 左侧文件树里点对应 ex_*.py 即可。这里为提示精确度，toast 里带上文件名。
  const dirBtn = $('[data-act=open-dir]', body);
  if (dirBtn) {
    dirBtn.addEventListener('click', (e) => {
      e.preventDefault();
      openFolderInIDE(ex.dir);
    });
  }
  $$('.ex-card', body).forEach((card) => {
    card.addEventListener('click', () => {
      const p = card.dataset.path;
      // 用文件名作为「定位提示」，但 folder= 仍然传目录
      openFolderInIDE(ex.dir, p ? p.split('/').pop() : null);
    });
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

function buildDemoCard(demo, indexNum, scope, course) {
  // 从文件名抓出 demo_XX 的数字
  const m = demo.filename.match(/demo[_-]?(\d+)/i);
  const demoNum = m ? m[1] : null;
  const numLabel = demoNum ? demoNum.padStart(2, '0') : String(indexNum).padStart(2, '0');

  // 找对应讲义：用 demo 数字匹配 lecture path 中的相同数字
  let matchedLecture = null;
  if (demoNum && course && course.lectures.length) {
    const numStr = demoNum.replace(/^0+/, ''); // "06" → "6"
    matchedLecture = course.lectures.find(l => {
      const lm = l.path.match(/(\d+)/);
      return lm && lm[1].replace(/^0+/, '') === numStr;
    });
  }

  const jumpHTML = matchedLecture
    ? `<a class="demo-jump-lecture" data-lecture="${escapeHtml(matchedLecture.path)}" title="跳转到第 ${numLabel} 节讲义">📚 讲义 第${numLabel}节</a>`
    : '';

  const card = document.createElement('div');
  card.className = 'demo-card';
  card.innerHTML = `
    <div class="demo-head">
      <div class="index-chip">${numLabel}</div>
      <div class="live-pulse" title="运行状态"></div>
      <div class="demo-title">
        <div class="name">${escapeHtml(demo.title)}</div>
        <div class="file">
          ${escapeHtml(demo.path)}
          ${jumpHTML}
        </div>
      </div>
      <div class="demo-actions">
        <button class="btn primary" data-act="run" title="运行 (Cmd/Ctrl+Enter)">▶ <span class="btn-label">运行</span></button>
        <button class="btn danger" data-act="stop" style="display:none;" title="停止">■ <span class="btn-label">停止</span></button>
      </div>
      <div class="caret">›</div>
    </div>
    <div class="demo-body">
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
    if (e.target.closest('.btn, .demo-jump-lecture')) return;
    toggleCard(card, scope);
  });

  // ---- 跳转到对应讲义 ----
  const jumpLect = $('.demo-jump-lecture', card);
  if (jumpLect) {
    jumpLect.addEventListener('click', (e) => {
      e.stopPropagation();
      e.preventDefault();
      const lectPath = jumpLect.dataset.lecture;
      if (lectPath && state.current.courseId) {
        state.lastLecturePath = lectPath;
        openPiece(state.current.courseId, 'lecture', lectPath);
      }
    });
  }

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

  // ---- 布局：固定为单栏（源码上 / 终端下），不再提供切换 ----

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

// ---------------- 跳转到 CNB 云端 IDE ----------------
// 顶栏「☁ 云端 IDE」按钮：打开整个工作区根。复用 openFolderInIDE("")，让所有跳转
// 走同一个 URL 拼接逻辑（含 encodeURIComponent / 末尾斜杠归一化），避免两套实现走样。
function openInVscode() {
  if (!state.env || !state.env.cnb_web_url) {
    toast('当前不在 CNB 环境中，云端 IDE 入口不可用', 'warn', 3000);
    return;
  }
  openFolderInIDE('');
}

/**
 * 在 CNB 云端 IDE（vscode-web / code-server）中打开仓库内的某个子目录。
 *
 * code-server 标准入口：<root>/?folder=<容器内绝对路径>
 * CNB 把仓库挂载到容器内 /workspace，所以传 "exercises/03-..." 这种相对路径，
 * 这里拼成 /workspace/exercises/03-...。
 *
 * 跳转 bug 关键修复点（之前点了 IDE 没切到指定目录）：
 *   ① 必须 encodeURIComponent 路径 —— 反代层若不编码，参数可能在反向代理转发时被吞掉
 *      或被切断（CNB 的 web URL 自带 /-/vscode-web/cnb-xxx-001/ 多级路径，未编码的
 *      绝对路径里的 / 会跟反代规则冲突）
 *   ② 拼 URL 前要把 root 末尾斜杠去净、再统一加一个 / 与 ?folder=，避免出现
 *      "<root>//?folder=" 这种导致 code-server 404 或忽略参数的形态
 *   ③ window.open 用 noopener，避免新窗口拿到 opener 引用
 *
 * @param {string} relPath   仓库相对目录，如 "exercises/02-tools-and-agent-loop"
 * @param {string=} hintFile 仅用于 toast 提示「在左侧文件树点 xxx 打开」，不进 URL
 */
function openFolderInIDE(relPath, hintFile) {
  const root = (state.env && state.env.cnb_web_url) || '';
  if (!root) {
    toast('当前不在 CNB 环境中，云端 IDE 入口不可用', 'warn', 3000);
    return;
  }
  const clean = String(relPath || '').replace(/^\/+|\/+$/g, '');
  // 容器内的绝对路径要整段 encode（含开头的斜杠），让反代层把它原样转给 code-server
  const folderAbs = '/workspace/' + clean;
  const target = `${root.replace(/\/+$/, '')}/?folder=${encodeURIComponent(folderAbs)}`;
  window.open(target, '_blank', 'noopener');
  const tip = hintFile
    ? `已打开 ${clean}/，请在左侧文件树点 ${hintFile}`
    : `已在云端 IDE 打开 ${clean}/`;
  toast(tip, 'info', 2400);
}

// ---------------- 启动钩子 ----------------
document.addEventListener('DOMContentLoaded', () => {
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
