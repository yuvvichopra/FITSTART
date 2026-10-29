# 🌿 FitStart: Evidence-Based Personal Fitness & Nutrition Engine

> **A soundly engineered, scientific training and nutrition platform built with Flask, SQLAlchemy, MySQL/SQLite, and Chart.js for real-world student, collegiate, and athlete constraints.**

---

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Key Architecture & Technology Stack](#key-architecture--technology-stack)
3. [Core Systems & Capabilities](#core-systems--capabilities)
   - [Personalized Onboarding Questionnaire](#1-personalized-onboarding-questionnaire)
   - [Deterministic Workout Recommendation Engine](#2-deterministic-workout-recommendation-engine)
   - [Tailored Indian & Global Nutrition Engine](#3-tailored-indian--global-nutrition-engine)
   - [Workout Logging & Adaptive Progression Coaching](#4-workout-logging--adaptive-progression-coaching)
   - [Daily Habits & Somatic Recovery Tracking](#5-daily-habits--somatic-recovery-tracking)
   - [Dashboard Analytics & Objective Weekly Review](#6-dashboard-analytics--objective-weekly-review)
   - [Structured Scientific Research Library](#7-structured-scientific-research-library)
4. [Security & Data Isolation](#security--data-isolation)
5. [Local Development & Setup Guide](#local-development--setup-guide)
6. [Database Configuration (MySQL & SQLite)](#database-configuration-mysql--sqlite)
7. [Running the Test Suite](#running-the-test-suite)
8. [Restarting the Local Application](#restarting-the-local-application)

---

## 📌 Project Overview
FitStart is designed to eliminate generic routines and hallucinatory AI advice. Engineered with rigor and academic integrity, FitStart translates peer-reviewed exercise physiology and public-health nutrition guidelines into deterministic, transparent software.

FitStart accounts for real constraints faced by collegiate students and working adults:
- **Hostel & Mess Logistics:** Prioritizes accessible Indian staples (oats, sattu, boiled eggs, curd/dahi, dal, roti, bananas, peanut butter).
- **Equipment Flexibility:** Dynamically structures workouts for commercial gyms, hostel gyms with basic dumbbells, home setups, or pure calisthenics/bodyweight.
- **Joint Safety & Pain Substitutions:** Automatically detects joint sensitivities (deep squats, lower back deadlifts, shoulder overhead pressing) and swaps in biomechanically safer variations with technique cues.
- **Adaptive Recovery:** Suppresses progressive overload and prescribes recovery/deload protocols whenever poor sleep (< 6h) or elevated soreness is reported.

---

## 🛠️ Key Architecture & Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend Framework** | Python 3.14 + Flask 3.0.3 | Application factory, modular blueprint routing |
| **ORM & Database** | SQLAlchemy 2.1 + Flask-SQLAlchemy 3.1 | Relational models with cascade rules, indexes, and constraints |
| **Database Engines** | MySQL (PyMySQL) & SQLite | Primary production MySQL support with seamless zero-friction local SQLite fallback |
| **Authentication & Security** | Flask-Login + Werkzeug Scrypt/PBKDF2 | Session cookies (HttpOnly, SameSite), CSRF protection via Flask-WTF |
| **Frontend UI** | HTML5, CSS3, JavaScript (ES6+), Jinja2 | Brand identity: Warm Neutrals (`#FBF9F5`), Forest Green (`#1E3A2F`), Charcoal (`#1C2321`), Muted Sage (`#8DA399`) |
| **Data Visualizations** | Chart.js | Interactive training volume, calorie trends, and sleep/hydration charts |
| **Test Suite** | pytest 8.4 | Comprehensive test coverage across 21 test scenarios |

---

## 🚀 Core Systems & Capabilities

### 1. Personalized Onboarding Questionnaire
A multi-step interactive wizard tracking 8 distinct physiological and lifestyle dimensions:
- **Personal Metrics:** Age, gender, height, bodyweight, measurement units (metric vs imperial), regional food preferences, activity multipliers.
- **Experience:** Beginner, occasional, consistent, experienced, training history, exercise confidence rating (1–5), preferred session duration (30–90m).
- **Goals:** Primary goal (fat loss, muscle gain, body recomp, strength, endurance, general fitness, return to training) + multiple secondary goals.
- **Equipment:** Setting (commercial gym, hostel gym, home, bodyweight) and gear checklist (barbells, dumbbells, cables, bands, bench, pull-up bar).
- **Schedule:** 2 to 6 training days/week, preferred days, workout timing (morning, afternoon, evening), cardio choices, college/work constraints.
- **Diet & Logistics:** Vegetarian, vegan, eggetarian, non-vegetarian, strict allergen filtering (peanuts, dairy, gluten, soy, eggs, shellfish), budget tier, meal frequency (2–5 meals/day), cooking facilities (hostel mess vs full kitchen).
- **Recovery & Safety:** Typical sleep duration, step target, movements causing joint discomfort (knee, lower back, shoulder), injuries, and sensitive medical limitations.
- **Preferences:** Priority muscle groups, coaching feedback style (encouraging, analytical, direct, gentle), desired training difficulty.

### 2. Deterministic Workout Recommendation Engine
Synthesizes a complete rules-based program:
- **Supported Splits:**
  - 2-Day Foundational Full-Body
  - 3-Day Full-Body Synergy Split
  - 4-Day Upper / Lower Periodized Split
  - 5-Day Hybrid Split
  - 6-Day Push / Pull / Legs (PPL) Split
  - Calisthenics & Minimal Equipment Split
  - Conservative Return-to-Training Protocol
- **Exercise Architecture:** Warm-up instructions (RAMP framework), targeted exercises, sets, reps, rest intervals (seconds), RPE/RIR guidance, technique execution cues, and verified substitution alternatives.
- **Plan Versioning & Restoration:** Old plans are safely archived in database history when a new plan is generated. Users can inspect past versions and restore any previous plan at any time.

### 3. Tailored Indian & Global Nutrition Engine
- **Documented Energy Estimation:**
  - **BMR:** Validated Mifflin-St Jeor formula (`10*W + 6.25*H - 5*A ± offset`).
  - **TDEE:** Physical activity multipliers (1.20 to 1.725).
  - **Calorie Targets:** Safe, evidence-based deficits for fat loss (15-20%, capped at sustainable floors of 1500 kcal for men / 1250 kcal for women); lean surpluses for hypertrophy (+10-15%); maintenance for recomp/general health.
  - **Underage Safeguard:** Explicitly flags users under 18 with warnings contraindicating severe caloric restriction during developmental growth.
- **Macronutrient Science:**
  - Protein: 1.6 to 2.2 g/kg body weight (ACSM/ISSN guidelines for active adults).
  - Dietary Fats: 22–28% of total daily energy.
  - Carbohydrates: Remaining calories for glycogen and energy replenishment.
  - Dietary Fiber: 25–35g daily (ICMR & WHO standards).
- **Verified Food Database:** Realistic nutrient data per 100g for Indian staples (dals, roti, rice, paneer, curd, soya chunks, boiled eggs, chicken, sattu, roasted chana, oats, fruits, nuts).
- **Interactive Meal Editor:** Edit portion weights in grams with immediate recalculation of calories, protein, carbs, and fat from stored data.

### 4. Workout Logging & Adaptive Progression Coaching
- Log individual workouts with exercises, sets, weight (kg), reps completed, RPE (1–10), and form notes.
- **All-Time Personal Records (PRs):** Computes estimated 1-Rep Max (1RM) using the validated Epley formula: `1RM = Weight * (1 + Reps / 30)`.
- **Double Progression Suggestions:** When all sets hit target repetitions with controlled exertion (RPE <= 8), the system suggests increasing weight by 2.5kg.
- **Safety Overload Gate:** If the user logs fatigue, muscle soreness, or short sleep (< 6h), the system suppresses overload and advises maintaining load or deloading.

### 5. Daily Habits & Somatic Recovery Tracking
- **Hydration Tracker:** Visual daily water logging with quick `+250ml` and `+500ml` buttons.
- **Sleep & Restfulness:** Records sleep duration (hours) and subjective restfulness quality (1–5 scale).
- **Daily Steps & Activity:** Compares recorded steps against profile targets.
- **Somatic Recovery State:** Great, Good, Moderate, Fatigued, Sore, Pain.
- **Data Integrity:** Distinctly handles unlogged days versus zero values (an unlogged day is never assumed to be zero food or activity).

### 6. Dashboard Analytics & Objective Weekly Review
- **Chart.js Visualizations:**
  - Training Volume Trend (kg moved over time).
  - Calorie & Macronutrient Intake vs Dotted Target Line.
  - Sleep Duration & Hydration overlay trends.
- **Objective Weekly Review:**
  - Synthesizes recorded trends over the previous 7 days.
  - Highlights true accomplishments and consistency metrics.
  - Explicitly reports tracking gaps (e.g., "Food recorded on only 3 days; more tracking will refine energy estimates").
  - Suggests transparent adjustments for the upcoming week.

### 7. Structured Scientific Research Library
Hosted locally at `/research`, citing:
- **ACSM (American College of Sports Medicine):** Resistance training frequency, volume, and cardiorespiratory health.
- **NSCA (National Strength and Conditioning Association):** Periodization, progressive overload (2-for-2 rule), and technique.
- **ICMR - National Institute of Nutrition (NIN) India:** Dietary Guidelines for Indians, cereal-pulse amino acid complementarity, and fiber targets.
- **WHO (World Health Organization):** Weekly physical activity thresholds (150–300 min moderate).
- **PubMed Systematic Reviews (Morton et al.):** Protein distribution and hypertrophy meta-analyses.
- **wger Open Source Fitness:** Anatomical taxonomy for exercise substitutions.

---

## 🔒 Security & Data Isolation
- **Tenant Isolation:** All database queries for workout plans, meal items, daily logs, and habit records strictly enforce `user_id == current_user.id`. Cross-user access or deletion attempts result in immediate HTTP 404/403 rejections.
- **CSRF Defense:** Flask-WTF tokens protect all state-modifying POST requests.
- **Password Security:** Hashes passwords with salt using Werkzeug (`scrypt` / `pbkdf2:sha256`).
- **Session Protection:** `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SAMESITE = 'Lax'`.
- **Credential Hygiene:** Database secrets and environment keys are loaded exclusively from `.env` (ignored by Git).

---

## 💻 Local Development & Setup Guide

### Prerequisites
- Python 3.10+ (tested and verified on Python 3.14.2)
- Git
- Windows PowerShell or Command Prompt

### Step 1: Clone or Navigate to the Project Directory
```powershell
cd "c:\Users\Yuvraj Chopra\Desktop\FITSTART"
```

### Step 2: Install Required Dependencies
All required libraries are listed in `requirements.txt`:
```powershell
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Default `.env` configuration:
```ini
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=fitstart-super-secret-key-change-in-production-2026
DATABASE_URL=sqlite:///fitstart.db
FLASK_RUN_HOST=127.0.0.1
FLASK_RUN_PORT=5000
```

---

## 🗄️ Database Configuration (MySQL & SQLite)

FitStart supports both **MySQL** (preferred) and **SQLite** (local zero-setup development):

### Using SQLite (Default Zero-Friction Setup)
No additional installation required. The database file `fitstart.db` will be initialized automatically in the root folder upon first startup.
```ini
DATABASE_URL=sqlite:///fitstart.db
```

### Using MySQL
To use MySQL:
1. Ensure your local MySQL server is running on port 3306.
2. Create a database:
   ```sql
   CREATE DATABASE fitstart CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. Update `.env` with your MySQL connection string (using the included `pymysql` driver):
   ```ini
   DATABASE_URL=mysql+pymysql://username:password@localhost:3306/fitstart
   ```
4. FitStart will automatically create and seed all tables upon application start.

---

## 🧪 Running the Test Suite

Execute the full automated test suite covering all 21 verification points:

```powershell
python -m pytest -v
```

Expected output:
```
tests/test_coaching_and_security.py::test_user_data_isolation PASSED
tests/test_coaching_and_security.py::test_adaptive_coaching_rules PASSED
tests/test_coaching_and_security.py::test_invalid_inputs_resilience PASSED
tests/test_coaching_and_security.py::test_external_api_failure_resilience PASSED
tests/test_logging_and_habits.py::test_workout_logging_and_pr_calculations PASSED
tests/test_logging_and_habits.py::test_habit_tracking_and_water_sleep PASSED
tests/test_logging_and_habits.py::test_progress_dashboard_and_chart_data PASSED
tests/test_logging_and_habits.py::test_empty_datasets_handling PASSED
tests/test_nutrition_personalization.py::test_nutrition_calculations_and_safety PASSED
tests/test_nutrition_personalization.py::test_dietary_restrictions PASSED
tests/test_nutrition_personalization.py::test_food_allergies_exclusion PASSED
tests/test_nutrition_personalization.py::test_meal_portion_editing_and_recalculations PASSED
tests/test_startup_and_auth.py::test_application_startup PASSED
tests/test_startup_and_auth.py::test_registration_and_login PASSED
tests/test_startup_and_auth.py::test_duplicate_registration_prevention PASSED
tests/test_startup_and_auth.py::test_profile_persistence PASSED
tests/test_startup_and_auth.py::test_questionnaire_validation PASSED
tests/test_workout_personalization.py::test_different_workout_goals PASSED
tests/test_workout_personalization.py::test_equipment_based_substitutions PASSED
tests/test_workout_personalization.py::test_different_training_schedules PASSED
tests/test_workout_personalization.py::test_plan_versioning_and_restoration PASSED

====================== 21 passed in ~4s ======================
```

You can also run the full end-to-end integration verification script:
```powershell
python verify_live_app.py
```

---

## 🏃 Restarting the Local Application

### Exact Windows PowerShell Startup Command:
```powershell
cd "c:\Users\Yuvraj Chopra\Desktop\FITSTART"
python run.py
```

### Accessing the Application:
Once started, open your web browser and navigate to:
```
http://127.0.0.1:5000/
```

### Quick Workflow Tour:
1. **Register / Log In:** Click **Get Started** or visit `http://127.0.0.1:5000/auth/register`.
2. **Onboarding Questionnaire:** Answer the 8 steps regarding your experience, schedule, diet, and joint safety.
3. **Workout Plan:** Visit `/workout/plan` to view your personalized weekly split, warm-up cues, rest periods, and substitutions.
4. **Nutrition Plan:** Visit `/nutrition/plan` to see your calculated BMR, TDEE, macro distribution, and meal plan. Edit portions directly to recalculate totals.
5. **Log a Workout:** Record sets, weights, and RPE at `/workout/log`.
6. **Track Daily Habits:** Log water, sleep, and recovery soreness at `/habits/tracker`.
7. **View Dashboard & Weekly Review:** Inspect interactive volume and calorie charts on `/dashboard/` and read your weekly summary on `/dashboard/weekly-review`.
8. **Explore Evidence:** Visit `/research` to read the academic consensus guidelines powering FitStart.
