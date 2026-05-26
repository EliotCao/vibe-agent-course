# Day7 · 课后练习

---

## 必做（3 道）

### 7.1 写一个自定义 Skill

**要求**：写一个与你未来实际工作/项目相关的 Skill。

参考方向：
- `code-review`：代码审查清单（命名/复杂度/错误处理/测试覆盖）
- `api-design`：RESTful API 设计规范（路径/状态码/分页/错误格式）
- `git-workflow`：Git 分支管理规范（feature/release/hotfix）

**验收标准**：
- `skills/<name>/SKILL.md` 存在且包含正确的 frontmatter
- 用 `list_skills` 能看到、用 `load_skill` 能加载
- 给 Agent 一个相关任务，观察它自动加载并遵循你的 Skill

---

### 7.2 让 NPC 回复 3 次不同的问题

**要求**：在你仓库的 Issue 里分别问 NPC：
1. "帮我看看 README 有没有过时的内容"
2. "这个项目用了哪些依赖，分别是做什么的"
3. "帮我找一下代码里有没有 TODO 注释"

**验收标准**：
- 3 条 NPC 回复截图
- 每条回复要有实质内容（不是空话）

---

### 7.3 NPC 故障排查

**要求**：故意制造一个 NPC 故障（比如删掉 Secrets 里的 API Key），然后：
1. 触发 NPC → 观察失败
2. 查看流水线日志找到错误原因
3. 修复并重新触发
4. 记录完整排查过程到 `troubleshooting.md`

**验收标准**：
- `troubleshooting.md` 包含：故障现象 → 日志关键行 → 根因分析 → 修复步骤

---

## 选做（2 道）

### 7.4 ★ Skills 自动匹配（不用 list_skills + load_skill）

**要求**：修改 Agent，让它在每次 chat 开始时自动调 `skills.match(user_input)`，如果匹配到 skill 就自动加载，不需要 LLM 主动调 list_skills / load_skill。

**思考**：这样做的优缺点是什么？（token 节省 vs LLM 自主决策的灵活性）

---

### 7.5 ★ 让 NPC 支持 PR Review

**要求**：当有人在 PR 评论里 @ NPC 时，让 NPC 能读到 PR 的 diff 并给出 review 意见。

**提示**：
- `git diff origin/main..HEAD` 可以拿到 diff
- 把 diff 注入到 user prompt 里让 Agent 审阅
- 可能需要修改 npc-entrypoint.sh

---

## 答案要点（教师参考）

| 题号 | 关键点 |
|------|--------|
| 7.1 | frontmatter 格式正确 + body 有实际规范内容 + Agent 能自动加载 |
| 7.2 | NPC 正常工作 = Dockerfile + Pipeline + Secrets 都配对了 |
| 7.3 | 重点是排查过程的条理性，不是"改对了就行" |
| 7.4 | 在 agent.py 的 chat 开头加 `matched = skills.match(user_input); for s in matched: skills.load(s)` |
| 7.5 | npc-entrypoint.sh 里加 `git diff` 并 prepend 到 task 变量 |
