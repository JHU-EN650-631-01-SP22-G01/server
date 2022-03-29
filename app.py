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

@app.route('/', methods=['GET'])
def department_main(): 
    return j2_env.get_template('index.jinja').render(
        sections = ['article', 'form'], 
        department_name = 'test'
    )

@app.route('/article', methods=['GET'])
def test_article(): 
    return j2_env.get_template('section_article.jinja').render(
        sections = ['article', 'form'], 
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
        sections = ['article', 'form'], 
        section_name = 'form', 
        date_time = 'ANY TIME', 
        auth_page = 'auth'
    )

@app.route('/auth', methods=['POST'])
def test_auth(): 
    auth_code = request.form.get('code', 'default')
    return j2_env.get_template('section_article.jinja').render(
        sections = ['article', 'form'], 
        section_name = auth_code, 
        date_time = 'ANY TIME', 
        subsections = {
            'subsection1': 'content for subjection', 
            'subsection2': 'content for subjection', 
            'subsection3': 'content for subjection', 
        }
    )

if __name__ == '__main__':
    app.run()
