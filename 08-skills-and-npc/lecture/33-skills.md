# 第 33 节 · Skills 系统：为什么需要、SKILL.md 标准、加载机制

## 一句话回答

> **Skills = 可热插拔的领域知识包。** 让同一个 Agent 面对不同团队/项目时，自动切换到正确的规范——不用改代码。

## 为什么 system prompt 不够

![为什么需要 Skills](./images/33-why-skills.png)

想象你在同一家公司接了 3 个项目：

| 项目 | 代码规范 | 测试要求 | 提交格式 |
|---|---|---|---|
| 前端 React | 函数组件 + hooks + 禁止 class | vitest | `feat(ui): xxx` |
| 后端 Go | 错误必须用 sentinel + wrap | go test -race | `fix(api): xxx` |
| 数据流水线 | PEP8 + type hint 100% | pytest --cov ≥80% | `chore(etl): xxx` |

如果把 3 套规范全塞进 system prompt：
- token 炸裂（每次都付 3 倍钱）
- LLM 容易"串台"

**Skills 的解法：**
- 每套规范 = 一个 `SKILL.md` 文件
- 启动时只加载**索引**（name + description，极小）
- 用户问题匹配到哪个 skill，才加载对应的**完整指令**

## SKILL.md 格式标准

```markdown
---
name: add-docstring
description: 给 Python 函数添加 Google 风格 docstring
---

# 使用规则

当用户要求"加注释""加文档""补 docstring"时，遵循以下规范：

## 格式
- Google 风格 docstring
- 第一行是简短描述（不超 72 字符）
- Args / Returns / Raises 三段

## 示例

```python
def fetch_user(user_id: int, timeout: float = 5.0) -> dict:
    """根据 ID 获取用户信息。

    Args:
        user_id: 用户唯一标识符。
        timeout: HTTP 超时（秒），默认 5.0。

    Returns:
        用户信息字典，包含 name / email / role。

    Raises:
        NotFoundError: user_id 不存在时。
    """
```
```

### frontmatter 字段

| 字段 | 必填 | 作用 |
|------|------|------|
| `name` | ✅ | Skill 唯一标识（用于匹配 + 加载） |
| `description` | ✅ | 一句话描述（注入到 system prompt 索引里） |

## 渐进式加载机制

```
Level 1（启动时）：
  扫描 skills/ → 解析 frontmatter → 生成索引
  注入到 system prompt：
    "可用 Skills: add-docstring(给函数加 docstring) / go-sentinel(Go 错误规范) / ..."

Level 2（运行时）：
  用户问 "帮我给这个函数加文档"
  → 匹配到 add-docstring
  → 加载完整 body 注入到 system prompt
  → LLM 按照 body 里的格式规范生成 docstring
```

**好处**：
1. 启动 token 极小（索引只有几十个 token）
2. 只付当次真正需要的 skill 的 token 成本
3. 新增 skill 不用改代码——放一个 .md 文件进去就行

## 给 Agent 加 `list_skills` 和 `load_skill` 工具

最小实现只要 2 个新工具：

```python
@registry.tool("列出所有可用的 Skills 名称和描述")
def list_skills() -> str:
    return skills.to_index_prompt()

@registry.tool("加载指定 skill 的完整规范到上下文中")
def load_skill(name: str) -> str:
    return skills.load(name)
```

这样 LLM 就可以**自己决定什么时候该加载哪个 skill**——不需要人手动指定。

## 动手试试

1. 在 `my_coding_agent/skills/` 下建一个 `add-docstring/SKILL.md`
2. 给 ToolRegistry 添加 `list_skills` + `load_skill` 两个工具
3. 用 Agent 问"帮我给 bash.py 里的函数加 docstring"
4. 观察 Agent 是否自动 `load_skill("add-docstring")` → 按规范生成

## 小结

- Skills = 热插拔的领域规范包，解决"多项目多规范"问题
- SKILL.md = YAML frontmatter（元数据）+ Markdown body（完整指令）
- 渐进式加载：启动只加索引，运行时按需加 body
- 给 Agent 加 2 个工具（list_skills / load_skill）就能让 LLM 自主管理 Skills

---

## 随堂练习

> 看懂 SKILL.md 标准不算数，**自己写一个能跑通的 Skill** 才算。下面这道必做题就是让你为真实项目场景产出一份 SKILL.md，并让 Agent 自动加载它：
>
> 🧪 [作业 7.1 · 写一个自定义 Skill](https://cnb.cool/xidian/vibe-coding-learning/vibe-agent-course/-/blob/main/exercises/08-skills-and-npc/README.md)（README 中的 §7.1）
>
> 进阶选做：把"`list_skills` + `load_skill` 由 LLM 调"改成"chat 入口自动 `skills.match()`"，体会 token 节省 vs LLM 自主决策的权衡：
>
> 🧪 [作业 7.4 ★ Skills 自动匹配](https://cnb.cool/xidian/vibe-coding-learning/vibe-agent-course/-/blob/main/exercises/08-skills-and-npc/README.md)（README 中的 §7.4）
