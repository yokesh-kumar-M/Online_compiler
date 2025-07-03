
Python Online Compiler
A sophisticated web-based Python compiler built with Django that provides a secure, feature-rich environment for writing, testing, and executing Python code directly in the browser.

✨ Features
🔧 Core Functionality
Real-time Code Execution: Execute Python code with instant results
Advanced Code Editor: Monaco Editor with syntax highlighting, auto-completion, and error detection
Dual Execution Modes:
Safe Mode: Controlled execution environment
Subprocess Mode: Traditional subprocess execution
Code Validation: Pre-execution syntax and security validation
Session Management: Save and load code snippets within sessions
🛡️ Security Features
Sandboxed Execution: Restricted imports and dangerous function blocking
Timeout Protection: Automatic termination of long-running code
Output Limiting: Prevents memory overflow from excessive output
Input Sanitization: Comprehensive validation of user input
CSRF Protection: Built-in Django CSRF protection
🎨 User Interface
Modern Design: Clean, responsive interface with gradient backgrounds
Split Layout: Side-by-side code editor and output display
Dark Theme: Easy-on-the-eyes Monaco editor with dark theme
Real-time Status: Live updates of execution status and cursor position
Keyboard Shortcuts: Quick access to common functions
📚 Additional Features
Code Examples: Built-in library of Python examples and tutorials
Auto-save: Automatic saving of code during editing
Clear Functions: Easy clearing of editor and output
Responsive Design: Works seamlessly on desktop and mobile devices
Error Handling: Comprehensive error reporting and user feedback

```bash
🚀 Installation
Prerequisites
Python 3.8 or higher
pip (Python package manager)
Git
Step 1: Clone the Repository
bash
git clone https://github.com/yokesh-kumar-M/Online_compiler
cd online-compiler
Step 2: Create Virtual Environment
bash
python -m venv venv
```

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
Step 3: Install Dependencies
bash
pip install -r requirements.txt
Step 4: Configure Django
bash
# Create database tables
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Collect static files (for production)
python manage.py collectstatic
Step 5: Run the Development Server
bash
python manage.py runserver
Visit http://localhost:8000 in your browser to access the compiler.

🔧 Configuration
Environment Variables
Create a .env file in the project root:

env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
Security Settings
For production deployment, update settings.py:

python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
📖 Usage
Basic Usage
Write Code: Enter your Python code in the Monaco editor
Run Code: Click "Run Code" button or press Ctrl+Enter
View Output: Results appear in the output panel
Save Code: Use "Save" button to store code in session
Load Examples: Browse built-in examples for learning
Keyboard Shortcuts
Ctrl+Enter / Cmd+Enter: Run code
Ctrl+S / Cmd+S: Save code
Ctrl+O / Cmd+O: Load code
Ctrl+L / Cmd+L: Clear editor
F5: Run code
Code Examples Available
Hello World: Basic Python syntax
Fibonacci Sequence: Recursive functions
Data Structures: Lists, dictionaries, sets
Sorting Algorithms: Algorithm implementations

🏗️ Project Structure

``` bash
online_compiler/
├── compiler/                 # Main Django app
│   ├── templates/           # HTML templates
│   │   └── compiler/
│   │       └── index.html   # Main interface
│   ├── views.py            # View functions
│   ├── urls.py             # URL routing
│   └── models.py           # Database models
├── online_compiler/         # Django project settings
│   ├── settings.py         # Configuration
│   ├── urls.py             # Main URL routing
│   └── wsgi.py             # WSGI application
├── static/                 # Static files
├── media/                  # Media files
├── logs/                   # Log files
├── requirements.txt        # Python dependencies
├── manage.py              # Django management
└── README.md              # This file
```

🔒 Security Considerations
Implemented Security Measures
Restricted Imports: Blocks dangerous modules like os, subprocess, sys
Function Filtering: Prevents execution of eval, exec, compile
Timeout Protection: Limits execution time to prevent infinite loops
Output Limiting: Prevents memory exhaustion from excessive output
Input Validation: Comprehensive validation of all user inputs
CSRF Protection: Django's built-in CSRF protection
Session Security: Secure session handling and storage
Additional Recommendations for Production
Use HTTPS for all connections
Implement rate limiting
Set up proper logging and monitoring
Use a reverse proxy (nginx)
Configure firewall rules
Regular security updates
🚀 Deployment
Using Gunicorn (Production)
bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn online_compiler.wsgi:application --bind 0.0.0.0:8000
Using Docker
dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "online_compiler.wsgi:application", "--bind", "0.0.0.0:8000"]
Environment Variables for Production
env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
🧪 Testing
Run Tests
bash
# Run all tests
python manage.py test

# Run specific test
python manage.py test compiler.tests.TestCodeExecution

# Run with coverage
pytest --cov=compiler tests/
Test Coverage
View functions testing
Code execution testing
Security validation testing
User interface testing
🤝 Contributing
Development Setup
Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Make your changes
Add tests for new functionality
Ensure all tests pass (python manage.py test)
Commit your changes (git commit -m 'Add amazing feature')
Push to branch (git push origin feature/amazing-feature)
Open a Pull Request
Code Style
Follow PEP 8 for Python code
Use Black for code formatting
Add docstrings for all functions
Include type hints where appropriate
📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
Django: Web framework
Monaco Editor: Code editor component
Font Awesome: Icons
Bootstrap: CSS framework inspiration
Python Community: For the amazing language
📞 Support
For support, email support@yourcompiler.com or create an issue on GitHub.

🔮 Future Enhancements
Planned Features
 Multi-language support (JavaScript, Java, C++)
 User authentication and profiles
 Code sharing and collaboration
 Advanced debugging tools
 Package installation support
 Code version history
 Real-time collaboration
 Mobile app development
 API for external integrations
 Advanced analytics and metrics
Performance Improvements
 Code caching mechanisms
 Async execution handling
 Load balancing support
 Database optimization
 CDN integration for static files
Made with efforts by Yokesh Kumar

Happy Coding! 🐍

=======
# 🖥️ Django Online Compiler

A simple web-based code compiler using Django and Python. Users can input Python code and get the output directly on the webpage using Python's `subprocess` module.

---

## 🔧 Tech Stack

- **Backend**: Django, Python
- **Frontend**: Django templates (HTML)
- **Code Execution**: Python `subprocess`

---

```bash
## Project Structure

 ├── compiler/ # Django app
 │ ├── templates/
 │ │ └── index.html
 │ ├── views.py
 │ ├── urls.py
 ├── online_compiler/ # Django project settings
 │ ├── settings.py
 │ └── urls.py
 ├── manage.py
 └── .gitignore
```
---

## How to Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/online-compiler.git
cd online-compiler

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate     # On Windows: venv\Scripts\activate

# 3. Install Django
pip install django

# 4. Run the server
python manage.py runserver
>>>>>>> b33120670119842e193b6b76568b5b5a8c26c1da
