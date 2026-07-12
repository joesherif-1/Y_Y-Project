import os
from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

APP_NAME = "Cancer Risk-Factor Checker"

# Symptoms the questionnaire asks about: key -> (label shown to user, points, why it matters)
# Points are higher for "red flag" symptoms doctors take most seriously.
SYMPTOMS = {
    "weight_loss": ("Unexplained weight loss", 3,
        "Losing weight without trying can be a sign the body is fighting something and is "
        "worth checking with a doctor, especially alongside other symptoms."),
    "lump": ("A new lump or swelling", 3,
        "New lumps or swelling have many possible causes, but doctors recommend any new one "
        "be examined in person."),
    "bleeding": ("Unusual bleeding or bruising", 3,
        "Unusual bleeding or bruising can point to several different conditions, so it's one "
        "doctors want to investigate directly."),
    "pain": ("Persistent pain that doesn't go away", 2,
        "Pain that lingers rather than fading is the body's way of signaling something needs "
        "attention."),
    "fever": ("Recurring fever or night sweats", 2,
        "Recurring fevers or night sweats are often linked to infections, and less commonly "
        "to other conditions doctors screen for."),
    "cough": ("A cough or hoarseness that won't go away", 2,
        "A cough or hoarseness lasting weeks is taken seriously by doctors, especially for "
        "smokers or former smokers."),
    "bowel": ("A change in bowel or bladder habits", 2,
        "Changes in bowel or bladder habits are a symptom doctors specifically ask about "
        "during check-ups."),
    "skin": ("A change in a mole or patch of skin", 2,
        "Changes in a mole or skin patch are exactly what the ABCDE rule and this site's AI "
        "spot check are designed to help you notice."),
    "fatigue": ("Constant tiredness (fatigue)", 1,
        "Constant tiredness has many everyday causes, but combined with other symptoms it's "
        "worth mentioning to a doctor."),
    "appetite": ("Loss of appetite", 1,
        "Losing your appetite for no clear reason, especially alongside other symptoms, is "
        "worth a doctor's opinion."),
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
# + AI spot check(3) + hand self-check: pale(2) + yellow(3) + clubbing(3)
MAX_SCORE = 54


def score_assessment(form):
    """Turn the questionnaire answers into a score with a breakdown."""
    breakdown = []
    total = 0

    def add(label, points, explain=""):
        nonlocal total
        if points > 0:
            breakdown.append({"label": label, "points": points, "explain": explain})
            total += points

    try:
        age = int(form.get("age", 0))
    except ValueError:
        age = 0
    if age >= 60:
        add("Age 60 or older", 4,
            "Cancer risk generally rises with age, mainly because cells build up genetic "
            "changes over a longer lifetime.")
    elif age >= 40:
        add("Age 40-59", 2,
            "Risk starts climbing in this range, though it's still noticeably lower than for "
            "older adults.")

    # "Unsure" answers get a middle score, so an unknown history
    # is treated more carefully than a clear "no".
    if form.get("prev_cancer") == "yes":
        add("Previous cancer diagnosis", 4,
            "A past cancer diagnosis means doctors watch more closely for it returning or for "
            "a second, unrelated cancer forming.")
    elif form.get("prev_cancer") == "unsure":
        add("Unsure about previous diagnosis (middle score)", 2,
            "Since it's unclear, this gets a cautious middle score rather than assuming a "
            "clear \"no\" — worth checking your health records.")

    if form.get("chronic") == "yes":
        add("Long-term medical condition", 2,
            "Some chronic conditions (like long-term hepatitis or inflammatory bowel disease) "
            "are linked to higher cancer risk over time.")
    elif form.get("chronic") == "unsure":
        add("Unsure about long-term conditions (middle score)", 1,
            "Same reasoning as above — an unknown history gets a cautious middle score.")

    if form.get("family_cancer") == "yes":
        add("Close family member with cancer", 3,
            "Shared genes and sometimes shared environment mean a family history can point to "
            "inherited risk factors.")
    elif form.get("family_cancer") == "unsure":
        add("Unsure about family cancer history (middle score)", 2,
            "A cautious middle score, since an unknown family history could be hiding a real "
            "pattern.")

    smoking = form.get("smoking")
    if smoking == "current":
        add("Currently smokes", 4,
            "Smoking is one of the most well-established cancer risk factors, linked to many "
            "cancer types beyond just the lungs.")
    elif smoking == "former":
        add("Used to smoke", 2,
            "Former smokers still carry increased risk, though it gradually declines the "
            "longer someone has quit.")

    alcohol = form.get("alcohol")
    if alcohol == "regular":
        add("Drinks alcohol regularly", 2,
            "Regular alcohol use is linked to several cancer types, with risk rising alongside "
            "the amount consumed.")
    elif alcohol == "occasional":
        add("Drinks alcohol occasionally", 1,
            "Occasional drinking carries a smaller, but non-zero, increase in risk.")

    chosen = [s for s in form.getlist("symptoms") if s in SYMPTOMS]
    for key in chosen:
        label, points, explain = SYMPTOMS[key]
        add(label, points, explain)

    duration = form.get("duration", "none")
    if chosen:
        add("How long the symptoms have lasted", DURATION_POINTS.get(duration, 0),
            "Symptoms that stick around longer are generally taken more seriously by doctors "
            "than ones that pass quickly.")

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
                add("AI spot check: strongly similar to suspicious training images", 3,
                    "The model found this spot visually much closer to the \"suspicious\" "
                    "training images than most spots it has seen.")
            elif ai_pct >= 50:
                add("AI spot check: similar to suspicious training images", 2,
                    "The model found this spot somewhat closer to the \"suspicious\" side, "
                    "though less strongly than a high score would show.")

    # Hand self-check observations (made by the user's own eyes in step 2 -
    # the AI cannot see color or 3D shape reliably from a phone photo).
    hand_flag = False
    if form.get("hand_pale") == "1":
        add("Pale nails or palms (possible anemia clue)", 2,
            "Paleness in nails or palms can be a simple clue for low iron (anemia), which "
            "sometimes has an underlying cause worth checking.")
    if form.get("hand_yellow") == "1":
        add("Yellow tint to skin or eyes (possible jaundice)", 3,
            "Yellowing of skin or eyes (jaundice) usually points to a liver or bile-related "
            "issue that needs prompt medical attention.")
        hand_flag = True
    if form.get("hand_clubbing") == "1":
        add("Fingertip/nail shape changes or swelling (clubbing)", 3,
            "Clubbing (rounded, swollen fingertips) is a recognized clinical sign linked to "
            "several lung and heart conditions.")
        hand_flag = True

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
        "hand_flag": hand_flag,
        "ai": ai,
    }


