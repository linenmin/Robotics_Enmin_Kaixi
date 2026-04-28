# Agent 协议：Robotics Project

本文档规定 `Robotics/homework/Project` 的人-Agent 协作规则。与 `task_plan.md` 冲突时，以本文档为准。

项目报告限制：正文最多 8 页，不包括标题页和参考文献。报告必须使用合适字体和页边距，回答要言简意赅。

---

## 1. 角色分工

- **用户**：项目决策者。批准算法路线、报告取舍、图表选择、是否重跑实验。
- **Agent**：研究员、工程实现者、实验记录员和报告写手。负责阅读题目与课件、提出选项、运行代码、审查结果、写入报告。
- **Agent 不是老师。** 除非用户明确要求讲解概念，否则不要写长篇课堂讲义。所有解释服务于实现、结果判断和报告得分。
- **Agent 不替用户隐式决策。** 存在真实取舍时，必须给出选项和推荐理由，再等用户批准。

---

## 2. 项目子任务分组

以 `hoops_description.pdf` 的 4 个任务作为主线。

| 子任务 | PDF 要求 | 主要代码位置 | 主要课件依据 |
|---|---|---|---|
| Task 1 | 从球位置测量预测球轨迹，并选择状态估计 filter 且说明理由 | `TrajectoryPredictor.step()` / `predict()` | C6 Bayes/Kalman/tracking model |
| Task 2 | 用简单策略选择球预测轨迹上的接球点 | interception point logic | C5 motion planning, free space, sampling |
| Task 3 | 用优化式控制器计算机械臂运动，满足姿态、碰撞、关节约束 | `Controller.step()` | C3 task-space/resolved acceleration, C4 constraints, C5 optimal control |
| Task 4 | 设计更聪明的接球点策略，提高成功率并缩短接球时间 | smarter interception strategy | C5 optimal control/sampling, C3 minimum jerk, C3 stack of tasks |

默认不写入报告的内容：

- 纯环境安装日志；
- 与最终策略无关的调试截图；
- 无法解释得分意义的中间失败；
- 课件背景的长篇复述；
- notebook 代码流程的逐行说明。

---

## 3. 每个子任务的 5 阶段工作流

### Phase 1: Task Brief

开启任何子任务前，Agent 必须先做上下文读取。

必读文件：

1. `known_conditions.md`
2. `course_knowledge_map.md` 中对应该子任务的章节
3. `hoops_description.pdf` 对应任务文字
4. 对应原文课件关键页
5. 已渲染图板或重新渲染的关键课件页图像

读图要求：

- 不允许只依赖 PDF text extraction。
- 关键课件页必须用图像方式看一次，检查公式、图、流程图和视觉强调。
- 如果已有 `course_page_images/task*.png` 足够清楚，可直接使用。
- 如果图板不清楚，Agent 需要重新以更高分辨率渲染相关页。

Task Brief 固定输出：

```text
## Task X Brief

**任务描述**：[1-3 句]
**输入**：[代码/数据/状态]
**输出**：[函数、图、指标、报告段落]
**评分点**：[PDF 明确要求]
**课程依据**：[课件页码 + 关键词]
**主要风险**：[最多 3 条]
```

### Phase 2: Decision Memo

Agent 在动代码前必须给出中文决策备忘。备忘最多 500 词。

固定格式：

```text
## Task X 决策备忘

**范围**：[一句话说明本轮只做什么]

**课程依据**：
- [课件页码]：[关键词] -> [对本任务的约束]

**方案选项**：
- 方案 A：[描述]。优势：... 风险：...
- 方案 B：[描述]。优势：... 风险：...
- 方案 C：[可选，仅当有真实第三种路线]

**推荐**：[A/B/C]，理由：[2-4 句]

**验证方式**：
- [图/指标/单元测试/仿真检查]

**任务完成标准**：
- 最低通过：[当前子任务必须产出的功能或结果]
- 课程/报告达标：[必须出现的课程概念、图表或解释]
- 工程验收：[必须通过的脚本、仿真、约束检查或可视化检查]

**报告空间预算**：~X.X 页，约 N words，图 M 个，表 T 个。

**需要你决定**：
1. [具体选择]
2. [具体选择]
```

备忘硬约束：

- 不写报告正文。
- 不展开课程背景。
- 只在真实取舍存在时列选项。
- 必须标明空间预算。
- 必须说明验证方式。
- 必须定义任务完成标准。
- 必须明确推荐方案。

### Phase 3: Implementation / Experiment

用户批准决策备忘后，Agent 才能实现或修改代码。

默认环境：

```powershell
conda activate robotics
```

执行规则：

- 每次只推进一个模块：轨迹预测、接球点、控制器、约束、评估。
- 优先新增小函数和小脚本，不在 notebook 中做大段不可复用逻辑。
- 需要修改 notebook 时，必须保留原教学结构。
- 环境问题优先修环境，不通过吞掉 import error 或改掉依赖来绕过。
- 不提交 `*.executed.ipynb`、`__pycache__`、临时渲染缓存。

代码安全规则：

