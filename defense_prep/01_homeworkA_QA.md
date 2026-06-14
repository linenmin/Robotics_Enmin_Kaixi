# Homework A — 口试抽考卡（Defense Q&A Drill）

每题格式：**你写了啥 → 教授会问啥（英文，按真实口试）→ 答案（中文 + 英文术语）→ 陷阱。**
笔记链接见 `00_index_crossref.md` 的 legend。

---

## A-Q1 — 逆位置运动学：一个 / 两个 / 无穷个解
**你写了：** 3-DOF 臂（base yaw q1, shoulder pitch q2, elbow pitch q3）。边界点 → 1 个解（臂全伸直，elbow-up/down 合并 = singular）。一般可达点 → 2 个（elbow-up, elbow-down）。base 轴上的点 → ∞（q1 free）。
**笔记：** L1 › 模块一/模块二。

**Q: Why exactly one solution on the workspace boundary?**
A: 在外边界上臂完全伸直，two-link 平面子问题的目标落在最大可达半径的圆上。elbow-up 和 elbow-down 两个分支重合 → 单一（singular）构型。此处 IK Jacobian 掉秩（loses rank）。

**Q: Why infinitely many on the base rotation axis?**
A: 目标落在 base z-axis 上时，转动 q1 不改变 end-effector 位置。q1 变成 free/redundant 参数 → 一个单参数解族（1-parameter family）。

**Q: Generic point — why exactly two and not more?**
A: base yaw q1 由目标方位角唯一确定。剩下的平面 2-link 问题（q2,q3）恰好有两个解（law of cosines 给 ±elbow angle）。

**陷阱：** 别说「singular = 无解」。这里 singular 意思是分支*合并*（一个解）或某个 DOF 变*free*（无穷解）。把「singular」和「Jacobian loses rank」绑在一起说。

---

## A-Q2 — 滚动硬币到达任意构型
**你写了：** 状态 q=(x,y,φ,θ)。步骤：(1) 转向目标，滚到 (xg,yg)；(2) 原地转到 φg；(3) 闭环 maneuver（滚 L、转 π、滚 L、转 π）用 ±2L mod 2π 修正 rolling angle θ。理由：nonholonomic constraints 禁止*瞬时* sideways 运动，但不删除构型；闭环产生 otherwise-coupled 变量的净变化。停车类比。
**笔记：** L1 › 模块一：构型空间。

**Q: What is a nonholonomic constraint, precisely?**
A: 一个对速度的约束，*不可积*（not integrable）成对构型的约束 —— 即它限制瞬时运动方向，但整个 C-space 仍可达。rolling-without-slipping 是典型例子。

**Q: Why does the closed maneuver change θ but return x,y,φ?**
A: 出去 L 再回来 L（中间两个 π 转向）让 contact point 和 heading 复原，但总滚弧长 = 2L，所以 θ 累积 2L/r。选 L 使 2L/r ≡ Δθ (mod 2π)。

**Q: How do you know the full goal is reachable at all?**
A: nonholonomic 系统的可控性（Lie-bracket / 「停车」论证）：允许运动的组合张成 C 的切空间，所以任意构型可达，即使无法在一瞬间到达。

**陷阱：** 把「瞬时不能 sideways 移动」和「*能*到达 sideways-displaced 构型」说清楚 —— 这正是这题的核心。

---

## A-Q3 — 旋转矩阵 → exponential coordinates
**你写了：** tr(R)=0 ⇒ 1+2cosθ=0 ⇒ θ=2π/3；ω̂=(R−Rᵀ)/(2sinθ)；从 skew 矩阵读 ω；exponential coords ωθ。指出非唯一性：(−ω,−θ) 同一个旋转。
**笔记：** L1 › 模块二：刚体运动 — 旋转。

**Q: Derive tr(R)=1+2cosθ.**
A: Rodrigues: R = I + sinθ·ω̂ + (1−cosθ)·ω̂²。tr(I)=3, tr(ω̂)=0, tr(ω̂²)=−2（因 ‖ω‖=1）。所以 tr(R)=3+0−2(1−cosθ)=1+2cosθ。

**Q: What if sinθ = 0 (θ=0 or π)?**
A: 公式 ω̂=(R−Rᵀ)/(2sinθ) 失效（除以 0）。θ=0 → ω 无定义（identity rotation）。θ=π → R 对称，用 R=I+2ω̂²；从对角线提 ω：ωᵢ=±√((Rᵢᵢ+1)/2)。这是标准的 log-map 边界情况。

**Q: Why are exponential coordinates not unique?**
A: (ω,θ) 和 (−ω,−θ) 给同一个 R；θ 和 θ+2π 也是。你报告 principal value θ∈[0,π]。

**陷阱：** 他们爱问 sinθ=0 的情况。把 θ=π 分支准备好 —— 这是大多数人会忘的那个。

---

## A-Q4 — 点机器人路径规划（visibility graph + A*）
**你写了：** C-space = 2D（点机器人）。节点 = start + goal + 所有障碍顶点。segment collision-free 则连边，cost = Euclidean。A* 用 Euclidean heuristic。返回最短路径，长度 7.82。声称 complete + optimal，因为多边形间最短 collision-free 路径只在障碍顶点拐弯。
**笔记：** L5 › 模块四：搜索法; 模块一：基础概念。

**Q: Why is the optimal path guaranteed to be in the visibility graph?**
A: 对点机器人 + 多边形障碍，最短路径是分段直线，只能在凸障碍顶点改变方向（"taut string" / 拉紧的绳 论证）。所有这些拐点都是顶点，都是图节点 ⇒ 最优路径就是一条图上的路径。

**Q: Is your A* heuristic admissible? Why does that matter?**
A: 是 —— 直线 Euclidean distance 永不高估真实剩余路径长（triangle inequality），所以 A* 返回最优路径，且不会展开真实代价超过最优值的节点。

**Q: Complexity?**
A: 建图对 n 个顶点是 O(n²) 段-障碍检查（naive）；图上 A* 接近 Dijkstra。对这个小场景没问题。

**Q: What changes if the robot has size (not a point)?**
A: 把障碍按机器人半径膨胀（Minkowski sum / configuration-space obstacles），在膨胀后的 C-space 里规划。visibility graph 只对 点/多边形 情况干净有效。

**陷阱：** 区分 **complete**（有解必找到）和 **optimal**（找到最短）。你两个都声称了 —— 要能分别论证。还可能被问「如果障碍非凸/曲线呢？」→ 顶点论证失效；转到 PRM/RRT（L5 模块四）。
