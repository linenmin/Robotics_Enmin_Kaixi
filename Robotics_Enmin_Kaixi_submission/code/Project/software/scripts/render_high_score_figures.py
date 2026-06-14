import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SOFTWARE_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = SOFTWARE_DIR.parent
if str(SOFTWARE_DIR) not in sys.path:
    sys.path.insert(0, str(SOFTWARE_DIR))


def render_figures(benchmark_path: Path, task2_plot: Path, mesh_side_plot: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    benchmark_figure = output_dir / "figure_strategy_benchmark.png"
    side_by_side_figure = output_dir / "figure_task2_task4_side_by_side.png"
    geometry_figure = output_dir / "figure_hoop_geometry_definition.png"
    pareto_figure = output_dir / "figure_candidate_pareto.png"
    failure_figure = output_dir / "figure_failure_velocity_diagnostics.png"
    _render_strategy_benchmark(benchmark, benchmark_figure)
    _render_side_by_side(task2_plot, mesh_side_plot, side_by_side_figure)
    _render_hoop_geometry(geometry_figure)
    _render_candidate_pareto(benchmark, pareto_figure)
    _render_failure_velocity_diagnostics(benchmark, failure_figure)
    return benchmark_figure, side_by_side_figure, geometry_figure, pareto_figure, failure_figure


def _render_strategy_benchmark(benchmark: dict, output_path: Path):
    rows = benchmark["strategy_rows"]
    strategies = ["simple_geometric", "latest_nlp_feasible", "earliest_nlp_feasible", "smart_cost"]
    labels = ["simple", "late\nfeasible", "time-first\nfeasible", "balanced\ncost"]
    colors = ["#9aa0a6", "#CC79A7", "#0072B2", "#E69F00"]
    summary = benchmark["summary"]

    fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.2), constrained_layout=True)
    fig.patch.set_facecolor("white")

    success_rates = [summary[strategy]["success_rate"] for strategy in strategies]
    axes[0, 0].bar(labels, success_rates, color=colors)
    axes[0, 0].set_ylim(0, 1.05)
    axes[0, 0].set_ylabel("success rate")
    axes[0, 0].set_title("Hoop-crossing success")
    for index, value in enumerate(success_rates):
        axes[0, 0].text(index, value + 0.03, f"{value:.2f}", ha="center", va="bottom", fontsize=10)

    _boxplot_metric(axes[0, 1], rows, strategies, labels, colors, "catch_time_s", "successful catch time [s]", only_success=True)
    _boxplot_metric(axes[1, 0], rows, strategies, labels, colors, "radial_error_m", "hoop radial error [m]", only_success=True)
    axes[1, 0].axhline(0.03, color="black", linestyle="--", linewidth=1.2, label="effective tolerance")
    axes[1, 0].legend(loc="upper right", fontsize=9)
    _boxplot_metric(axes[1, 1], rows, strategies, labels, colors, "max_abs_ddq", "max joint acceleration [rad/s^2]", only_success=True)
    axes[1, 1].axhline(2.0, color="black", linestyle="--", linewidth=1.2, label="limit")
    axes[1, 1].legend(loc="upper right", fontsize=9)

    for ax in axes.ravel():
        ax.grid(axis="y", alpha=0.25)
        ax.tick_params(labelsize=10)
        ax.title.set_fontsize(11)
        ax.xaxis.label.set_fontsize(10)
        ax.yaxis.label.set_fontsize(10)

    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def _boxplot_metric(ax, rows, strategies, labels, colors, key, ylabel, only_success: bool):
    values = []
    shown_labels = []
    shown_colors = []
    for strategy, label, color in zip(strategies, labels, colors, strict=True):
        selected = [row for row in rows if row["strategy"] == strategy and (row["success"] or not only_success)]
        data = [row[key] for row in selected if row.get(key) is not None and np.isfinite(row[key])]
        if data:
            values.append(data)
            shown_labels.append(label)
            shown_colors.append(color)
    box = ax.boxplot(values, tick_labels=shown_labels, patch_artist=True, widths=0.55)
    for patch, color in zip(box["boxes"], shown_colors, strict=True):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)
    ax.set_ylabel(ylabel)


def _render_side_by_side(task2_plot: Path, mesh_side_plot: Path, output_path: Path):
    left = Image.open(task2_plot).convert("RGB")
    right = Image.open(mesh_side_plot).convert("RGB")
    target_height = 860
    left = _resize_to_height(left, target_height)
    right = _resize_to_height(right, target_height)
    width = left.width + right.width + 36
    height = target_height + 70
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    font = _font(28)
    draw.text((18, 14), "(a) Predicted trajectory and Task 2 candidate filtering", fill="black", font=font)
    draw.text((left.width + 54, 14), "(b) Same side-view geometry with UR10 mesh", fill="black", font=font)
    canvas.paste(left, (0, 70))
    canvas.paste(right, (left.width + 36, 70))
    canvas.save(output_path)
    canvas.save(output_path.with_suffix(".pdf"))


