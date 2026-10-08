# 讲义插图 · AI 生图 Prompt 速查

> 本目录里 1.6–1.9 MB 的 PNG 都是 AI 生成的"水彩纸感手绘风"教学插图。
> 统一画面元素：**牛皮纸/旧纸张水彩底色**、**黑色手写体大标题**、**小男孩 + 龙虾 NPC 出演**、**黑字白底气泡或便签**、右下角小字"图片由 AI 生成"水印。
> 下面两张图等待生成，文件名已在对应 markdown 里占好位。

---

## 1. `06-chatbot-vs-agent-swimlane.png`

**用途**：第 5 节《Agent vs Chatbot》的时序泳道图，用画面表达 Chatbot（4 步直线）vs Agent（循环里反复调工具）的差异。

**画布建议**：横向 16:9，1920×1080 或更高。

### 中文 prompt

```
一张教学插图，水彩牛皮纸质感背景，手绘风格，整张图横向分成左右两个并排的"时间泳道"：

左侧泳道顶部用黑色手写体大字写："Chatbot · 4 步走完"。
左侧画面从上往下 4 个步骤，每步用一根细黑色手绘箭头连接：
  1. 一个穿黄色 T 恤的小男孩举手提问，旁边白底黑字气泡写"问题"。
  2. 一只可爱的橘红色小龙虾（程序）双钳举起 messages 信封。
  3. 一只戴眼镜的猫头鹰（LLM）从云朵里冒出来，吐出一张白色便签"回答"。
  4. 龙虾把便签递给小男孩。
左侧泳道底部一行小字："一次问答就结束"。

右侧泳道顶部黑色手写体大字写："Agent · 循环里反复调"。
右侧画面中央画一个粗黑色虚线大圆圈，圈上方写"loop 直到不再要工具"，圆圈里逆时针排布 4 个手绘小图标：
  - 龙虾递信封给猫头鹰（chat with tools）
  - 猫头鹰吐出一张写着"tool_calls"的便签
  - 龙虾跑去敲打一把扳手图标的工具箱（执行工具）
  - 一张白底便签写"role=tool 结果"被塞回信封堆
圆圈外右下角，龙虾把最终答案便签递给小男孩，旁边气泡写"交付最终回答"。
右侧泳道底部一行小字："多回合 · 多工具"。

整张图顶部居中用最大号黑色手写体写主标题："有 loop 才是 Agent"。
底部居中小字副标题："差别不在模型多大，而在程序有没有循环"。
右下角浅灰小字水印："图片由 AI 生成"。

整体配色温暖，限定使用：牛皮纸米色背景、橘红（龙虾）、米黄（小男孩 T 恤）、淡蓝（左侧泳道底色）、淡橙（右侧泳道底色）、黑色描边。文字必须清晰可读，不要英文乱码。
```

### English prompt（备用）

```
A hand-drawn educational illustration on a watercolor kraft-paper background, landscape 16:9. The canvas is split vertically into two parallel "time lanes":

LEFT LANE — title in bold black handwritten Chinese: "Chatbot · 4 步走完".
Four steps top-to-bottom connected by thin hand-drawn black arrows:
  1) A boy in a yellow T-shirt raises his hand, white speech bubble "问题".
  2) A cute orange-red lobster (the program) holds up a "messages" envelope.
  3) An owl with glasses (the LLM) pops from a cloud, dropping a white sticky note "回答".
  4) The lobster hands the sticky note back to the boy.
Footer small text: "一次问答就结束".

RIGHT LANE — title: "Agent · 循环里反复调".
Center: a thick black dashed circle labeled "loop 直到不再要工具", with 4 hand-drawn icons going counter-clockwise inside:
  - lobster hands envelope to owl (chat with tools)
  - owl returns a sticky note "tool_calls"
  - lobster hammers a wrench/toolbox icon (execute tool)
  - sticky note "role=tool 结果" gets appended to the envelope stack
Outside the circle, bottom-right: lobster hands a final answer note to the boy, bubble "交付最终回答".
Footer small text: "多回合 · 多工具".

Top center main title in the largest black handwritten Chinese font: "有 loop 才是 Agent".
Bottom center subtitle: "差别不在模型多大，而在程序有没有循环".
Bottom-right small grey watermark: "图片由 AI 生成".

Warm palette: kraft-paper beige background, orange-red lobster, mustard yellow shirt, soft blue tint on left lane, soft orange tint on right lane, all outlines in black. All Chinese text must be crisp and readable, no garbled glyphs.
```

---

## 2. `10-tool-calling-extensions.png`

**用途**：第 9 节《Tool Calling 的三个扩展面》——把 MCP / Skill / RAG 三种工具来源贴到第 8 节的最小循环上。

**画布建议**：横向 16:9，1920×1080。

### 中文 prompt

