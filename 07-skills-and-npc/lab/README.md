# Day7 · 实操指南

> **核心任务**：Part1 给 Agent 加 Skills 扩展系统；Part2 把 Agent 打包成 Docker 镜像挂到仓库做 NPC。

---

## 时间规划（约 100 分钟实操）

| 阶段 | 时间 | 内容 |
|------|------|------|
| A · Skills 实现 | 30 min | 写 Skills 加载器 + 2 个工具 + 1 个自定义 SKILL.md |
| B · Skills 验证 | 20 min | 跑 demo_33 + 用 Agent 测试"加 skill 前 vs 后"对比 |
| C · Docker 打包 | 20 min | 用模板 Dockerfile 构建镜像，本地验证 |
| D · NPC 上线 | 20 min | 配 .cnb.yml + settings.yml + push + 在 Issue 里 @ |
| E · 截图提交 | 10 min | 截图 NPC 回复 + git push |

---

## Part 1 · Skills 扩展（50 分钟）

### 阶段 A · 实现 Skills 系统

1. 在你的 `my_coding_agent/` 下建 `skills/` 目录
2. 复制 `demos/skills/add-docstring/SKILL.md` 作为第一个 skill
3. 把 `demos/skills_loader.py` 复制到你的项目里
4. 给 ToolRegistry 注册 2 个新工具：

```python
@registry.tool("列出所有可用的 Skills")
def list_skills() -> str:
    return skills.to_index_prompt()

@registry.tool("加载指定 skill 的完整规范")
def load_skill(name: str) -> str:
    return skills.load(name)
```

5. 在 Agent 的 system prompt 尾部追加 `skills.to_index_prompt()`

### 阶段 B · 验证

对比测试：
1. **关闭 Skills**：问 Agent "帮我给 bash.py 里的函数加 docstring"
2. **开启 Skills**：同样的问题再问一次
3. 看差异：有 Skill 时 Agent 是否自动 load_skill → 按 Google 风格生成

---

## Part 2 · Docker + NPC 上线（50 分钟）

### 阶段 C · Docker 打包

1. 从 `lab/templates/` 复制 4 个文件到你的仓库根：
   - `Dockerfile`
   - `npc-entrypoint.sh`
   - `cnb.yml` → 重命名为 `.cnb.yml`
   - `settings.yml` → 放到 `.cnb/settings.yml`

2. 修改 `.cnb/settings.yml` 里的 NPC 名字

3. 本地构建验证：
```bash
docker build -t my-agent:latest .
docker run --rm my-agent:latest --help
```

### 阶段 D · NPC 上线

1. 在仓库 Settings → Secrets 配置：
   - `HUNYUAN_API_KEY`
   - `HUNYUAN_BASE_URL`

2. `git push` 触发镜像构建

3. 等构建完成后，在 Issue 里评论：
```
@你的用户名/仓库名(my-agent) 帮我介绍一下这个仓库
```

4. 等待 NPC 回复 → **截图**

### 阶段 E · 提交

```bash
git add .
git commit -m "day7: add skills + npc deployment"
git push
```

---

## 助教检查重点

1. `skills/add-docstring/SKILL.md` 存在且格式正确
2. ToolRegistry 里有 list_skills + load_skill 两个工具
3. Dockerfile + npc-entrypoint.sh + .cnb.yml + .cnb/settings.yml 4 个文件齐全
4. Issue 里有 NPC 回复的截图
5. "加 Skill 前 vs 后"的对比记录

---

## 4 份模板

都在 `lab/templates/` 下：

| 文件 | 放到哪 | 需要改什么 |
|------|--------|-----------|
| `Dockerfile` | 仓库根 | COPY 路径（如果目录结构不同） |
| `npc-entrypoint.sh` | 仓库根 | 一般不用改 |
| `cnb.yml` | 仓库根（重命名为 `.cnb.yml`） | 一般不用改 |
| `settings.yml` | `.cnb/settings.yml` | 改 NPC 名字 |
