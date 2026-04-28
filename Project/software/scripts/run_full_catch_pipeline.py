import argparse
import json
import sys
from pathlib import Path

SOFTWARE_DIR = Path(__file__).resolve().parents[1]
if str(SOFTWARE_DIR) not in sys.path:
    sys.path.insert(0, str(SOFTWARE_DIR))
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from benchmark_high_score_strategies import run_benchmark
from render_task4_meshcat_report_scene import render_scene
from replay_task4_meshcat import build_replay


def run_pipeline(seed: int, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    benchmark_dir = output_dir / f"seed_{seed}_benchmark"
    benchmark_metrics, benchmark_summary, benchmark_payload = run_benchmark(
        seeds=[seed],
        output_dir=benchmark_dir,
        max_candidate_distance=1.15,
        max_candidates=8,
        success_tolerance=0.03,
    )
    replay_html = output_dir / f"full_pipeline_meshcat_replay_seed{seed}.html"
    replay_summary = build_replay(
        seed=seed,
        output_html=replay_html,
        open_browser=False,
        keep_alive_seconds=0.0,
    )
    side_scene_html = output_dir / f"full_pipeline_side_scene_seed{seed}.html"
    side_scene_summary = render_scene(
        seed=seed,
        output_html=side_scene_html,
        camera_view="side",
        show_target_markers=True,
        simple_max_distance=1.0,
    )
    summary = {
        "seed": seed,
        "benchmark_metrics": str(benchmark_metrics),
        "benchmark_summary_csv": str(benchmark_summary),
        "meshcat_replay_html": str(replay_html),
        "side_scene_html": str(side_scene_html),
        "strategy_summary": benchmark_payload["summary"],
        "strategy_rows": benchmark_payload["strategy_rows"],
        "replay_summary": replay_summary,
        "side_scene_summary": side_scene_summary,
    }
    summary_path = output_dir / f"full_pipeline_seed{seed}.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary_path, summary


def parse_args():
    parser = argparse.ArgumentParser(description="Run the complete high-score catch pipeline for one seed.")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output-dir", type=Path, default=Path("../outputs/high_score"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    summary_file, result = run_pipeline(seed=args.seed, output_dir=args.output_dir)
    print(json.dumps({k: result[k] for k in ["seed", "strategy_summary", "meshcat_replay_html", "side_scene_html"]}, indent=2))
    print(f"summary: {summary_file}")
