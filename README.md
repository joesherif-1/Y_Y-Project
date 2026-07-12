# Cancer Risk-Factor Checker

A student educational website built with Python (Flask). The user takes a photo of
their hand as a check-in step, then answers a questionnaire about known cancer risk
factors. The site calculates a **risk-factor score** and explains what contributed to it.

> **Important:** This tool cannot detect or diagnose cancer. The hand photo is never
> uploaded or analyzed — it stays on the user's device. The score only counts general,
> well-known risk factors, and the site always advises talking to a real doctor.

## How it works

1. **Home page** — take/choose a hand photo (client-side only) to unlock the questionnaire.
2. **Questionnaire** — 7 sections: age & sex, medical history, family history of cancer,
   smoking & alcohol, symptoms, duration of symptoms, and other health information.
3. **Results** — each risk factor adds weighted points (e.g. current smoking +4,
   family history +3, unexplained weight loss +3). The total maps to a
   Low / Moderate / Elevated level, with a breakdown of every point and a disclaimer.
   Serious "red flag" symptoms lasting 2+ weeks always trigger a "see a doctor soon" note.
   History questions offer a "Not sure" answer that adds a middle score, so an unknown
   history is treated more carefully than a clear "no" (worst-case thinking).
   If the user ran the AI spot check on their hand photo, its finding is scored too
   (suspicious-like ≥70% adds +3, 50–69% adds +2, benign-like adds 0) and explained
   on the results page with honest limits.
   Step 2 is a guided hand self-check for signs a phone camera can't judge reliably —
   pale nails/palms (+2), yellow-tinted skin or eyes (+3), fingertip clubbing/swelling
   (+3) — observed by the user's own eyes and scored like any other risk factor; the
   yellow-tint and clubbing signs also trigger a "see a doctor soon" note.

## Version 2: AI Skin Check (ML experiment)

The `/skin-check` page runs a real neural network **in the browser** (TensorFlow.js), so
photos never leave the user's device. The model is a MobileNetV2 fine-tuned on the public
HAM10000 dermatology dataset (10,015 images) to separate benign-looking from
suspicious-looking skin spots.

- Train it yourself on Google Colab: see [`training/README.md`](training/README.md)
  (about 30 minutes, free GPU).
- Drop the exported files into `static/model/` and the page starts working automatically,
  displaying the model's real test accuracy.
- Until then, the page shows a "model not installed yet" notice.

## Local setup

```bash
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

## Project structure

```
app.py                    # Flask routes + scoring logic
templates/                # HTML pages (Flask requires this folder name)
  base.html               # shared layout
  index.html              # home + hand photo step
  questionnaire.html      # 7-section multi-step form
  result.html             # score, level, breakdown
static/style.css          # styling (Flask requires this folder name)
Procfile                  # for deploying on Render
```

## Roadmap / Next Steps

- AI model at the end of the program
- Very polished UI
- Test with real people
- Make it go public
- Write a research

## Deploy to Render

1. Push the code to a GitHub repository.
2. On [render.com](https://render.com), create a new **Web Service** and connect the repo.
   Render auto-detects the Python/Flask app and uses the `Procfile`.
3. Set an environment variable `SECRET_KEY` (generate one with
   `python -c 'import secrets; print(secrets.token_hex(32))'`).
4. Deploy — you'll get a URL like `https://your-app.onrender.com`.

Made with love in Saudi Arabia 🇸🇦
By Younus Hassen and Yousef Sherif
