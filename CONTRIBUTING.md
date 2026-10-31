# Contributing

Thank you for working on this project. These rules keep the repository clean and make sure four
people can work at the same time without conflicts.

## 1. Golden rules
1. **Never push directly to `main`.** All work goes through a pull request.
2. **One member, one branch, your own files.** Do not edit another member's module. If you find a
   problem in it, open an issue or comment on their pull request.
3. **Use your own GitHub account** and set `git config user.name` / `user.email`, so GitHub credits
   the right person.
4. **Small commits, clear messages.** Commit after each finished step, not once at the end.
5. **Green CI before merge** (lint + tests) and **one teammate's review**.

## 2. Who owns what
| Area | Owner |
|---|---|
| `etl/member1_structural_cleaning.py`, `tests/test_member1_*` | Abhijith |
| `etl/member2_missing_values.py`, `tests/test_member2_*` | Farhan |
| `etl/member3_invalid_and_outliers.py`, `tests/test_member3_*` | Keerthi |
| `etl/member4_features.py`, `etl/member4_reports.py`, `tests/test_member4_*` | Anaz |
| `pipeline.py`, `etl/common.py`, `tests/conftest.py`, `tests/test_pipeline.py`, `docs/`, `.github/`, `README.md` | Abhijith |

Need a change in a shared file (for example a new constant in `etl/common.py`)? Open an issue or ask
the team lead; do not edit it inside your own pull request.

## 3. Branch names
`feature/memberN-<topic>`, for example `feature/member2-missing-values`.
Other work: `fix/<topic>` (bug fix), `docs/<topic>` (documentation).

## 4. Commit messages
Use the form `<type>: <what you did>` in the present tense, under 72 characters.

| Type | Use for | Example |
|---|---|---|
| `feat` | new functionality | `feat: add duplicate removal` |
| `fix` | bug fix | `fix: handle NaN in children column` |
| `test` | tests | `test: cover zero-night stays` |
| `docs` | documentation | `docs: explain outlier capping` |
| `refactor` | code clean-up, no behaviour change | `refactor: extract _iqr_bounds` |

## 5. Pull request process
1. `git pull origin main` and make sure your branch is up to date.
2. Run the checks locally:
   ```bash
   flake8 .
   pytest
   python check_member.py N      # N = your member number
   ```
3. Push your branch and open a pull request into `main`. Fill in the template and add a screenshot
   of the `check_member.py` output.
4. Ask a teammate to review. Answer every comment; push fixes to the same branch.
5. When CI is green and one person has approved, **merge with "Create a merge commit"**.
6. Merge order: **Member 1, then 2, then 3, then 4**, because each stage uses the previous one.

## 6. Code standards
- Python 3.10+, formatted to `flake8` with a maximum line length of 100.
- Every transformation step must call `_log(...)` with a clear **reason** (why it was necessary).
  The reasons end up in `reports/transformation_log.csv` and in the final report.
- Keep the function signatures and the `meta` keys from [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
  unchanged, other modules depend on them.
- Do not hard-code absolute paths. Use the constants from `etl/common.py`.
- Do not commit data files, `__pycache__` or virtual environments (`.gitignore` covers them).
- Add or update tests for what you change. Tests skip automatically while a teammate's module is
  still a stub, so they never block you.

## 7. Reporting problems
Use the **Task** or **Bug report** issue template. Include what you expected, what happened, and the
command you ran.
