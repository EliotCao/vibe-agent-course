# 第 33 节 · Skills：为什么需要、与 Tool Call 的区别、实现原理

## 一句话回答

> **Skill = 可热插拔的领域知识包（一份 `SKILL.md`）。** 让同一个 Agent 面对不同团队/项目时，自动切换到正确的规范——不改一行代码。

## 一、为什么需要 Skills：一个"扩展性"问题

![为什么需要 Skills](./images/33-why-skills.png)

Skills 要解决的根本问题只有一个：

> **怎样让一个 Agent 不断新增领域能力/规范——却不用改代码、也不撑爆 prompt？**

比如同一个人接了 3 个项目（前端 React、后端 Go、数据流水线），规范各不相同，以后还会接第 4、第 5 个。两种朴素做法扩展性都不行：

- **全塞进 system prompt**：每加一个项目就堆一段 → token 炸裂、规范互相串台，且 prompt 是"一次性全量加载"，无法随能力增长扩展。
- **写成 Tool / 硬编码**：每扩展一次要写代码 + 注册 + 重新部署，成本高，非工程用户也上不了手。

**Skills 的解法：扩展 = 往 `skills/` 目录丢一个 `SKILL.md` 文件。** 三个扩展性优点：

- **零代码热插拔**：新增能力只是加一个 `.md`，不改代码、不重启
- **按需加载不膨胀**：启动只装索引（name + 一句话，几十 token），命中才加载全文——能力越多，常驻开销几乎不变
- **天然隔离不串台**：没命中的 skill 正文根本不进上下文

### Skill Hub：从"能力"到"生态"

一旦"能力 = 一个可分发的文件"，就能像装包一样共享：社区/团队把 skill 发布到 **Skill Hub（技能市场）**，用户按需下载丢进目录即用。这带来质变：

- **复用**：写好的 `code-review`、`add-docstring` 等规范一次发布、人人可用，不必重复造轮子
- **协作生态**：贡献者持续发布、用户按需组合，Agent 的能力边界由"官方内置"变成"社区共建"
- **可移植**：同一份 skill 在任何遵循同一约定的 Agent 上都能跑，能力不再被单个产品绑死

> Skills 让单个 Agent 可扩展；**Skill Hub 让整个 Agent 生态可扩展**——这正是 Tool（要写代码、难以跨产品分发）很难做到的。

## 二、Skills vs Tool Call

这是本节最关键的一组对比。两者常被混淆，但定位完全不同：

| 维度 | Tool Call | Skill |
|---|---|---|
| 本质 | 一个**能执行的动作**（函数） | 一段**领域知识 / 工作规范**（文本） |
| 回答的问题 | Agent **能做什么**（read/write/bash…） | Agent 该**怎么做、按什么标准做** |
| 注入方式 | 函数签名 → JSON Schema，进 `tools` 参数 | Markdown 正文 → 拼进 prompt |
| 模型如何用 | 生成一次 `tool_call`，运行时执行并回填结果 | 当作"上文规范"阅读，指导后续所有输出 |
| 有无副作用 | 通常有（改文件、跑命令） | 没有，纯知识 |
| 扩展成本 | 写代码 + 注册 | 丢一个 `.md` 文件进目录 |

一句话概括：

> **Tool 是"手"，Skill 是"脑子里的规矩"。** 光有手不知道规矩会乱做；Skill 告诉手该按什么标准做。

### 换个角度：精准性 vs 扩展性

很多人会问："两者都是给 Agent 加能力，到底差在哪？"——差在这一对权衡：

| 维度 | Tool Call | Skill |
|---|---|---|
| **精准 / 确定性** | **高**：代码在运行时被真正执行，同输入同输出、副作用明确、可复现 | **较低**：只是文本，靠 LLM 读懂并"肯"遵守，可能被忽略或曲解 |
| **扩展性** | **差**：新增能力要写代码 + 注册 + 重新部署 | **好**：丢一个 `.md` 进目录即可，零代码、热插拔 |

为什么会这样，一句话点破：

> **Tool 用「执行」换确定性，Skill 用「不执行」换扩展性。**
> - Tool 的精准来自**代码被真正执行**（不经模型自由发挥）→ 确定，但每加一个能力都要改代码；
> - Skill 的扩展性来自**它只是文本、无需执行环境** → 随手加改，但是否照做取决于模型。

所以二者**不是替代、而是互补**：Skill 负责"该按什么标准做"，真正落地的动作仍由 Tool 执行。

有意思的是：**Skills 机制本身正是用两个 Tool 实现的**——`list_skills` / `load_skill`。也就是"用工具去加载知识"。下面就是原理。

## 三、SKILL.md 标准

每个 skill 是一个目录，目录里放一份 `SKILL.md`：**YAML frontmatter（元数据）+ Markdown 正文（完整规范）**。

```markdown
---
name: add-docstring
description: 给 Python 函数添加 Google 风格 docstring
---

# 使用规则

当用户要求"加注释/加文档/补 docstring"时，遵循以下规范：
- Google 风格，第一行简短描述（≤72 字符）
- Args / Returns / Raises 三段
```

