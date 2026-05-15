# Cancer Assessment Website

A Python App, or HTML website used to detect cancer. The goal of the project is to help people upload pictures of their hands, and answer a questionnare, Based on the given data it gives an inference of whether or not you have the likely chance of cancer with a ML model.

## Features for Prototype 0.1

- Start screen with customizable introduction text
- 20-question assessment with progress tracking
- Yes/No answer format for each question
- Results page showing percentage risk
- Modern, responsive UI with gradient styling

## Local Setup Instructions

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the website:**
   - Open your browser and navigate to `http://127.0.0.1:5000`

## Deployment Instructions

### Option 1: Deploy to Render

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

Made with Love in Saudi Arabia 🇸🇦
By Younus Hassen and Yousef Sherif
