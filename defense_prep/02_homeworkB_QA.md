# Homework B — 口试抽考卡（Defense Q&A Drill）

每题格式：**你写了啥 → 教授会问啥（英文）→ 答案（中文 + 英文术语）→ 陷阱。**
笔记链接见 `00_index_crossref.md` 的 legend。

---

## B-Q1 — Gaussian-mixture prior 在 linear-Gaussian 测量下的后验
**你写了：** Prior p(x)=0.5·N(x|−1,1)+0.5·N(x|1,0)；第二项 = degenerate Gaussian = x=1 处的 point mass。采样 10000（seed 42）：prior mean −0.008, std 1.229。测量 z=2x+ε, ε~N(0,0.3), z=0.5。Bayes: p(x|z)∝p(z|x)p(x)。后验：连续部分移向 x≈0.25，x=1 的 spike 还在但权重下降。后验 mean 0.303, std 0.390。结果是带一个 degenerate component 的 Gaussian mixture，**不是**单个 Gaussian。
**笔记：** L6 › 第16–19页 贝叶斯公式; 第46–47页 正态分布下的预测与贝叶斯更新。

**Q: Why is the posterior not a single Gaussian?**
A: prior 是个 *mixture*。Bayes 把每个 component 乘以同一个 likelihood，所以后验是重新加权的 mixture。只有 单 Gaussian prior × Gaussian likelihood 才得到单 Gaussian。

**Q: Where does x≈0.25 come from?**
A: likelihood 在 2x=z=0.5 ⇒ x=0.25 处取峰。宽的连续 component 从 −1 被拉向 0.25（prior mean 和 likelihood 的折中，按各自 precision 加权）。

**Q: What happens to the point mass at x=1, and why does its weight drop?**
A: point mass 在 Bayes 下仍是 point mass（support 是单点），但它的 mixture 权重被它的 likelihood p(z|x=1)=N(0.5|2,0.3) 重新缩放，这个值很小（2 离 0.5 远）。所以相对权重缩小。

**Q: Why sampling instead of closed form?**
A: degenerate component 让密度奇异（singular）；用采样（或解析+离散的混合处理）绕开写一个 ill-defined 的连续密度。连续部分*解析上*就是一个 Gaussian；只有 mixture 的记账用数值做。

**陷阱：** 要明确说 variance「0」= Dirac/point mass，这是对（可能是 typo 的）prior 的有意解释。说「I kept the statement as written and interpreted it as a degenerate Gaussian」。别让他们以为你忽略了它。

---

## B-Q2 — 平面内 end-effector 最大速度
**你写了：** Gram–Schmidt → 平面的 orthonormal basis E=[e1 e2]；平面内速度 y=Eᵀṗ=EᵀJ_p·q̇=A·q̇，A=EᵀJ_p。约束 ‖q̇‖₂≤1，把 unit ball 经 A 映射 → **ellipse**（由 SVD A=UΣVᵀ）。平面内最大速度 v_max=σ_max(A)=√λ_max(AAᵀ)。singularity 时 ellipse 退化成线段/点。
**笔记：** L3b › 模块四 伪逆理论与SVD（P.24–44）; 模块一 几何雅可比。

**Q: Why is the reachable velocity set an ellipse?**
A: 它是 unit ball {‖q̇‖≤1} 在线性映射 A 下的像。SVD：Vᵀ 转动 ball（仍是 ball），Σ 沿不同轴不同缩放（ball→ellipsoid），U 转到输出平面。ball 的线性像 = ellipse/ellipsoid。这就是 **manipulability ellipsoid**。

**Q: Why is the max exactly σ_max?**
A: max over ‖q̇‖≤1 of ‖Aq̇‖ 就是 A 的 operator 2-norm = 最大 singular value。最优 q̇ 是 right singular vector v₁；输出是 σ₁u₁（major semi-axis）。

**Q: Why √λ_max(AAᵀ)?**
A: A 的 singular values = AAᵀ 特征值的平方根。所以 σ_max=√λ_max(AAᵀ)。（用 AᵀA 也行 —— 非零特征值相同。）

**Q: Role of Gram–Schmidt? Why orthonormal?**
A: 为了把平面内速度表示在一个 2D orthonormal frame 里，使 ‖ṗ_Π‖=‖y‖（保模长）。若不 orthonormal，坐标范数不等于物理速度。

**Q: What at a singular configuration?**
A: J_p 在某方向掉秩 ⇒ A 的某个 singular value 变 0 ⇒ ellipse 塌成线段（或点）。机器人沿该方向无法产生平面内速度。

**陷阱：** 「只用 linear algebra，不需要 optimization」—— 可能被追问为什么。答：因为线性映射在 ball 上的最大值*解析上*就是 top singular value；不需要迭代求解器。