```
一张教学插图，水彩牛皮纸质感背景，手绘风格，横向布局。

画面正中央：一只戴眼镜的猫头鹰（LLM）站在云朵上，前方一只橘红色小龙虾（程序）举着 messages 信封问它"chat with tools"。猫头鹰头顶飘出一张白底便签写"tool_calls"，下方一条手绘黑色虚线大箭头指向一个菱形手写体大字标签："走哪条路？"。

从菱形岔出三条平行的手绘黑色弯线，分别指向画面下方并排排列的三个"工具来源摊位"，每个摊位都是一张牛皮纸卡片，顶部一行手写黑字大标题：

  ① 左侧 · 淡蓝色卡片，标题 "Local · 本地 @tool"。
     画面：小龙虾从自己围裙口袋掏出一把手绘扳手。
     副标题小字："写死在代码里"。

  ② 中间 · 米黄色卡片，标题 "MCP · 远程工具"。
     画面：一只穿邮差服的小章鱼站在远处的木牌"MCP Server"旁，
     伸出触手通过一根虚线电话线把扳手递过来。
     副标题小字："工具协议化 · 可插拔"。

  ③ 右侧 · 淡绿色卡片，标题 "RAG · 检索工具"。
     画面：一只戴书生帽的小乌龟从一摞书堆里捧出一张"向量片段"便签。
     副标题小字："私有知识查出来塞进 prompt"。

三个摊位下方各画一根细黑色弯箭头汇合到同一个手绘信封堆，
信封堆上方手写小字 "messages.append(role=tool)"，
再一根大箭头回到最上面的猫头鹰，形成闭环。

画面右上角额外画一个粉色礼物盒，盒盖打开里面探出三样东西（一把扳手、一卷羊皮卷、一张便签），盒身手写黑字 "Skill 包"，
一根手绘虚线箭头从礼物盒指向猫头鹰头顶的云朵，旁边小字注释 "注入 system prompt + 注册多个 tool"。

顶部居中用最大号黑色手写体主标题："工具的三种来源 · 协议没变"。
底部居中小字副标题："MCP / RAG 是工具的另一种来源 · Skill 是工具+提示词的打包"。
右下角浅灰小字水印："图片由 AI 生成"。

配色：牛皮纸米色背景、橘红龙虾、淡蓝/米黄/淡绿三色摊位、粉色 Skill 礼物盒、黑色手绘描边。所有中文文字必须清晰可读。
```

### English prompt（备用）

```
A hand-drawn educational illustration on watercolor kraft-paper background, landscape 16:9.

CENTER: an owl with glasses (the LLM) stands on a cloud. A small orange-red lobster (the program) holds up a "messages" envelope, captioned "chat with tools". A white sticky note "tool_calls" drifts above the owl, with a thick black dashed arrow pointing down to a diamond handwritten label: "走哪条路？".

Three parallel hand-drawn curved arrows fan out from the diamond to three "tool source booths" arranged in a row at the bottom, each booth is a kraft-paper card with a handwritten title:

  ① Left, soft blue card, title "Local · 本地 @tool".
     Scene: lobster pulls a hand-drawn wrench out of its apron pocket.
     Subtitle: "写死在代码里".

  ② Middle, mustard-yellow card, title "MCP · 远程工具".
     Scene: a small octopus dressed as a postman stands near a wooden sign "MCP Server", extending a tentacle through a dashed telephone wire to hand over a wrench.
     Subtitle: "工具协议化 · 可插拔".

  ③ Right, soft green card, title "RAG · 检索工具".
     Scene: a small turtle with a scholar's cap pulls a "向量片段" sticky note from a stack of books.
     Subtitle: "私有知识查出来塞进 prompt".

Below the three booths, thin black arrows converge into a single envelope stack labeled "messages.append(role=tool)", then a big arrow loops back up to the owl, forming a closed circle.

TOP-RIGHT EXTRA: a pink gift box, lid open, with three items poking out (a wrench, a scroll, a sticky note); the box reads "Skill 包". A dashed arrow points from the box to the owl's cloud, with annotation "注入 system prompt + 注册多个 tool".

Main title at top center, largest black handwritten Chinese: "工具的三种来源 · 协议没变".
Subtitle at bottom center: "MCP / RAG 是工具的另一种来源 · Skill 是工具+提示词的打包".
Bottom-right grey watermark: "图片由 AI 生成".

Palette: kraft beige background, orange-red lobster, soft blue / mustard / soft green booths, pink Skill gift box, black hand-drawn outlines. All Chinese text crisp and readable.
```

---

## 使用步骤

1. 拷上面的中文 prompt 到同款生图工具（GPT-4o image / Nano Banana / Midjourney v6 等）。
2. 若一次出图字体不清晰，可加固定提示："Chinese handwritten font must be crisp, no garbled glyphs, no English mixed in"。
3. 生成 1600×1100 或更大尺寸的 PNG，保存为：
   - `images/06-chatbot-vs-agent-swimlane.png`
   - `images/10-tool-calling-extensions.png`
4. 直接替换占位即可，markdown 引用路径已写好。

> 旧的 `06-chatbot-vs-agent-swimlane.mmd`（mermaid 源）可以保留作为"信息源参考"，也可以删除。
