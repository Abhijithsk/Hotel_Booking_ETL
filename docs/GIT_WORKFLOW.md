# Git Workflow - Step by Step

Each member works on their **own branch**, in their **own files**, under their **own GitHub
account**. See [CONTRIBUTING.md](../CONTRIBUTING.md) for the rules.

| Member | Branch | Files |
|---|---|---|
| 1 | `feature/member1-structural-cleaning` | `etl/member1_structural_cleaning.py` |
| 2 | `feature/member2-missing-values` | `etl/member2_missing_values.py` |
| 3 | `feature/member3-invalid-and-outliers` | `etl/member3_invalid_and_outliers.py` |
| 4 | `feature/member4-features-and-reports` | `etl/member4_features.py`, `etl/member4_reports.py` |

---

## Part A - Team lead (one time)

1. Create an **empty** repository `Hotel_Booking_ETL` on GitHub (no README, no .gitignore, no licence).
2. *Settings -> Collaborators -> Add people*: invite the three members. Each must accept the e-mail invite.
3. In the project folder:
   ```bash
   git init -b main
   git config user.name  "Your Name"
   git config user.email "your-github-email@example.com"
   git add .
   git commit -m "chore: initial project scaffold"
   git remote add origin https://github.com/Abhijithsk/Hotel_Booking_ETL.git
   git push -u origin main
   ```
4. Open the **Actions** tab and check that the first CI run is green (members' tests show as skipped).
5. Protect `main`: *Settings -> Branches -> Add branch protection rule*, pattern `main`:
   - [x] Require a pull request before merging (1 approval)
   - [x] Require status checks to pass before merging, and select the `lint-and-test` checks
   - [x] Do not allow bypassing the above settings
   (On a private repository under a free plan, branch protection may not be available; the team
   can still follow the same rules by agreement.)
6. Create four issues from the task cards in `docs/tasks/` (*Issues -> New issue -> Task*), paste the
   card, assign one member to each, and add labels or a milestone if you wish.
7. Send each member the repository link and their task card.

## Part B - Each member

Replace `N` and the branch name with your own (see the table above).

**1. Clone and set up**
```bash
git clone https://github.com/Abhijithsk/Hotel_Booking_ETL.git
cd Hotel_Booking_ETL
git config user.name  "Your Name"
git config user.email "your-github-email@example.com"
python -m venv .venv && source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

**2. Create your branch**
```bash
git checkout -b feature/memberN-<topic>
```

**3. Add your code**
Open your stub in `etl/` and replace it with your finished module (your starter code is in the
package the team lead gave you). Read every line; you will be asked about it in the review.

**4. Check your work**
```bash
flake8 .
pytest
python check_member.py N
```
Expected last lines of `check_member.py`:

| N | Expected |
|---|---|
| 1 | `CHECK OK after Member 1: 87,396 rows x 34 columns` |
| 2 | `CHECK OK after Member 2: 87,396 rows x 35 columns, 0 null values` |
| 3 | `CHECK OK after Member 3: 86,638 rows x 35 columns, 0 null values` |
| 4 | `PIPELINE FINISHED ... raw 119,390 x 32 -> clean 86,638 x 46` |

Members 2 to 4 need the earlier members' code. Run `git pull origin main` after the previous pull
request has been merged.

**5. Commit and push** (several small commits are better than one big one)
```bash
git add etl tests
git status
git commit -m "feat: add duplicate removal and column renaming"
git push -u origin feature/memberN-<topic>
```

**6. Open a pull request** on GitHub (*Compare & pull request*), base `main`. Fill in the template,
add a screenshot of `check_member.py`, link your issue (`Closes #N`) and request a teammate as reviewer.

**7. Review and merge.** Fix review comments by pushing to the same branch. When CI is green and
someone approved, click **Merge pull request -> Create a merge commit**. Merge order is 1, 2, 3, 4.

**8. Update your local copy**
```bash
git checkout main
git pull origin main
```

## Part C - After all four pull requests are merged

```bash
git checkout main
git pull origin main
python pipeline.py
git checkout -b docs/final-reports
git add reports screenshots
git commit -m "docs: add generated reports and screenshots"
git push -u origin docs/final-reports
```
Open a pull request for it, merge it, and create a release tag:
```bash
git checkout main && git pull origin main
git tag -a v1.0 -m "First complete ETL pipeline"
git push origin v1.0
```

## Handy commands
| Task | Command |
|---|---|
| See changes | `git status`, `git diff` |
| See history | `git log --oneline --graph --all` |
| Bring the latest `main` into your branch | `git fetch origin && git merge origin/main` |
| Undo uncommitted changes in a file | `git restore <file>` |
| Fix the last commit message (not yet pushed) | `git commit --amend` |

## Troubleshooting
| Problem | Fix |
|---|---|
| `Authentication failed` on push | GitHub no longer accepts passwords; sign in through the browser prompt or use a personal access token |
| `remote origin already exists` | `git remote set-url origin https://github.com/Abhijithsk/Hotel_Booking_ETL.git` |
| `Permission denied` / 403 on push | The collaborator invite has not been accepted yet |
| `check_member.py 2` raises `NotImplementedError` | Member 1's code is not in your branch yet: `git pull origin main` |
| Merge conflict | You probably edited a file you do not own. Restore it with `git checkout origin/main -- <file>` |
| CI fails on `flake8` | Run `flake8 .` locally and fix the lines it lists |
