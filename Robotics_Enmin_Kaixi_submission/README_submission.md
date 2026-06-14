# Robotics Submission

Authors: Enmin Lin and Kaixi Yao

This archive contains the three required PDF reports and the source code needed to reproduce the homework and project results.

## Contents

- `reports/Homework_A_answers.pdf`
- `reports/Homework_B_answers.pdf`
- `reports/Project_report.pdf`
- `reports/Kaixi_Yao_Enmin_Lin_CoC.pdf`
- `code/Homework_A/Homework_A_coding_questions.ipynb`
- `code/Homework_B/Homework_B_coding_questions.ipynb`
- `code/Project/software/`
- `code/Project/exercise_0_software_environment/`

The GenAI code of conduct form is included as a separate PDF.

## Reproduction Notes

The homework notebooks run with a standard Python environment containing `numpy` and `matplotlib`.

For the project, create the course environment:

```bash
conda env create -f code/Project/exercise_0_software_environment/py13roboticscourse_env.yml
conda activate py13roboticscourse
```

Then run the project tests from the software directory:

```bash
cd code/Project/software
python -m unittest discover -s tests -v
```

The main project scripts are in `code/Project/software/scripts/`.
