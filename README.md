# Health Assessment Website

A Python Flask website foundation for health assessments. The site presents a start screen with customizable text, asks 20 questions, and provides a percentage result indicating the likelihood of having a specific disease.

## Features

- Start screen with customizable introduction text
- 20-question assessment with progress tracking
- Yes/No answer format for each question
- Results page showing percentage risk
- Modern, responsive UI with gradient styling
- Easy customization of questions and disease type

## Local Setup Instructions

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Customize the assessment:**
   - Edit `app.py` to modify:
     - `DISEASE_NAME` - the name of the disease being assessed
     - `START_TEXT` - the introduction text on the start screen
     - `QUESTIONS` - the list of 20 questions to ask

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the website:**
   - Open your browser and navigate to `http://127.0.0.1:5000`

## Deployment Instructions

### Option 1: Deploy to Render (Free, Recommended)

1. **Create a GitHub repository** and push your code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/your-username/your-repo.git
   git push -u origin main
   ```

2. **Sign up for Render** at [render.com](https://render.com)

3. **Create a new Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will automatically detect it's a Python/Flask app
   - Set the following environment variables:
     - `SECRET_KEY`: Generate a random secret key (use: `python -c 'import secrets; print(secrets.token_hex(32))'`)
   - Click "Create Web Service"

4. **Your app will be deployed** and you'll get a URL like `https://your-app.onrender.com`

### Option 2: Deploy to Heroku (Free tier available)

1. **Install Heroku CLI** and sign up at [heroku.com](https://heroku.com)

2. **Login to Heroku:**
   ```bash
   heroku login
   ```

3. **Create a Heroku app:**
   ```bash
   heroku create your-app-name
   ```

4. **Set environment variables:**
   ```bash
   heroku config:set SECRET_KEY=your-random-secret-key
   ```

5. **Deploy:**
   ```bash
   git push heroku main
   ```

### Option 3: Deploy to Railway (Free)

1. **Sign up at [railway.app](https://railway.app)**

2. **Create a new project** and connect your GitHub repository

3. **Railway will automatically detect** it's a Python app and deploy it

4. **Add environment variable** `SECRET_KEY` in the project settings

## Customization

### Editing Questions
In `app.py`, modify the `QUESTIONS` list:
```python
QUESTIONS = [
    "Your custom question 1",
    "Your custom question 2",
    # ... up to 20 questions
]
```

### Changing Disease Name
In `app.py`, modify:
```python
DISEASE_NAME = "Your Disease Name"
```

### Modifying Start Text
In `app.py`, modify:
```python
START_TEXT = "Your custom introduction text"
```

### Adjusting Risk Calculation
The current calculation counts "yes" answers as risk factors. To modify this logic, edit the `result()` function in `app.py`.

## File Structure

```
.
├── app.py                 # Main Flask application
├── Procfile              # Deployment configuration
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore file
├── static/
│   └── style.css         # Website styling
└── templates/
    ├── base.html         # Base template
    ├── index.html        # Start screen
    ├── question.html     # Question page
    └── result.html       # Results page
```

## Notes

- This is a foundation/template website. All questions, text, and disease information should be customized before use.
- The assessment is for informational purposes only and should not replace professional medical advice.
- The `SECRET_KEY` environment variable is set automatically in production deployments.
