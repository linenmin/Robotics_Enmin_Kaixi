# Project Environments

- **Primary runtime**: `conda activate robotics`
  - **type**: conda
  - **python**: 3.13.13
  - **created from**: `exercise_0_software_environment/py13roboticscourse_env.yml`
  - **notes**: Environment created on 2026-04-28 for the Robotics project. The provided YAML installed `example-robot-data` without an importable loader on Windows/Python 3.13, so `example-robot-data-loaders` was installed with `pip --no-deps`, a `.pth` path file was added, and its `path.py` was corrected to point at `D:/Anaconda3/envs/robotics/Library/share/example-robot-data/robots`.

## Verification

- `exercise_0_software_environment/0_setup.ipynb` executed successfully with `robotics`.
- `software/hoops.ipynb` executed successfully with `robotics`.