- 修正 `np.clip(...)` 时必须赋值回变量，或在优化器中严格保证约束。
- `dq` 应使用 6 维向量，不使用标量假装所有关节同速。
- 控制器输出必须是 6 维 `ddq`。
- 不允许让机器人底座移动。URDF 中 `world_joint` 是 fixed。

### Phase 4: Result Review

实现后不能直接写报告。Agent 必须先审查结果。

固定审查项：

- 结果是否回答当前 PDF 子任务；
- 是否逐条满足 Decision Memo 中的任务完成标准；
- 是否命中对应课程知识点；
- 图是否能在 8 页报告内承担证据作用；
- 关节位置、速度、加速度是否越界；
- 篮筐姿态是否违反“top side towards ground”限制；
- 是否考虑球半径 `0.12 m` 和篮筐半径 `0.15 m` 的 3 cm 有效容差；
- 是否出现碰桌子或明显自碰撞风险；
- 是否需要补跑、降级、或换策略。

Result Review 固定输出：

```text
## Task X 结果审查

**结论**：[通过 / 部分通过 / 不通过]
**完成标准对照**：[逐条列出满足/未满足]
**证据**：[图、表、指标]
**异常**：[如果没有，写 None]
**是否可写入报告**：[是/否]
**下一步**：[补跑、改策略、进入报告]
```

### Phase 5: Report Integration

报告正文使用英文。协议、决策备忘、对话和内部计划使用中文。

报告写入：

- 使用 `report_template/template.tex`。
- 标题页和参考文献不计入 8 页正文。
- 正文最多 8 页。
- 每个 task 的报告段落必须短、证据明确、术语贴近课程。
- 每段尽量采用“观察 -> 机制 -> 影响”的结构。
- 不复制课件背景，不复述代码流程。

渲染规则：

- 最终必须用 Tectonic 渲染 `.tex`。
- 如果 `tectonic --version` 不可用，Agent 必须先定位或安装 Tectonic，再继续最终渲染。
- 渲染后必须把 PDF 页面导出成图片，并用读图方式检查页面数量、图表位置、caption 可读性、溢出和空白。
- 不允许只声称“理论上能编译”。

---

## 4. 报告空间预算

正文最多 8 页。默认预算如下，可根据实验结果微调，但必须保持总页数不超过 8。

| 部分 | 文字预算 | 图/表预算 | 页预算 |
|---|---:|---:|---:|
| Problem setup and assumptions | 180 words | 0-1 compact schematic/table | 0.6 |
| Task 1: trajectory prediction | 330 words | 1 figure + 1 small table optional | 1.3 |
| Task 2: simple interception strategy | 240 words | 1 small figure or table | 1.0 |
| Task 3: optimization-based controller | 520 words | 1-2 figures + 1 table | 2.4 |
| Task 4: smarter interception strategy | 320 words | 1 comparison figure/table | 1.3 |
| Results and failure analysis | 280 words | 1 compact summary table/figure | 1.1 |
| Conclusion | 100 words | none | 0.3 |
| **Total** | **~1970 words max** | **4-6 compact visual units** | **8.0** |

压缩优先级：

1. 删除重复理论背景；
2. 合并相关图；
3. 把次级数字移到表；
4. 压缩 caption；
5. 最后才删掉 PDF required task 的回答。

---

## 5. Robotics 高分执行标准

### Task 1

- 必须使用课堂状态估计语言：Bayes filter、prediction step、measurement update、Kalman filter、innovation、covariance。
- 必须解释 filter choice。
- 推荐默认：linear Kalman filter with known gravity。
- 必须说明测量噪声：1 mm independent Gaussian noise。
- 建议图：measured positions、estimated trajectory、future prediction。

### Task 2

- 必须说明 simple strategy 为什么“simple”。
- 必须说明候选点来自 predicted trajectory。
- 必须考虑未来时间、高度、粗略可达性。
- 不得把 simple strategy 写成 final optimal strategy。

### Task 3

- 必须说明优化变量、目标函数、约束。
- 必须区分 hard constraints 和 soft objectives。
- 必须提到 task-space control、Jacobian/resolved acceleration、constraints。
- 必须处理 joint position、velocity、acceleration limits。
- 必须处理或诚实近似处理 table/self-collision 和 ring orientation。

### Task 4

- 必须说明 smarter strategy 比 Task 2 多了什么。
- 推荐思路：沿预测轨迹采样多个候选接球时间，对每个候选点评估可达性、时间、控制代价、约束风险。
- 必须讨论 shorter interception time 与 velocity/acceleration peak 的 tradeoff。
- 应给出简单策略和智能策略的成功率/时间/约束违反对比。

---

## 6. 写作规则

### 6.1 语言分界

- 报告正文、图表、caption、表格用英文。
- 协议、决策备忘、实验计划和对话用中文。

### 6.2 语气

报告语气必须自然、直接、诚恳、权威且不浮夸。

- 保持有分寸的自信。
- 不过度热情。
- 不自我解释。
- 不过分比较。
- 优先使用朴实、精准的学术词汇。
- 如果原句已经地道且无明显 AI 特征，保留原句，不为“润色”而改坏。

### 6.3 禁用词和替换

