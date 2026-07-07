# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A student educational website (grade 10 extracurricular by Younus Hassen and Yousef Sherif): a cancer
risk-factor questionnaire plus an in-browser ML skin-lesion classifier. The maintainers are beginners —
prefer simple, readable code and explain changes in beginner-friendly terms.

## Commands

```bash
pip install -r requirements.txt
python app.py                # dev server; respects PORT (macOS AirPlay occupies 5000, so set PORT)
```

There are no tests or linters. Deployment is automatic: pushing to `main` redeploys the Render web
service (gunicorn via `Procfile`).

## Architecture

**Flask app (`app.py`)** — all routes and all scoring logic in one file:

- `/` (`templates/index.html`) — hand-photo check-in unlocks the questionnaire; optional "AI spot check"
  crops a 224×224 square around a tapped point and runs the ML model on it, client-side.
- `/questionnaire` (`templates/questionnaire.html`) — a single page; JS shows one of 7 `<section class="step">`s
  at a time and POSTs everything to `/result`.
- `/result` — `score_assessment()` turns answers into a weighted score. `SYMPTOMS`, `RED_FLAGS`,
  `DURATION_POINTS`, and `MAX_SCORE` in `app.py` must stay consistent with each other and with the
  questionnaire's input names/values; "Unsure" answers score middle values on purpose.
- `/skin-check` (`templates/skin_check.html`) — the dedicated ML page.

**ML pipeline** — three pieces share a strict contract:

1. `training/train_skin_model.ipynb` (Google Colab) trains MobileNetV2 on HAM10000 (benign vs
   suspicious) and exports a **SavedModel** + `metrics.json` as `skin_model.zip`. It deliberately uses
   **zero pip installs** — only stock Colab libraries — because pip version conflicts on Colab broke it
   twice. Keep it that way.
2. `training/convert_to_web.sh` converts that zip to a **TF.js graph model** in `static/model/`
   (the version-fragile step, isolated in a throwaway venv; includes a protobuf-clash workaround).
3. The browser (`index.html` and `skin_check.html`) loads it with `tf.loadGraphModel('/static/model/model.json')`
   and feeds **raw 0–255 pixels at 224×224** — no normalization in JS, because a `Rescaling` layer is
   inside the model. If you change preprocessing in the notebook, the JS must match, and vice versa.
   `static/model/metrics.json` (test accuracy etc.) is displayed to users; regenerate it with the model.

## Non-negotiable framing (the point of the project)

The site must never claim to detect or diagnose cancer. Keep the established honesty rules when editing:

- Photos are analyzed client-side only and never uploaded — don't add server-side image handling.
- The model only ever sees a close-up crop of a single skin spot, never a whole hand/body photo
  (it was trained on single-lesion dermatoscope images; anything else produces meaningless output).
- Results are worded as "looks similar to benign/suspicious training images", with disclaimers and
  "see a doctor" advice; red-flag symptoms always advise seeing a doctor regardless of score.

## Gotchas

- `CascadeProjects/Y_Y Project/` is a stale duplicate of an early prototype — never edit it.
- Flask only finds pages in `templates/` and CSS/JS/model files in `static/` (an early bug came from
  files at the repo root).
- `.claude/launch.json` is machine-specific local preview config and is gitignored.
