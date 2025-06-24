# 🖥️ Django Online Compiler

A simple web-based code compiler using Django and Python. Users can input Python code and get the output directly on the webpage using Python's `subprocess` module.

---

## 🔧 Tech Stack

- **Backend**: Django, Python
- **Frontend**: Django templates (HTML)
- **Code Execution**: Python `subprocess`

---

## 📁 Project Structure
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

---

## 🚀 How to Run Locally

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
