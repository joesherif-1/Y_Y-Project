import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

APP_NAME = "Cancer Risk-Factor Checker"

# Symptoms the questionnaire asks about: key -> (label shown to user, points)
# Points are higher for "red flag" symptoms doctors take most seriously.
SYMPTOMS = {
    "weight_loss": ("Unexplained weight loss", 3),
    "lump": ("A new lump or swelling", 3),
    "bleeding": ("Unusual bleeding or bruising", 3),
    "pain": ("Persistent pain that doesn't go away", 2),
    "fever": ("Recurring fever or night sweats", 2),
    "cough": ("A cough or hoarseness that won't go away", 2),
    "bowel": ("A change in bowel or bladder habits", 2),
    "skin": ("A change in a mole or patch of skin", 2),
    "fatigue": ("Constant tiredness (fatigue)", 1),
    "appetite": ("Loss of appetite", 1),
}

# Symptoms that should always trigger a "please see a doctor" message,
# no matter what the total score is.
RED_FLAGS = {"weight_loss", "lump", "bleeding"}

DURATION_POINTS = {
    "none": 0,      # no symptoms
    "under2": 0,    # under 2 weeks
    "w2to4": 1,     # 2-4 weeks
    "m1to3": 2,     # 1-3 months
    "over3": 3,     # more than 3 months
}

# Highest score possible: age(4) + previous cancer(4) + chronic condition(2)
# + family history(3) + smoking(4) + alcohol(2) + all symptoms(21) + duration(3)
# + AI spot check(3)
MAX_SCORE = 46


def score_assessment(form):
    """Turn the questionnaire answers into a score with a breakdown."""
    breakdown = []
    total = 0

    def add(label, points):
        nonlocal total
        if points > 0:
            breakdown.append((label, points))
            total += points

    try:
        age = int(form.get("age", 0))
    except ValueError:
        age = 0
    if age >= 60:
        add("Age 60 or older", 4)
    elif age >= 40:
        add("Age 40-59", 2)

    # "Unsure" answers get a middle score, so an unknown history
    # is treated more carefully than a clear "no".
    if form.get("prev_cancer") == "yes":
        add("Previous cancer diagnosis", 4)
    elif form.get("prev_cancer") == "unsure":
        add("Unsure about previous diagnosis (middle score)", 2)

    if form.get("chronic") == "yes":
        add("Long-term medical condition", 2)
    elif form.get("chronic") == "unsure":
        add("Unsure about long-term conditions (middle score)", 1)

    if form.get("family_cancer") == "yes":
        add("Close family member with cancer", 3)
    elif form.get("family_cancer") == "unsure":
        add("Unsure about family cancer history (middle score)", 2)

    smoking = form.get("smoking")
    if smoking == "current":
        add("Currently smokes", 4)
    elif smoking == "former":
        add("Used to smoke", 2)

    alcohol = form.get("alcohol")
    if alcohol == "regular":
        add("Drinks alcohol regularly", 2)
    elif alcohol == "occasional":
        add("Drinks alcohol occasionally", 1)

    chosen = [s for s in form.getlist("symptoms") if s in SYMPTOMS]
    for key in chosen:
        label, points = SYMPTOMS[key]
        add(label, points)

    duration = form.get("duration", "none")
    if chosen:
        add("How long the symptoms have lasted", DURATION_POINTS.get(duration, 0))

    # AI spot check from the hand photo (percentage 0-100, set by the browser).
    # It only ever sees one cropped spot, so it gets modest weight - at most the
    # same points as a family history of cancer.
    ai = None
    ai_raw = form.get("ai_spot", "")
    if ai_raw:
        try:
            ai_pct = max(0, min(100, int(float(ai_raw))))
        except ValueError:
            ai_pct = None
        if ai_pct is not None:
            ai = {"pct": ai_pct}
            if ai_pct >= 70:
                add("AI spot check: strongly similar to suspicious training images", 3)
            elif ai_pct >= 50:
                add("AI spot check: similar to suspicious training images", 2)

    if total >= 16:
        level, level_class = "Elevated", "high"
    elif total >= 8:
        level, level_class = "Moderate", "medium"
    else:
        level, level_class = "Low", "low"

    # Red flag: a serious symptom that has lasted 2 weeks or more.
    red_flag = bool(RED_FLAGS.intersection(chosen)) and duration in ("w2to4", "m1to3", "over3")

    return {
        "total": total,
        "max_score": MAX_SCORE,
        "percent": round(total / MAX_SCORE * 100),
        "level": level,
        "level_class": level_class,
        "breakdown": breakdown,
        "red_flag": red_flag,
        "ai": ai,
    }


@app.route("/")
def index():
    return render_template("index.html", app_name=APP_NAME)


@app.route("/questionnaire")
def questionnaire():
    return render_template("questionnaire.html", app_name=APP_NAME, symptoms=SYMPTOMS)


@app.route("/result", methods=["GET", "POST"])
def result():
    if request.method == "GET":
        return redirect(url_for("index"))
    return render_template("result.html", app_name=APP_NAME, r=score_assessment(request.form))


@app.route("/skin-check")
def skin_check():
    return render_template("skin_check.html", app_name=APP_NAME)


@app.route("/health")
def health():
    return "OK"


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
