# 🚀 Compile-Mate

A comprehensive online coding platform built with Django, featuring competitive programming, collaborative learning, and community engagement tools.

![Python](https://img.shields.io/badge/Python-3.13.7-blue.svg)
![Django](https://img.shields.io/badge/Django-5.1.2-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [Deployment](#-deployment)
- [Project Structure](#-project-structure)
- [Admin Panel](#-admin-panel)
- [API Endpoints](#-api-endpoints)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🎯 Core Features

#### **Problem Solving**
- 34+ coding problems across multiple difficulty levels (Easy, Medium, Hard)
- Real-time code execution with multiple test cases
- Support for multiple programming languages (Python, Java, C++, JavaScript)
- Detailed problem descriptions with constraints and examples
- Submission history and performance tracking

#### **Contests & Competitions**
- Timed coding contests
- Leaderboard system
- Contest analytics and performance metrics
- Past contest archive

#### **User Profiles**
- Comprehensive user profiles with statistics
- Activity tracking and progress visualization
- Problem-solving history
- Achievements and badges

### 🎓 Learning & Growth

#### **Learning Paths**
- Structured learning roadmaps
- Topic-wise problem organization
- Progress tracking
- Enrollment system

#### **Certifications**
- Course completion certificates
- PDF certificate generation
- Achievement validation
- Certificate download functionality

#### **Code Reviews**
- Submit code for peer review
- Provide detailed feedback
- Comment system
- Review history

### 👥 Collaboration & Community

#### **CodeConnect (Live Collaboration)**
- **Video Calls**: Real-time WebRTC video communication
- **Whiteboard**: Interactive canvas for drawing and explanations
- **Live Code Editor**: Monaco Editor with syntax highlighting
- **Screen Sharing**: Share your screen with collaborators
- Room-based collaboration system

#### **Social Feed**
- Create and share posts
- Like and comment functionality
- Follow other users
- Activity feed

#### **Discussion Forums**
- Topic-based discussions
- Upvote/downvote system
- Comment threads
- Search functionality

#### **Snippets Library**
- Save code snippets
- Syntax highlighting
- Public/private visibility
- Tag-based organization

### 💼 Career Tools

#### **Job Board**
- Job postings from companies
- Application tracking
- Company profiles
- Filter by location, experience, salary

#### **Resume Scanner**
- Upload and analyze resumes
- ATS score calculation
- Keyword matching
- Improvement suggestions

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 5.1.2
- **Database**: PostgreSQL
- **ORM**: Django ORM
- **Authentication**: Django Auth System
- **Task Queue**: (Ready for Celery integration)

### Frontend
- **HTML5 & CSS3**
- **Tailwind CSS**: Utility-first CSS framework
- **Alpine.js**: Lightweight JavaScript framework
- **Chart.js**: Data visualization
- **Monaco Editor**: Code editor (VS Code editor)
- **Lucide Icons**: Modern icon library

### Real-time Features
- **WebRTC**: Video/audio communication
- **Canvas API**: Whiteboard functionality
- **JavaScript**: Dynamic interactions

### Deployment
- **Platform**: Render.com
- **Server**: Gunicorn WSGI server
- **Static Files**: WhiteNoise middleware
- **Database**: PostgreSQL on Render

## 📥 Installation

### Prerequisites

- Python 3.13.7 or higher
- PostgreSQL 12 or higher
- Git
- pip (Python package manager)

### Local Setup

1. **Clone the Repository**

```bash
git clone https://github.com/HarshaRockzz/Compile-Mate.git
cd Compile-Mate
```

2. **Create Virtual Environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

4. **Set Up PostgreSQL Database**

```sql
-- Open PostgreSQL shell
CREATE DATABASE compilemate_db;
CREATE USER compilemate_user WITH PASSWORD 'your_password';
ALTER ROLE compilemate_user SET client_encoding TO 'utf8';
ALTER ROLE compilemate_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE compilemate_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE compilemate_db TO compilemate_user;
```

5. **Configure Environment Variables**

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_NAME=compilemate_db
DATABASE_USER=compilemate_user
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
```

6. **Update Settings**

Edit `compilemate/settings.py` to use environment variables:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'compilemate_db',
        'USER': 'compilemate_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

7. **Run Migrations**

```bash
python manage.py migrate
```

8. **Create Superuser**

```bash
python manage.py createsuperuser
```

9. **Load Sample Data** (Optional)

```bash
python manage.py seed_problems
```

## ⚙️ Configuration

### Database Configuration

The application supports both local PostgreSQL and cloud databases via `DATABASE_URL`:

```python
# For local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'compilemate_db',
        'USER': 'compilemate_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# For production (Render)
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://compilemate_user:password@localhost:5432/compilemate_db',
        conn_max_age=600
    )
}
```

### Static Files

```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Media Files

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

## 🚀 Running the Application

### Development Server

```bash
# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Run server
python manage.py runserver
```

Access the application at: `http://localhost:8000`

### Admin Panel

Access the admin panel at: `http://localhost:8000/admin`

Use the superuser credentials you created.

## 🌐 Deployment

### Deploying to Render

1. **Push Code to GitHub** (Already done! ✅)

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up or log in
   - Connect your GitHub account

3. **Deploy via Blueprint**
   - Click "New +" → "Blueprint"
   - Select the `Compile-Mate` repository
   - Render will detect `render.yaml`
   - Click "Apply"

4. **Environment Variables** (Auto-configured via `render.yaml`)
   - `DATABASE_URL`: Auto-generated from PostgreSQL service
   - `SECRET_KEY`: Auto-generated
   - `DEBUG`: False
   - `ALLOWED_HOSTS`: Your Render domain
   - `CSRF_TRUSTED_ORIGINS`: Your Render domain

5. **Wait for Deployment**
   - Build process: ~5-10 minutes
   - Database creation: ~2 minutes
   - Total time: ~10-15 minutes

6. **Access Your Application**
   - URL: `https://compilemate.onrender.com` (or your custom domain)
   - Admin: `https://compilemate.onrender.com/admin`

### Manual Deployment Steps

If not using the blueprint:

```bash
# Build command
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

# Start command
gunicorn compilemate.wsgi:application
```

## 📁 Project Structure

```
Compile-Mate/
├── compilemate/              # Main project directory
│   ├── settings.py          # Django settings
│   ├── urls.py              # Root URL configuration
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
│
├── users/                    # User management app
│   ├── models.py            # User model extensions
│   ├── views.py             # Authentication views
│   ├── forms.py             # User forms
│   └── admin.py             # User admin customization
│
├── problems/                 # Problem solving app
│   ├── models.py            # Problem, Submission, TestCase models
│   ├── views.py             # Problem views
│   ├── executors.py         # Code execution logic
│   └── management/          # Management commands
│       └── commands/
│           └── seed_problems.py
│
├── contests/                 # Contest management app
│   ├── models.py            # Contest, Participation models
│   ├── views.py             # Contest views
│   └── admin.py             # Contest admin
│
├── learning_paths/           # Learning paths app
│   ├── models.py            # LearningPath, PathEnrollment models
│   ├── views.py             # Learning path views
│   └── admin.py             # Learning path admin
│
├── certifications/           # Certifications app
│   ├── models.py            # Certificate models
│   ├── views.py             # Certificate generation
│   └── pdf_generator.py     # PDF creation logic
│
├── code_reviews/             # Code review system
│   ├── models.py            # CodeReviewRequest, CodeReview models
│   ├── views.py             # Review views
│   └── admin.py             # Review admin
│
├── social_feed/              # Social networking features
│   ├── models.py            # Post, Comment models
│   ├── views.py             # Feed views
│   └── admin.py             # Feed admin
│
├── snippets/                 # Code snippets library
│   ├── models.py            # Snippet models
│   ├── views.py             # Snippet CRUD views
│   └── admin.py             # Snippet admin
│
├── collaboration/            # CodeConnect features
│   ├── models.py            # CollaborationRoom models
│   ├── views.py             # Room management
│   └── admin.py             # Collaboration admin
│
├── job_portal/               # Job board
│   ├── models.py            # JobPosting, Application models
│   ├── views.py             # Job views
│   └── admin.py             # Job admin
│
├── resume_scanner/           # Resume analysis
│   ├── models.py            # Resume models
│   ├── views.py             # Resume scanning logic
│   └── scanner.py           # ATS scoring algorithm
│
├── templates/                # HTML templates
│   ├── base.html            # Base template
│   ├── home.html            # Homepage
│   ├── problems/            # Problem templates
│   ├── contests/            # Contest templates
│   ├── learning_paths/      # Learning path templates
│   ├── certifications/      # Certificate templates
│   ├── code_reviews/        # Review templates
│   ├── social_feed/         # Social feed templates
│   ├── snippets/            # Snippet templates
│   └── collaboration/       # Collaboration templates
│
├── static/                   # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
│
├── media/                    # User-uploaded files
│   ├── avatars/
│   ├── certificates/
│   └── resumes/
│
├── requirements.txt          # Python dependencies
├── runtime.txt              # Python version for Render
├── Procfile                 # Process file for deployment
├── render.yaml              # Render deployment configuration
├── build.sh                 # Build script for Render
├── manage.py                # Django management script
└── README.md                # This file
```

## 🔧 Admin Panel

### Access

URL: `/admin`

### Features

#### **Enhanced User Management**
- List display: Username, Email, Full Name, Join Date, Status
- Filters: Staff status, Superuser status, Active status
- Search: Username, Email, First Name, Last Name
- Actions: Activate/Deactivate users, Make staff
- Inline editing of profiles

#### **Advanced Problem Management**
- List display: Title, Difficulty, Status, Test Cases, Created Date
- Filters: Difficulty, Created Date
- Search: Title, Description
- Actions: Publish/Unpublish problems, Bulk test case creation
- Inline test case editor
- Rich text description with Markdown support
- Constraints section
- Tag management

#### **Contest Management**
- List display: Name, Start Time, Duration, Participants
- Filters: Start Date, Status
- Search: Name, Description
- Actions: Start/End contests
- Participant management
- Problem assignment

#### **Submission Tracking**
- List display: User, Problem, Language, Status, Test Cases
- Filters: Status, Language, Submission Date
- Search: User, Problem
- View code and test results
- Performance metrics

#### **Learning Path Management**
- Course creation and editing
- Progress tracking
- Enrollment management
- Certificate issuance

#### **Certification Management**
- Certificate templates
- Manual certificate generation
- View and download certificates
- User certificate history

#### **Code Review Management**
- Review request moderation
- Assign reviewers
- Track review status
- View feedback

#### **Job Portal Management**
- Job posting creation
- Application tracking
- Company management
- Filter by status

## 🔗 API Endpoints

### Authentication
- `POST /users/login/` - User login
- `POST /users/register/` - User registration
- `GET /users/logout/` - User logout
- `GET /users/profile/<username>/` - View profile

### Problems
- `GET /problems/` - List all problems
- `GET /problems/<id>/` - View problem details
- `POST /problems/<id>/submit/` - Submit solution
- `GET /problems/<id>/submissions/` - View submissions

### Contests
- `GET /contests/` - List all contests
- `GET /contests/<id>/` - View contest details
- `POST /contests/<id>/register/` - Register for contest
- `GET /contests/<id>/leaderboard/` - View leaderboard

### Learning Paths
- `GET /learning-paths/` - List learning paths
- `GET /learning-paths/<id>/` - View path details
- `POST /learning-paths/<id>/enroll/` - Enroll in path

### Certifications
- `GET /certifications/` - List available certifications
- `GET /certifications/my-certificates/` - View user certificates
- `GET /certifications/<id>/download/` - Download certificate PDF

### Code Reviews
- `GET /code-reviews/` - List review requests
- `POST /code-reviews/submit/` - Submit code for review
- `POST /code-reviews/<id>/review/` - Submit review
- `POST /code-reviews/<id>/comment/` - Add comment

### Social Feed
- `GET /social/` - View social feed
- `POST /social/post/create/` - Create post
- `POST /social/post/<id>/like/` - Like post
- `POST /social/post/<id>/comment/` - Comment on post

### Snippets
- `GET /snippets/` - List snippets
- `GET /snippets/<id>/` - View snippet
- `POST /snippets/create/` - Create snippet
- `PUT /snippets/<id>/edit/` - Edit snippet
- `DELETE /snippets/<id>/delete/` - Delete snippet

### Collaboration
- `GET /collaborate/` - List collaboration rooms
- `POST /collaborate/create/` - Create room
- `GET /collaborate/room/<id>/` - Join room
- WebRTC signaling endpoints

### Job Portal
- `GET /jobs/` - List job postings
- `GET /jobs/<id>/` - View job details
- `POST /jobs/<id>/apply/` - Apply for job

### Resume Scanner
- `GET /resume-scanner/` - Resume scanner page
- `POST /resume-scanner/upload/` - Upload and scan resume

## 🧪 Testing

### Run Tests

```bash
python manage.py test
```

### Test Coverage

```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Write docstrings for functions and classes

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Harsha**
- GitHub: [@HarshaRockzz](https://github.com/HarshaRockzz)

## 🙏 Acknowledgments

- Django community for the amazing framework
- Tailwind CSS for the utility-first CSS framework
- Monaco Editor for the code editor
- Chart.js for data visualization
- All contributors and users of Compile-Mate

## 📞 Support

For support, email support@compilemate.com or open an issue on GitHub.

## 🔄 Version History

- **v1.0.0** (2025-01-10)
  - Initial release
  - 34+ coding problems
  - Full authentication system
  - Contest management
  - Learning paths and certifications
  - Code reviews and social feed
  - CodeConnect collaboration features
  - Job portal and resume scanner
  - Admin panel enhancements

## 🚧 Roadmap

- [ ] AI-powered code suggestions
- [ ] Mobile application (React Native)
- [ ] Real-time collaborative coding (enhanced)
- [ ] Integration with popular IDEs
- [ ] Advanced analytics dashboard
- [ ] Company-specific problem sets
- [ ] Premium subscription features
- [ ] API for third-party integrations

---

**Made with ❤️ by Harsha**

⭐ Star this repo if you find it helpful!

