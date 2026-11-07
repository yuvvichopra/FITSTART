# 🌱 FitStart – Personalized Fitness & Nutrition Platform

**FitStart** is a full-stack fitness and wellness web application designed to bring personalized workout planning, nutrition tracking, and daily habit monitoring into one platform.

The project focuses on helping users manage their fitness journey through structured training plans, nutritional targets, progress visualization, and recovery tracking.

🔗 **Live Demo:** https://fitstart-ywn7.onrender.com/  
💻 **GitHub Repository:** https://github.com/yuvvichopra/FITSTART

---

## ✨ Key Features

### 📊 1. Personalized Dashboard
- Weekly workout statistics.
- Daily calorie intake overview.
- Training volume visualization.
- Sleep and hydration tracking.
- Progress monitoring through interactive charts.

### 🏋️ 2. Personalized Workout Planning
- Workout plans based on fitness goals and experience level.
- Equipment-based exercise selection.
- Customizable training frequency.
- Exercise instructions, target muscles, sets, reps, and rest periods.
- Exercise substitutions.
- Progressive overload and recovery guidance.

### 🥗 3. Nutrition & Meal Planning
- Personalized daily calorie targets.
- Protein, carbohydrate, and fat targets.
- Vegetarian and dietary preference support.
- Meal planning based on food preferences and regional cuisine.
- Food logging with portion-based nutritional information.

### 💧 4. Habit & Recovery Tracking
- Daily water intake tracking.
- Sleep duration and quality monitoring.
- Daily step tracking.
- Workout completion records.
- Recovery feedback and personal notes.

### 👤 5. Profile & Personalization
- Age, height, and body-weight inputs.
- Activity-level selection.
- Fitness goal selection.
- Training equipment and frequency preferences.
- Dietary pattern, cooking facilities, and budget preferences.

---

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML, CSS, JavaScript |
| Templating | Jinja |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Database Hosting | Neon |
| Application Hosting | Render |
| Data Visualization | Chart.js |
| Deployment Server | Gunicorn |

### AI-Assisted Development Tools
- **Google Antigravity:** AI-assisted coding, implementation, and development workflow.
- **ChatGPT:** Project planning, brainstorming, debugging assistance, technical guidance, and iterative development.

---

## ⚙️ Development Methodology

FitStart was developed using a modular full-stack approach.

### 1. Requirement Analysis & Personalization
Identified the core requirements of a fitness management platform and designed user inputs around physical metrics, fitness goals, dietary preferences, and lifestyle constraints.

### 2. Backend Development
Used Flask to manage application routes, backend logic, user interactions, and communication between the frontend and database.

### 3. Frontend Development
Used HTML, CSS, JavaScript, and Jinja templates to create responsive pages, interactive forms, navigation, and dashboards.

### 4. Database Integration
Integrated PostgreSQL using SQLAlchemy ORM to manage structured application data and persistent storage.

### 5. Fitness & Nutrition Logic
Implemented evidence-informed approaches, including:

- **Mifflin-St Jeor Equation:** For estimating Basal Metabolic Rate (BMR).
- **Activity Multipliers:** For estimating Total Daily Energy Expenditure (TDEE).
- **Macronutrient Distribution:** For calculating daily protein, carbohydrate, and fat targets.
- **Progressive Overload:** Double-progression approach for workout progression.
- **RIR (Reps in Reserve):** To guide training effort.
- **Recovery Tracking:** Sleep, hydration, steps, and perceived recovery.

Nutrition and training calculations are estimates and should be adjusted according to individual requirements and progress.

### 6. Data Visualization
Integrated Chart.js to display workout volume, calorie intake, and recovery trends through interactive charts.

### 7. Cloud Deployment
- Deployed the Flask application on Render.
- Configured Neon PostgreSQL as the cloud database.
- Used environment variables for configuration and sensitive credentials.
- Used Gunicorn as the production application server.

---

## 🏗️ Application Architecture

```text
                 USER
                   |
                   v
          FRONTEND INTERFACE
       HTML + CSS + JavaScript
                   |
                   v
             FLASK BACKEND
          Routes + Application Logic
                   |
                   v
             SQLAlchemy ORM
                   |
                   v
           NEON POSTGRESQL
            Cloud Database

                   |
                   v
          CHART.JS DASHBOARD
          Progress Visualization
```

---

## 🚀 Getting Started

Follow these steps to run FitStart locally.

### Prerequisites

- Python 3.10+
- pip
- PostgreSQL database or Neon account
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/yuvvichopra/FITSTART.git
```

### 2. Navigate to the Project Directory

```bash
cd FITSTART
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows:**
```bash
venv\Scripts\activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file if your local configuration uses dotenv, or configure the variables directly in your environment.

```env
SECRET_KEY=your_secret_key
DATABASE_URL=your_postgresql_connection_string
```

**Important:** Never commit your `.env` file, database credentials, or secret keys to GitHub.

### 6. Run the Application

The production entry point is:

```bash
gunicorn wsgi:app
```

For local development, use the Flask development entry point configured by your application.

---

## ☁️ Deployment

FitStart is deployed using:

| Service | Purpose |
|---|---|
| Render | Flask application hosting |
| Neon | Managed PostgreSQL database |
| Gunicorn | Production WSGI server |
| GitHub | Source code management and version control |

### Deployment Configuration

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
gunicorn wsgi:app
```

Configure the required environment variables in Render's Environment settings.

---

## 🔐 Security & Data Management

- Sensitive configuration is managed through environment variables.
- Database operations are handled through SQLAlchemy.
- PostgreSQL provides persistent cloud-based data storage.
- Database credentials and secret keys should never be exposed in source code.

---

## 🎯 Project Objective

FitStart started as a personal project to combine my interest in fitness with my learning journey in software development.

The objective was to build a practical, user-focused application while gaining hands-on experience with:

- Full-stack web development.
- Backend application architecture.
- Relational database integration.
- Cloud deployment and configuration.
- Data visualization.
- AI-assisted software development.

---

## 🔮 Future Improvements

- Progressive fitness analytics.
- More advanced workout customization.
- Improved nutrition recommendations.
- Mobile-friendly experience and PWA support.
- Enhanced recovery insights.
- Additional exercise and food database integrations.

---

## ⚠️ Disclaimer

FitStart is an educational and personal software project. Its workout and nutrition recommendations are informational estimates, not medical advice. Users should consult qualified professionals when they need individualized medical or dietary guidance.

---

## 👨‍💻 Developer

**Yuvraj Chopra**  
B.Tech – Computer Science Engineering (AI & ML)

Interested in software development, artificial intelligence, fitness technology, and building practical solutions through code.

**Built with Python, Flask, PostgreSQL, and AI-assisted development.**

⭐ If you find this project interesting, consider giving the repository a star!