LEVEL_COLORS = {
    "low": colors.HexColor("#2e8b64"),
    "medium": colors.HexColor("#c77f1d"),
    "high": colors.HexColor("#bb4444"),
}

LEVEL_MEANING = {
    "low": "Few known cancer risk factors apply to you right now. Keep up the healthy "
           "habits &mdash; and remember this score is not a medical test.",
    "medium": "Some known risk factors apply to you. That does <b>not</b> mean you have "
               "cancer &mdash; most people with risk factors never get it &mdash; but "
               "they're worth mentioning at your next doctor visit.",
    "high": "Several known risk factors apply to you. This is <b>not</b> a diagnosis "
            "&mdash; but booking a doctor's appointment to talk them through is a smart move.",
}


def build_pdf(r, app_name):
    """Render the same results shown on-screen into a downloadable PDF."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
    )
    styles = getSampleStyleSheet()
    navy = colors.HexColor("#16324c")
    muted = colors.HexColor("#5c6b78")

    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], textColor=navy, fontSize=18)
    h2_style = ParagraphStyle("H2Style", parent=styles["Heading2"], textColor=navy, fontSize=13, spaceBefore=14)
    body_style = ParagraphStyle("BodyStyle", parent=styles["Normal"], fontSize=10.5, leading=15)
    muted_style = ParagraphStyle("MutedStyle", parent=styles["Normal"], fontSize=9, leading=13, textColor=muted)
    small_note = ParagraphStyle("SmallNote", parent=styles["Normal"], fontSize=8.5, leading=12, textColor=muted)

    story = []
    story.append(Paragraph(app_name, title_style))
    story.append(Paragraph("Risk-Factor Assessment Results", muted_style))
    story.append(Spacer(1, 14))

    level_color = LEVEL_COLORS.get(r["level_class"], navy)
    score_style = ParagraphStyle("ScoreStyle", parent=styles["Normal"], fontSize=26, textColor=level_color, leading=30)
    story.append(Paragraph(f"Score: {r['total']} / {r['max_score']}  &mdash;  {r['level']} risk-factor level", score_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#d7e3ee")))
    story.append(Spacer(1, 10))

    story.append(Paragraph("What your level means", h2_style))
    story.append(Paragraph(LEVEL_MEANING.get(r["level_class"], ""), body_style))

    if r.get("hand_flag"):
        story.append(Paragraph("Your hand self-check", h2_style))
        story.append(Paragraph(
            "You noticed a <b>yellow tint</b> or a <b>change in fingertip or nail shape</b>. "
            "These aren't cancer tests, but doctors like to check them soon &mdash; book an "
            "appointment and describe exactly what you saw.", body_style))

    if r.get("red_flag"):
        story.append(Paragraph("About your symptoms", h2_style))
        story.append(Paragraph(
            "A symptom like <b>unexplained weight loss, a new lump, or unusual bleeding</b> "
            "that lasts 2+ weeks deserves a doctor's visit soon &mdash; whatever your score "
            "says.", body_style))

    if r.get("ai"):
        pct = r["ai"]["pct"]
        if pct >= 70:
            add_note = "It added <b>+3 points</b> &mdash; show that spot to a dermatologist."
        elif pct >= 50:
            add_note = "It added <b>+2 points</b> &mdash; show that spot to a dermatologist."
        else:
            add_note = "Reassuring, so it added <b>+0 points</b> &mdash; keep an eye on it."
        story.append(Paragraph("Your AI spot check", h2_style))
        story.append(Paragraph(
            f"The spot you tapped scored <b>{pct}% suspicious-like</b> ({100 - pct}% benign-like) "
            f"against the model's dermatology training images. {add_note}", body_style))
        story.append(Paragraph(
            "One small crop from a phone photo &mdash; an experiment, not an examination.",
            small_note))
    else:
        story.append(Paragraph("About your hand photo", h2_style))
        story.append(Paragraph(
            "No AI spot check this time, so your photo added <b>+0 points</b> &mdash; a photo "
            "alone can't show whether someone has cancer. In person, doctors can spot clues "
            "like nail shape and color changes that no website can judge.", body_style))

    if r.get("breakdown"):
        story.append(Paragraph("What added points", h2_style))
        for item in r["breakdown"]:
            row = Table(
                [[item["label"], f"+{item['points']}"]],
                colWidths=[4.6 * inch, 0.9 * inch],
            )
            row.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
                ("TEXTCOLOR", (0, 0), (0, 0), navy),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]))
            story.append(row)
            if item.get("explain"):
                story.append(Paragraph(item["explain"], small_note))
            story.append(HRFlowable(width="100%", color=colors.HexColor("#e8eef4")))

    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#d7e3ee")))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "<b>Not a diagnosis:</b> this student project counts general risk factors and compares "
        "photos to training images &mdash; it cannot detect cancer. Please talk to a healthcare "
        "professional about any concerns.", small_note))

    doc.build(story)
    buffer.seek(0)
    return buffer


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
    r = score_assessment(request.form)
    session["last_result"] = r
    return render_template("result.html", app_name=APP_NAME, r=r)


@app.route("/result/download")
def download_pdf():
    r = session.get("last_result")
    if not r:
        return redirect(url_for("index"))
    buffer = build_pdf(r, APP_NAME)
    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="cancer-risk-checker-results.pdf",
    )


@app.route("/skin-check")
def skin_check():
    return render_template("skin_check.html", app_name=APP_NAME)


@app.route("/health")
def health():
    return "OK"


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
