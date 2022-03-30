import os, datetime
from dotenv import load_dotenv
from flask import Flask, request
from jinja2 import Environment, FileSystemLoader

# Set environment variables for APIs
project_root_dir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.path.join(project_root_dir, '.env')
if os.path.exists(dotenv_path): load_dotenv(dotenv_path, override=True)

app = Flask(__name__)

# 24bits random secret key for XSS
app.config['SECRET_KEY'] = str(os.urandom(24))
app.permanent_session_lifetime = datetime.timedelta(minutes=30)

# CORS to allow the cross-domain issues
# CORS(app, supports_credentials=True)
templates_dir = os.path.join(project_root_dir, 'templates')
j2_env = Environment(loader=FileSystemLoader(templates_dir), trim_blocks=True)


# route
@app.route('/', methods=['GET'])
def department_main(): 
    return j2_env.get_template('index.jinja').render(
        sections = ['article', 'form', 'auth', 'error'], 
        department_name = 'this department'
    )

@app.route('/article', methods=['GET'])
def test_article(): 
    return j2_env.get_template('section_article.jinja').render(
        sections = ['article', 'form', 'auth', 'error'], 
        section_name = 'article', 
        date_time = 'ANY TIME', 
        subsections = {
            'subsection1': 'content for subjection', 
            'subsection2': 'content for subjection', 
            'subsection3': 'content for subjection', 
        }
    )

@app.route('/form', methods=['GET'])
def test_form(): 
    return j2_env.get_template('section_form.jinja').render(
        sections = ['article', 'form', 'auth', 'error'], 
        section_name = 'form', 
        date_time = 'ANY TIME', 
        next_page = 'posted'
    )

@app.route('/posted', methods=['POST'])
def test_posted(): 
    posted_code = request.form.get('code', 'default')
    return j2_env.get_template('section_article.jinja').render(
        sections = ['article', 'form', 'auth', 'error'], 
        section_name = 'AFTER POST', 
        date_time = 'ANY TIME', 
        subsections = {
            'your posted code is ': str(posted_code), 
        }
    )

@app.route('/auth', methods=['GET'])
def test_auth(): 
    return j2_env.get_template('section_auth.jinja').render(
        sections = ['article', 'form', 'auth', 'error'], 
        section_name = 'auth', 
        date_time = 'ANY TIME', 
        next_page = 'authed'
    )

@app.route('/authed', methods=['POST'])
def test_authed(): 
    username = request.form.get('username', 'guest')
    password = request.form.get('password', 'guest')
    return j2_env.get_template('section_article.jinja').render(
        sections = ['article', 'form', 'auth', 'error'], 
        section_name = 'AFTER AUTH', 
        date_time = 'ANY TIME', 
        subsections = {
            'YOUR USERNAME': username, 
            'YOUR PASSWORD': password
        }
    )

@app.route('/error', methods=['GET'])
def test_error(): 
    raise Exception("SOMETHING")

if __name__ == '__main__':
    app.run()
