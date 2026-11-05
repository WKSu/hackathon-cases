# Hackathon cases: Themadag Mobiliteit (Rotterdam × Den Haag)

Prototypes built over the lunch break, between the morning design session and the afternoon try-out. Time budget: **90 minutes per case**.

| Case | Folder | What we demo this afternoon |
|---|---|---|
| Contractmanagement | [`cases/contractmanagement`](cases/contractmanagement) | Concept dashboard: overview of all contracts with stoplight signals (synthetic data) |
| Laadlichten (wegbeheer): VRI | [`cases/laadlichten`](cases/laadlichten) | A "living map" of the city's traffic lights (VRIs) for civil servants |
| Laadlichten (wegbeheer): laadpalen | [`cases/laadpalen`](cases/laadpalen) | Address search with a 200 m circle: which parking bays fit a new charging point under the 2025 placement policy. [Live](https://wksu.github.io/hackathon-cases/cases/laadpalen/prototype/) |

## How this repo works

The local machine is the workshop and GitHub is the control room. The decisions and the progress sit in plain files next to the code, so the git history shows what was decided and when.

Each case folder contains:

- **`README.md`**: the brief, the **scope fence** (what is built today and what is not), the **status checklist** and the **parking lot**
- **`DECISIONS.md`**: an append-only log of the choices made while building
- **`prototype/`**: the code

Start a case from [`cases/_template/`](cases/_template). The briefs themselves are kept locally in `_private/` until you decide what may go into this public repo.

### The build loop (repeat every 15–20 minutes)

1. Take the next unchecked item from the case's status checklist.
2. Build it, locally with Claude.
3. If you made a choice someone could reasonably have made differently, add one entry to `DECISIONS.md`. This covers the data source, a threshold, a library, or what you left out.
4. Tick the item off, then commit and push.

On GitHub, the commit list on the case branch is your progress feed. `DECISIONS.md` is where you challenge choices: a line comment on it in the draft PR is enough.

### Branches

- `main` holds only demo-ready states.
- Each case has its own branch (`case/cm`, `case/ll` and `case/lp`) and **one draft PR** that you open at minute 0. The PR becomes the single page where you see the commits, the diff and the decisions for that case. Merge it when the demo works.
- Running both cases in parallel? Use a git worktree for each, so that two Claude sessions never share one working directory:

```bash
git worktree add -b case/cm ../hc-cm main
```

```bash
git worktree add -b case/ll ../hc-ll main
```

### Commit messages

Start each message with a case prefix: `[cm] …`, `[ll] …`, `[lp] …` or `[repo] …`. Then give the type: `feat`, `fix`, `decision`, `data` or `docs`.

For example: `[cm] feat: expiry signal with/without extension option`.

### Timebox per case (about 90 minutes)

| Min | What |
|---|---|
| 0–10 | Re-read the scope fence and settle the open decisions in `DECISIONS.md` (data, stack, what counts as "done") |
| 10–70 | Build in 15-minute slices, pushing after each slice |
| 70–85 | Feature freeze: write the demo script and take screenshots, then check that it opens on a clean machine |
| 85–90 | Merge the PR and tag `demo-cm`, `demo-ll` or `demo-lp` |
| Afternoon | Write the feedback from the try-out into `FEEDBACK.md` in the case folder. The parking lot becomes the backlog |

## Data and privacy rules (this repo is public)

- **Only synthetic data or open data goes into the repo.** That means no Oracle or Excel exports, no names, no e-mail addresses and no phone numbers.
- Raw inputs (forms, e-mails, transcripts, header-only Excels) go in `_private/`, which git ignores. The themadag rules say **transcripts are deleted after the day**. Once a file is in git history it is effectively impossible to delete, so a transcript must never be committed.
- Any person-level signal (for example, "who leaves soon") is modelled at **role** level: is the role filled, yes or no.