| 字段 | 必填 | 作用 |
|------|------|------|
| `name` | ✅ | 唯一标识（= 目录名） |
| `description` | ✅ | 一句话摘要，注入到 system prompt 索引 |

> 更宽松的实现：没有 frontmatter 时，自动取正文第一个非标题非空行当作 brief。

## 四、Agent 实现 Skills 的原理（伪代码）

核心是**两级渐进式加载**：

```
Level 1（启动时，极省 token）：扫描目录 → 只拿 name + 一句话 brief → 注入 system prompt
Level 2（运行时，命中才付费）：加载某个 skill 的 SKILL.md 全文 → 注入上下文
```

### 4.1 SkillLoader —— 扫描 + 索引 + 按需读全文

关键点：**惰性扫描**（首次用到才做 IO）、**索引缓存**、**防目录穿越**。

```
类 SkillLoader:
    初始化(skills_dir):
        本.根目录  = 规范化绝对路径(skills_dir)
        本.索引    = 空            # 缓存，首次访问才填充
        本.名字表  = 空字典        # name → 实际目录

    # ---- Level 1：只读元数据，生成一句话索引 ----
    方法 列出索引():
        若 本.索引 为空:
            本.索引 = 扫描()       # 首次调用才真正扫盘
        返回 本.索引               # [(name, brief), ...]

    方法 扫描():
        结果 = 空
        对 根目录下每个子目录 child:
            若 child 内存在 SKILL.md:
                头部  = 只读前若干KB(child/SKILL.md)
                brief = 提取摘要(头部)          # frontmatter.description 或正文首行
                结果[child.name] = (child.name, brief)
                本.名字表[child.name] = child
            否则若 child 内存在 skills/ 子目录:   # 兼容嵌套 skill 包
                对 skills/ 下每个内层目录: 同上收录
        返回 按 name 排序(结果)

    # ---- Level 2：命中某个 skill 才读全文 ----
    方法 加载(name):
        校验名字合法(name)                        # 白名单，挡非法字符
        skill_dir = 本.名字表[name]
        断言 skill_dir 仍在 本.根目录 之内         # 防目录穿越
        全文 = 读文件(skill_dir/SKILL.md)
        返回 Skill(name, brief=提取摘要(全文), 全文)
```

### 4.2 把 Loader 暴露成两个 Tool

这样 **LLM 能自己决定何时加载哪个 skill**：

```
函数 注册skill工具(工具表, loader):

    工具 list_skills():
        「列出所有可用 skill（name + 一句话）。不确定有哪些能力时调用。」
        返回 逐行拼接("- {name}: {brief}"  取自  loader.列出索引())

    工具 load_skill(name):
        「按名字加载某个 skill 的完整规范（SKILL.md 全文）。」
        skill = loader.加载(name)
        返回 "# Skill: {skill.name}\n---\n{skill.全文}"

    工具表.注册(list_skills)
    工具表.注册(load_skill)
```

### 4.3 启动时把 Level 1 索引拼进 system prompt

```
函数 组装系统提示词(loader):
    索引 = loader.列出索引()
    若 索引为空:
        返回 基础系统提示词
    索引文本 = 逐行拼接("- **{name}**: {brief}"  取自 索引)
    # 模型开局就"知道有哪些 skill 可用"，但只花几十 token
    返回 基础系统提示词 + Skills索引模板(索引文本)
```

### 4.4 两条运行路径

**路径 A：LLM 自主加载（自动）**

```
system prompt 里已列出 skill 索引
用户："帮这个函数加 docstring"
  → LLM 判断命中 add-docstring
  → 主动调用工具: load_skill("add-docstring")
  → 拿到全文规范 → 按规范生成 docstring
```

**路径 B：用户显式指定（快捷指令）** —— 在调用 LLM **之前**本地拦截：

```
函数 预处理(用户输入, loader):
    若 用户输入 以 "/skills" 开头:          # 本地直接列出，不走 LLM
        返回 直接回复(格式化skill列表(loader))
    若 用户输入 以 "@" 开头:                # 语法：@name <任务>
        name, 任务 = 解析(用户输入)
        skill = loader.加载(name)
        # 把 skill 全文当作"前置规范"拼到任务前面，再送 Agent
        返回 改写("[按以下规范完成]\n{skill.全文}\n\n[任务]\n{任务}")
    返回 原样透传                            # 交给 Agent 正常处理
```

> 两条路径的取舍：**A 省心（LLM 自己判断）**，但多一次工具调用往返；**B 精准（用户点名）**，省往返但要用户知道 skill 名。二者可同时保留。

## 小结

- **Skill = 热插拔的领域规范包**，解决"多项目多规范"下 system prompt 膨胀 + 串台
- **Tool 是能力（动作），Skill 是知识（规范）**；而 Skills 机制本身用两个 Tool（`list_skills`/`load_skill`）实现
- 原理 = **两级加载**：启动只装索引（Level 1，省 token），命中才加载全文（Level 2，按需付费）
- 落地只需三块：`SkillLoader`（扫描/索引/读全文）+ 两个工具 + system prompt 注入索引