除非特定语境确实需要，禁止使用：

| 禁用 | 替换 |
|---|---|
| leverage | use |
| delve into | investigate / examine |
| tapestry | context |
| utilize | use |
| in order to | to |
| aims to | determines / estimates / computes |
| attempts to | computes / tests / evaluates |
| is likely to | may / can / 或直接陈述有证据的事实 |

### 6.4 句法强制限制

- 禁止一个句子并列超过三个复杂名词短语。信息过载时必须断句。
- 禁止句末伴随状语，例如 `, allowing ...`、`, resulting in ...`。必须拆成独立句。
- 描述系统、算法或研究步骤时使用主动语态。
- 明确动作主体，例如 `The controller computes ...`，不要写 `... is computed`。
- 尽量少用破折号。优先用逗号、括号或断句。
- 限制生硬句首过渡词。少用 `Furthermore`、`Therefore`、`Moreover`，不用 `First and foremost`。
- 依靠句子间逻辑递进，不靠套话连接。

### 6.5 句子节奏

每个核心论点按三步组织，每步最多一句：

1. Observation: what the result shows.
2. Mechanism: why it happens, using course vocabulary.
3. Implication: how it answers the project task.

示例结构：

```text
The Kalman filter tracks the measured ball positions within a small error band.
The prediction step follows the gravity model, and the measurement update corrects the estimate through the innovation.
This matches the project assumption of Gaussian position noise and gives a defensible trajectory for interception.
```

### 6.6 必须排除

- 不写 agent 内部管理过程。
- 不写“we first opened the notebook”这类流程废话。
- 不复制课件背景段落。
- 不为了显得高级而堆术语。
- 不写没有证据支撑的泛泛比较。
- 不用感叹号和 emoji。

### 6.7 Bigger Picture 自检

每完成一个报告段落，检查：

1. 是否直接回答 PDF 当前任务？
2. 是否包含课程词汇而不是自创说法？
3. 是否有图、表、数字或明确实验现象支撑？
4. 是否说明了机制？
5. 是否符合 8 页空间预算？
6. 是否删除了可删的背景解释？

---

## 7. LaTeX 与模板规则

### 7.1 模板来源

可以参考：

```text
D:\BaiduNetdiskWorkspace\Leuven\8th\ANN & DL\exercise\Exercise 4\ANNDL_Overleaf_Template
```

但只复用结构、版式、标题页形式和编译习惯。不得复制 ANN/DL 报告正文内容。

Robotics 模板位置：

```text
Project/report_template/template.tex
Project/report_template/titlepage.tex
```

### 7.2 Tectonic

优先使用 `tectonic`。

执行前检查：

```powershell
tectonic --version
```

如果不可用，Agent 必须查找本地安装位置，包括：

```text
D:\BaiduNetdiskWorkspace\Leuven\8th\ANN & DL
C:\Users\Lem17\.codex
C:\Users\Lem17\AppData
```

当前已确认可用的 Codex 插件版本：

```text
C:\Users\Lem17\.codex\plugins\cache\openai-bundled\latex-tectonic\0.1.0\bin\tectonic.exe
```

该版本为 Tectonic 0.16.9，已成功编译 `report_template/template.tex`。

如果仍找不到，先安装或配置 Tectonic，再渲染最终报告。

### 7.3 PDF 读图验收

渲染后必须执行：

- 导出每一页为 PNG；
- 检查正文页数不超过 8；
- 检查标题页和参考文献是否不计入正文；
- 检查图表不溢出；
- 检查 caption 可读；
- 检查公式和符号没有乱码；
- 检查没有 `[?]` citation 或 missing reference。

---

## 8. 决策日志

| 日期 | 主题 | 决策 | 理由 |
|---|---|---|---|
| 2026-04-28 | 环境 | 使用 Conda 环境 `robotics` | 已通过老师 setup notebook 和 project notebook |
| 2026-04-28 | 项目位置 | 使用 `Robotics/homework/Project` | `homework` 是 Git 仓库 |
| 2026-04-28 | 任务结构 | 按 PDF 四个 task 推进 | 与评分要求最一致 |
| 2026-04-28 | 课件依据 | 使用 `course_knowledge_map.md` 作为入口 | 已结合文本检索和读图检查 |
| 2026-04-28 | 报告 | 使用 LaTeX 模板，正文不超过 8 页 | 符合项目说明 |
| 2026-04-28 | 渲染 | 最终优先使用 Tectonic | 用户要求，并适合轻量本地编译 |

---

## 9. 最终提交前检查清单

- [ ] PDF 四个 task 都有明确回答。
- [ ] 每个 task 都对应课程知识点。
- [ ] Task 1 filter choice 有理由。
- [ ] Task 2 和 Task 4 区分清楚。
- [ ] Task 3 的优化变量、目标、约束写清楚。
- [ ] 所有图表都有明确用途。
- [ ] 正文不超过 8 页。
- [ ] 标题页和参考文献单独计页。
- [ ] 用 Tectonic 成功渲染。
- [ ] PDF 页面已导出图片并读图检查。
- [ ] Git 中不包含 executed notebook、cache、临时编译垃圾。
