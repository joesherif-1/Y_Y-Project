import os
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration - EDIT THESE VALUES
DISEASE_NAME = "Example Disease"
START_TEXT = "Welcome to the health assessment tool. This questionnaire will help determine your risk level."
QUESTIONS = [
    "Question 1",
    "Question 2",
    "Question 3",
    "Question 4",
    "Question 5",
    "Question 6",
    "Question 7",
    "Question 8",
    "Question 9",
    "Question 10",
    "Question 11",
    "Question 12",
    "Question 13",
    "Question 14",
    "Question 15",
    "Question 16",
    "Question 17",
    "Question 18",
    "Question 19",
    "Question 20",
]

@app.route('/')
def index():
    return render_template('index.html', disease_name=DISEASE_NAME, start_text=START_TEXT)

@app.route('/question/<int:question_num>', methods=['GET', 'POST'])
def question(question_num):
    if question_num < 1 or question_num > len(QUESTIONS):
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        answer = request.form.get('answer')
        if answer:
            if 'answers' not in session:
                session['answers'] = {}
            session['answers'][str(question_num)] = answer
            
            if question_num < len(QUESTIONS):
                return redirect(url_for('question', question_num=question_num + 1))
            else:
                return redirect(url_for('result'))
    
    return render_template('question.html', 
                         question_num=question_num, 
                         question=QUESTIONS[question_num - 1],
                         total_questions=len(QUESTIONS),
                         disease_name=DISEASE_NAME)

@app.route('/result')
def result():
    if 'answers' not in session:
        return redirect(url_for('index'))
    
    answers = session['answers']
    
    # Calculate percentage based on "yes" answers
    yes_count = sum(1 for answer in answers.values() if answer.lower() == 'yes')
    percentage = (yes_count / len(QUESTIONS)) * 100
    
    # Clear session for next use
    session.clear()
    
    return render_template('result.html', 
                         percentage=round(percentage, 1),
                         disease_name=DISEASE_NAME)

if __name__ == '__main__':
    app.run(debug=True)