def _render_hoop_geometry(output_path: Path):
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.0), constrained_layout=True)
    fig.patch.set_facecolor("white")

    theta = np.linspace(0.0, 2.0 * np.pi, 400)
    hoop_radius = 0.15
    ball_radius = 0.12
    tolerance = hoop_radius - ball_radius

    ax = axes[0]
    ax.plot(hoop_radius * np.cos(theta), hoop_radius * np.sin(theta), color="#4D4D4D", linewidth=2.5, label="hoop ring")
    ax.plot(tolerance * np.cos(theta), tolerance * np.sin(theta), color="#009E73", linewidth=2.0, label="allowed ball center")
    crossing = np.array([0.022, 0.012])
    ax.scatter([0.0], [0.0], color="black", s=24, zorder=3)
    ax.scatter([crossing[0]], [crossing[1]], color="#E69F00", s=70, zorder=4)
    ax.arrow(0.0, 0.0, crossing[0], crossing[1], head_width=0.008, length_includes_head=True, color="#0072B2")
    ax.text(0.006, 0.032, "radial error", fontsize=10, color="#0072B2")
    ax.text(-0.145, 0.125, r"$r_h=0.15$ m", fontsize=10)
    ax.text(-0.070, -0.055, r"$r_h-r_b=0.03$ m", fontsize=10, color="#006B4B")
    ax.set_title("Hoop-plane view")
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("local hoop axis 1 [m]")
    ax.set_ylabel("local hoop axis 2 [m]")
    ax.set_xlim(-0.18, 0.18)
    ax.set_ylim(-0.18, 0.18)
    ax.grid(alpha=0.25)
    ax.legend(loc="lower right", fontsize=9, frameon=False)

    ax = axes[1]
    x = np.linspace(-0.24, 0.24, 160)
    hoop_z = 0.205
    crossing_x = 0.024
    z = hoop_z + 0.035 - 1.05 * (x + 0.06) ** 2 - 0.42 * (x - crossing_x)
    z += hoop_z - np.interp(crossing_x, x, z)
    ax.plot(x, z, color="#0072B2", linewidth=2.5, label="ball center path")
    ax.plot([-0.15, 0.15], [hoop_z, hoop_z], color="#4D4D4D", linewidth=3.0, label="horizontal hoop plane")
    ax.plot([-tolerance, tolerance], [hoop_z, hoop_z], color="#009E73", linewidth=5.0, solid_capstyle="round", label="allowed center band")
    ax.arrow(-0.17, 0.245, 0.10, -0.035, head_width=0.011, length_includes_head=True, color="#0072B2")
    ax.arrow(0.18, hoop_z, 0.0, 0.060, head_width=0.011, length_includes_head=True, color="#CC79A7")
    ax.scatter([crossing_x], [hoop_z], color="#E69F00", s=70, zorder=4)
    ax.text(0.154, hoop_z + 0.066, "open side", fontsize=9, color="#8B3E6D", ha="left", va="bottom")
    ax.set_title("Side view for a horizontal hoop")
    ax.set_xlabel("side-view coordinate [m]")
    ax.set_ylabel("height [m]")
    ax.set_xlim(-0.24, 0.24)
    ax.set_ylim(0.13, 0.29)
    ax.grid(alpha=0.25)
    ax.legend(loc="lower left", fontsize=9, frameon=False)

    for ax in axes:
        ax.tick_params(labelsize=9)
        ax.title.set_fontsize(11)
    fig.savefig(output_path, dpi=240)
    fig.savefig(output_path.with_suffix(".pdf"))
    plt.close(fig)