---

## B-Q3 — 惯性参数变换与 physical realizability
**你写了：** 10-vector μ=[m, mc_x, mc_y, mc_z, I_xx, I_xy, I_xz, I_yy, I_yz, I_zz]ᵀ。a→b 变换：mass 不变；c_b=(ᵃR_b)ᵀ(c_a−ᵃp_b)；inertia 经 parallel-axis 到 CoM → rotate → parallel-axis 回去：I_cb=(ᵃR_b)ᵀ·I_ca·ᵃR_b，其中 I_ca=I_a−m[c_a]ₓᵀ[c_a]ₓ。Realizable 当且仅当：m>0；I_c symmetric；I_c≻0 (SPD)；主惯量满足 triangle inequalities I₁+I₂≥I₃ 等。复合刚体：μ 相加（在同一 frame）。
**笔记：** L6 › 第72–80页 动力学对质量参数的线性性; 第81–86页 参数辨识与可实现性。

**Q: Why shift inertia to the CoM *before* rotating, then shift back?**
A: rotation law I'=RᵀIR 只对*同一点*的 inertia 成立。I_a 是关于 frame-a origin 的，不是 CoM。parallel-axis 把它移到 CoM（与转动点无关），在那转动，再 parallel-axis 移到 frame-b origin。跳过这步会得到错的 I_b。

**Q: Why are the triangle inequalities needed on top of SPD?**
A: SPD 保证 rotational kinetic energy 为正，但一个矩阵可以 SPD 却仍不对应真实质量分布。真实刚体的主惯量满足 I₁+I₂≥I₃（及轮换），因为每个 I=∫(dist²)dm 在非负质量密度上积分。这是比 SPD 更强的物理条件。

**Q: Why is dynamics *linear* in μ?**
A: 运动方程（Newton–Euler / regressor 形式）可写成 τ=Y(q,q̇,q̈)·μ，Y 是 regressor，μ 是惯性参数。正是这个线性性让 least-squares 参数辨识成为可能。

**Q: Composite body — when can you just add μ?**
A: 仅当两个 μ 表示在*同一* frame。mass、first moment mc、inertia 关于同一 origin 都是可加的。不同 frame → 先变换（part a），再相加。

**陷阱：** 别把「inertia about origin」和「inertia about CoM」混了。每步 parallel-axis 都要点明参考点。grader 会查你有没有直接转动 I_a。

---

## B-Q4 — 自然 vs 人工约束（peg / plane / wedge）
**你写了：** ideal contact（frictionless, infinitely stiff）⇒ reciprocity wᵀt=τᵀω+Fᵀv=0。每个情形选 task frame，列 **natural constraints**（环境强加：某些 v/ω 和互补的 F/τ 为零）和 **artificial constraints**（controller 在互补分量上设定）。Peg: z=insertion。Plane: z=normal。Wedge（line contact）：产生 τ_x 但不产生 τ_y, τ_z。用 t_o=Ad_T·t, w_o=Ad_T⁻ᵀ·w 证明 reciprocity 与 frame 无关。
**笔记：** L3c › 模块一：接触约束理论。

**Q: What does reciprocity wᵀt=0 physically mean?**
A: ideal contact 既不储能也不耗能，所以 contact wrench 对 admissible twist 不做功。数学上 admissible twist 空间和 admissible wrench 空间是 *reciprocal* 的（在 twist–wrench 配对下正交）。

**Q: Why does each direction split into exactly one natural + one artificial constraint?**
A: 6 DOF。每个方向上环境约束*要么*运动*要么*力（reciprocity 禁止同时约束两者，你也不能两者都留 free）。Natural = 环境固定的；artificial = controller 在互补变量上命令的。6 natural + 6 artificial。

**Q: Wedge — why τ_x but not τ_y or τ_z?**
A: 沿 y_t 的 line contact。点 r=(0,s,0) 处的 normal force F_z 给力矩 r×F=(s·F_z,0,0) → 只有 τ_x。法向力沿线分布可累成净 τ_x；没有机制产生 τ_y 或 τ_z（frictionless ⇒ 无切向力、无绕法向的力矩）。

**Q: Why is reciprocity frame-independent?**
A: w_oᵀt_o=(Ad_T⁻ᵀ·w_t)ᵀ(Ad_T·t_t)=w_tᵀ·Ad_T⁻¹·Ad_T·t_t=w_tᵀt_t。Ad 和它的 inverse-transpose 抵消。物理关系在任意 object-attached frame 变换下不变。

**陷阱：** frictionless 在你的约束里起了实质作用（F_z=0 切向、τ_z=0 绕法向）。如果他们改成「有摩擦」，你的 natural-constraint 表会变 —— 要能说出哪几项会动。
