# CompileMate

CompileMate is a gamified competitive programming platform designed to help users master coding skills, participate in contests, and earn real rewards. It features problem solving, leaderboards, user profiles, streaks, badges, a marketplace, and more—all in a modern, user-friendly interface.

---

## 🚀 Features

### 1. **User Authentication & Profiles**
- **Sign Up / Login:** Secure registration and login with email verification.
- **Profile Page:** View your stats, badges, streaks, recent activity, and rank.
- **Public Profiles:** (Optional) View other users' achievements and stats.

### 2. **Problem Solving**
- **Problem List:** Browse and filter problems by difficulty, tags, or search.
- **Problem Details:** View full problem statements, constraints, examples, and starter code in multiple languages.
- **Code Editor:** Submit solutions in Python, C++, Java, or JavaScript.
- **Submissions:** View your submission history, status, and detailed results.
- **Leaderboard:** See top solvers and your global rank.

### 3. **Contests**
- **Contest List:** Participate in weekly/monthly contests.
- **Live Leaderboard:** Track your rank in real time during contests.
- **Contest History:** See your past contest participation and performance.

### 4. **Gamification**
- **MateCoins:** Earn coins for solving problems and contests. Redeem them in the marketplace.
- **XP & Levels:** Gain XP to level up and unlock new features.
- **Badges & Achievements:** Earn badges for streaks, milestones, and special achievements.
- **Streaks:** Maintain daily/weekly solving streaks for extra rewards.

### 5. **Marketplace**
- **Rewards:** Redeem MateCoins for real-world vouchers and digital rewards.
- **Badge Gallery:** View all badges and how to earn them.

### 6. **Resume Scanner**
- **Upload Resume:** Scan your resume for skills and get instant feedback.
- **Skill Extraction:** See which skills are detected and get improvement tips.

### 7. **Support & Community**
- **Support Chat:** Get help from admins via a built-in chat system.
- **Discussion (Planned):** Discuss problems and solutions with the community.

### 8. **Admin Tools**
- **Admin Dashboard:** Manage users, problems, contests, and rewards.
- **Analytics:** Track platform usage, problem popularity, and user growth.

---

## 🛠️ Tech Stack
- **Backend:** Django, Django REST Framework
- **Frontend:** Django Templates, Tailwind CSS, Alpine.js
- **Database:** PostgreSQL (recommended), SQLite (dev)
- **Async/Real-time:** Django Channels (for chat, optional)
- **Task Queue:** Celery + Redis (for background tasks, optional)
- **Deployment:** Gunicorn, Nginx, Render.com

---

## ⚙️ Local Setup

1. **Clone the repo:**
   ```bash
   git clone https://github.com/yourusername/Compile-Mate.git
   cd Compile-Mate
   ```
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```
5. **Create a superuser (admin):**
   ```bash
   python manage.py createsuperuser
   ```
6. **Add sample problems:**
   ```bash
   python manage.py add_sample_problems
   ```
7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
8. **Access the app:**
   Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## 🚀 Deployment (Render.com Example)

1. **Push your code to GitHub.**
2. **Create a new Web Service on Render:**
   - Connect your repo
   - Set build command:
     ```
     pip install -r requirements.txt
     python manage.py collectstatic --noinput
     python manage.py migrate
     ```
   - Set start command:
     ```
     gunicorn compilemate.wsgi:application
     ```
3. **Add environment variables:**
   - `DJANGO_SECRET_KEY`, `DATABASE_URL`, etc.
4. **Add a PostgreSQL database on Render and connect it.**
5. **Set up static files:**
   - Use [WhiteNoise](https://whitenoise.evans.io/en/stable/) for static file serving.
6. **Deploy!**

---

## 🤝 Contributing

1. Fork the repo and create your branch: `git checkout -b feature/your-feature`
2. Commit your changes: `git commit -am 'Add new feature'`
3. Push to the branch: `git push origin feature/your-feature`
4. Open a pull request

---

## 📄 License
This project is licensed under the MIT License.

---

## 🙋 FAQ / Support
- For questions, open an issue or use the in-app support chat.
- For feature requests, open a GitHub issue.

---

**Happy Coding! 🚀** 
