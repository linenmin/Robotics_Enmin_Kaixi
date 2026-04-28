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
    _render_strategy_benchmark(benchmark, benchmark_figure)
    _render_side_by_side(task2_plot, mesh_side_plot, side_by_side_figure)
    return benchmark_figure, side_by_side_figure


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
    target_height = 760
    left = _resize_to_height(left, target_height)
    right = _resize_to_height(right, target_height)
    width = left.width + right.width + 36
    height = target_height + 122
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    font = _font(28)
    small_font = _font(20)
    draw.text((18, 14), "(a) Predicted trajectory and Task 2 candidate filtering", fill="black", font=font)
    draw.text((left.width + 54, 14), "(b) Same side-view geometry with UR10 mesh", fill="black", font=font)
    canvas.paste(left, (0, 70))
    canvas.paste(right, (left.width + 36, 70))
    caption_y = target_height + 84
    draw.text((18, caption_y), "Same color semantics as Task 2: red = simple candidate, yellow = smart candidate.", fill="black", font=small_font)
    draw.text((left.width + 54, caption_y), "Green sphere shows the physical ball at the smart catch point.", fill="black", font=small_font)
    canvas.save(output_path)


def _resize_to_height(image: Image.Image, height: int):
    width = int(round(image.width * height / image.height))
    return image.resize((width, height), Image.Resampling.LANCZOS)


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
    strategy_figure, comparison_figure = render_figures(
        benchmark_path=args.benchmark,
        task2_plot=args.task2_plot,
        mesh_side_plot=args.mesh_side_plot,
        output_dir=args.output_dir,
    )
    print(f"strategy figure: {strategy_figure}")
    print(f"comparison figure: {comparison_figure}")
