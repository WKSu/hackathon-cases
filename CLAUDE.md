# Instructions for Claude sessions in this repo

These prototypes are built in about 90 minutes and shown to non-technical civil servants the same afternoon. Speed matters, and so does keeping the human in control of the choices.

## Before you touch a case

1. Read `cases/<case>/README.md`, especially the **scope fence**, and then `cases/<case>/DECISIONS.md`.
2. Work only on items in the status checklist. If you get a new idea, or the user asks for something outside the scope fence, add it to the **parking lot** and do not build it. Mention that you parked it.

## Logging decisions (this is the main control mechanism)

Whenever you make a choice that someone could reasonably have made differently, append an entry to `DECISIONS.md`. Examples: data source, library, metric definition, threshold, data model field, or what to leave out. Write it in the same commit as the code that implements it. Use this format:

```markdown
## D-NNN: <short title>
- **Status:** proposed | accepted | superseded by D-NNN
- **When / who:** 2026-11-05 13:10 · Claude (or a name)
- **Decision:** one or two sentences.
- **Why:** the reason, including the trade-off.
- **Rejected alternative:** what you did not do, and why.
```

Use `proposed` when the user should confirm. **Don't block on it**: carry on with the proposal and point it out in your reply. Never edit an old entry's decision. Supersede it with a new entry instead.

## Commits

- Commit small, after each checklist item, and push straight away so progress shows on GitHub.
- Prefix: `[cm]`, `[ll]` or `[repo]`, then the type (`feat`, `fix`, `decision`, `data`, `docs`).
- Tick the item off in the case README's status checklist in the same commit.

## Data and privacy (hard rules: the repo is PUBLIC)

- Use only synthetic data or open data. Generate synthetic data with a script that you commit, so it can be reproduced.
- Never commit names, e-mail addresses, phone numbers, real contract values, Oracle or Excel exports, or transcripts. Raw inputs live in `_private/`, which git ignores.
- Model person-related signals at role level (role filled yes/no; vacancy), never per named person.
- Label mocked or fictitious values as such in the UI (`fictief`), so the audience does not mistake them for real data.

## Prototype defaults (unless DECISIONS.md says otherwise)

- One `index.html` per prototype that opens by double-click: no build step and no server.
- External libraries come from cdnjs or jsdelivr with an **exact pinned version**.
- Data lives in a `data.js` file that sets a global (`window.DATA = …`), or inline. Do **not** use `fetch('data.json')`: browsers block it when the page is opened as `file://`, and that is a classic way for a demo to fail.
- UI text is in Dutch, in a plain and short style.
- Put a short "Hoe te demonstreren" section (3 steps) in the case README before the feature freeze.