def _render_candidate_pareto(benchmark: dict, output_path: Path):
    candidate_rows = benchmark["candidate_rows"]
    strategy_rows = benchmark["strategy_rows"]
    time_weights = np.array([0.0, 1.0, 2.0, 3.0, 5.0, 7.5, 10.0, 15.0, 20.0, 30.0, 50.0, 75.0, 100.0, 150.0])
    curve = []
    for time_weight in time_weights:
        selected = []
        for seed in sorted({row["seed"] for row in candidate_rows}):
            feasible = [
                row for row in candidate_rows
                if row["seed"] == seed and row["geometric_status"] == "accepted" and row["success"]
            ]
            if not feasible:
                continue
            best = min(
                feasible,
                key=lambda row: (
                    time_weight * row["time_s"]
                    + 100.0 * row["terminal_error_m"]
                    + 0.20 * row["max_abs_ddq"]
                    + 0.20 * row["max_velocity_ratio"]
                ),
            )
            selected.append(best)
        if selected:
            curve.append(
                {
                    "time_weight": float(time_weight),
                    "mean_time_s": float(np.mean([row["time_s"] for row in selected])),
                    "mean_radial_error_m": float(np.mean([row["radial_error_m"] for row in selected])),
                    "success_rate": float(len(selected) / len({row["seed"] for row in candidate_rows})),
                }
            )
    (output_path.parent / "candidate_pareto_scan.json").write_text(json.dumps(curve, indent=2), encoding="utf-8")

    fig, ax = plt.subplots(figsize=(6.6, 4.5), constrained_layout=True)
    fig.patch.set_facecolor("white")
    if curve:
        ax.plot(
            [row["mean_time_s"] for row in curve],
            [1000.0 * row["mean_radial_error_m"] for row in curve],
            color="#4D4D4D",
            linewidth=1.8,
            marker="o",
            markersize=4,
            label="candidate-weight scan",
        )

    named = {
        "latest_nlp_feasible": ("late feasible", "#CC79A7", "s"),
        "earliest_nlp_feasible": ("time-first feasible", "#0072B2", "^"),
        "smart_cost": ("balanced cost", "#E69F00", "o"),
    }
    for strategy, (label, color, marker) in named.items():
        rows = [row for row in strategy_rows if row["strategy"] == strategy and row["success"]]
        if rows:
            ax.scatter(
                [np.mean([row["catch_time_s"] for row in rows])],
                [1000.0 * np.mean([row["radial_error_m"] for row in rows])],
                color=color,
                marker=marker,
                s=80,
                label=label,
                zorder=4,
            )

    ax.axhline(30.0, color="black", linestyle="--", linewidth=1.1, label="30 mm tolerance")
    ax.set_xlabel("mean successful catch time [s]")
    ax.set_ylabel("mean radial crossing error [mm]")
    ax.set_title("Time-accuracy tradeoff over feasible candidates")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8.5, frameon=False)
    fig.savefig(output_path, dpi=240)
    fig.savefig(output_path.with_suffix(".pdf"))
    plt.close(fig)


def _render_failure_velocity_diagnostics(benchmark: dict, output_path: Path):
    import contextlib
    import io

    from utils.ball_simulation import BallSimulation

    rows = [row for row in benchmark["strategy_rows"] if row["strategy"] == "earliest_nlp_feasible"]
    failed_seeds = {row["seed"] for row in rows if not row["success"]}
    seeds = sorted({row["seed"] for row in rows})
    velocities = []
    with contextlib.redirect_stdout(io.StringIO()):
        for seed in seeds:
            np.random.seed(seed)
            simulation = BallSimulation()
            velocities.append(simulation.velocities[0].copy())
    velocities = np.asarray(velocities, dtype=float)
    horizontal_speed = np.linalg.norm(velocities[:, :2], axis=1)
    lateral_speed = velocities[:, 1]

    fig, ax = plt.subplots(figsize=(6.2, 4.2), constrained_layout=True)
    fig.patch.set_facecolor("white")
    ax.scatter(horizontal_speed, lateral_speed, color="#9aa0a6", s=42, label="successful or unselected seeds")
    first_failed = min(failed_seeds) if failed_seeds else None
    for seed in failed_seeds:
        index = seeds.index(seed)
        ax.scatter(horizontal_speed[index], lateral_speed[index], color="#D55E00", s=95, marker="X", label="failed seed" if seed == first_failed else None)
        ax.text(horizontal_speed[index] + 0.004, lateral_speed[index] + 0.004, str(seed), fontsize=9)
    ax.axhline(np.percentile(lateral_speed, 95), color="#D55E00", linestyle="--", linewidth=1.1, label="95th pct lateral speed")
    ax.set_xlabel("initial horizontal ball speed [m/s]")
    ax.set_ylabel("initial lateral velocity $v_y$ [m/s]")
    ax.set_title("Failure seed is a lateral-trajectory outlier")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8.5, frameon=False)
    fig.savefig(output_path, dpi=240)
    fig.savefig(output_path.with_suffix(".pdf"))
    plt.close(fig)


def _resize_to_height(image: Image.Image, height: int):
    width = int(round(image.width * height / image.height))
    return image.resize((width, height), Image.Resampling.LANCZOS)


def _crop_mesh_side_view(image: Image.Image):
    width, height = image.size
    left = int(width * 0.14)
    right = int(width * 0.93)
    top = int(height * 0.08)
    bottom = int(height * 0.90)
    return image.crop((left, top, right, bottom))


def _font(size: int):
    for path in [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
    ]:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def parse_args():
    parser = argparse.ArgumentParser(description="Render high-score report figures.")
    parser.add_argument("--benchmark", type=Path, default=Path("../outputs/high_score/strategy_benchmark.json"))
    parser.add_argument("--task2-plot", type=Path, default=Path("../outputs/task2_dist1p0/task2_interception_selection.png"))
    parser.add_argument("--mesh-side-plot", type=Path, default=Path("../outputs/task4/task4_side_mesh_with_task2_markers_cropped.png"))
    parser.add_argument("--output-dir", type=Path, default=Path("../outputs/high_score"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    figures = render_figures(
        benchmark_path=args.benchmark,
        task2_plot=args.task2_plot,
        mesh_side_plot=args.mesh_side_plot,
        output_dir=args.output_dir,
    )
    for figure in figures:
        print(f"figure: {figure}")
