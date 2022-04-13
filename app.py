import os, dotenv, datetime

from flask import Flask, request, redirect, send_from_directory
from jinja2 import Environment, FileSystemLoader
from flask_wtf import CSRFProtect

from src.auth import utils as login_utils
from src.sqlalchemy import utils as db_utils
from src.forms import LoginForm, SearchForm

# Set environment variables for APIs
project_root_dir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.path.join(project_root_dir, '.env')
if os.path.exists(dotenv_path): dotenv.load_dotenv(dotenv_path, override=True)

app = Flask(__name__)
app.app_context().push()
app.config['FILE_SYSTEM_ROOT'] = os.path.join(project_root_dir, 'files')

# secret key
app.config['SECRET_KEY'] = "test" #str(os.urandom(24))
app.permanent_session_lifetime = datetime.timedelta(minutes=30)
csrf = CSRFProtect()
csrf.init_app(app)

# database initialise
db_manager = db_utils.init_dbmanager(app, init_json='[{"username": "root", "password":"123456789"}]')
db_manager.create_all()

# login manager initialise
login_manager = login_utils.init_manager(app)
login_manager.login_view = '/auth'

# CORS to allow the cross-domain issues
# CORS(app, supports_credentials=True)
templates_dir = os.path.join(project_root_dir, 'templates')
j2_env = Environment(loader=FileSystemLoader(templates_dir), trim_blocks=True)

# route
@app.route('/', methods=['GET'])
def department_main(): 
    return j2_env.get_template('index.jinja').render(
        theme_colour = '#003371',
        sections = ['article', 'form', 'auth', 'files', 'error'], 
        department_name = 'this department'
    )

@app.route('/article', methods=['GET'])
def test_article(): 
    return j2_env.get_template('section_article.jinja').render(
        theme_colour = '#003371',
        sections = ['article', 'form', 'auth', 'files', 'error'], 
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
    return j2_env.get_template('section_basic_form.jinja').render(
        theme_colour = '#003371',
        sections = ['article', 'form', 'auth', 'files', 'error'], 
        section_name = 'form', 
        date_time = 'ANY TIME', 
        form = SearchForm(),
        submit_to = '/posted'
    )

@app.route('/posted', methods=['GET', 'POST'])
def test_posted(): 
    search_form = SearchForm()
    if not search_form.validate_on_submit(): raise Exception(search_form.errors)
    return j2_env.get_template('section_article.jinja').render(
        theme_colour = '#003371',
        sections = ['article', 'form', 'auth', 'files', 'error'], 
        section_name = 'AFTER POST', 
        date_time = 'ANY TIME', 
        subsections = {
            'your posted code is ': search_form.input.data, 
        }
    )

@app.route('/auth', methods=['GET', 'POST'])
def test_auth():
    if request.method == 'GET': 
        return j2_env.get_template('section_basic_form.jinja').render(
            theme_colour = '#003371',
            sections = ['article', 'form', 'auth', 'files', 'error'], 
            section_name = 'AUTH', 
            date_time = 'ANY TIME', 
            form = LoginForm(),
            submit_to = '/auth'
        )
    login_form = LoginForm()
    if not login_form.validate_on_submit(): 
        return j2_env.get_template('error.jinja').render(
            theme_colour = '#003371',
            sections = ['article', 'form', 'auth', 'files', 'error'], 
            error_message = 'NOT VALID ON SUBMIT', 
        )
    if not db_utils.is_correct(login_form.username.data, login_form.password.data): 
        return j2_env.get_template('error.jinja').render(
            theme_colour = '#003371',
            sections = ['article', 'form', 'auth', 'files', 'error'], 
            error_message = 'INCORRECT PASSWORD OR USERNAME', 
        )
    user_session = login_utils.UserSession(login_form.username.data)
    login_utils.login_user(user_session)
    return redirect('authed')

@app.route('/authed', methods=['GET'])
@login_utils.login_required
def test_authed(): 
    return j2_env.get_template('section_article.jinja').render(
        theme_colour = '#003371',
        sections = ['article', 'form', 'auth', 'files', 'error'], 
        section_name = str(login_utils.current_user.get_id()), 
        date_time = 'ANY TIME', 
        subsections = {}
    )

@app.route('/files', methods=['GET'])
@login_utils.login_required
def dirtree():
    def make_tree(path):
        tree = dict(name=os.path.basename(path), children=[])
        try: 
            lst = os.listdir(path)
        except OSError:
            pass #ignore errors
        else:
            for name in lst:
                fn = os.path.join(path, name)
                if os.path.isdir(fn):
                    tree['children'].append(make_tree(fn))
                else:
                    tree['children'].append(dict(name=name))
        return tree
    
    abs_usr_dir = os.path.join(app.config['FILE_SYSTEM_ROOT'], login_utils.current_user.name)
    if not os.path.exists(abs_usr_dir): os.mkdir(abs_usr_dir)
    return j2_env.get_template('section_filesystem.jinja').render(
        theme_colour = '#003371',
        sections = ['article', 'form', 'auth', 'files', 'error'], 
        section_name = f'Private directory of {login_utils.current_user.name}',
        username = login_utils.current_user.name,
        tree = make_tree(abs_usr_dir)
    )

@app.route('/files/<path:filename>', methods=['GET'])
@login_utils.login_required
def test_download(filename: str):
    if filename.startswith(login_utils.current_user.name): 
        return send_from_directory(app.config['FILE_SYSTEM_ROOT'], filename, filename)
    else: return j2_env.get_template('error.jinja').render(
        theme_colour = '#003371',
        sections = ['article', 'form', 'auth', 'files', 'error'], 
        error_message = 'INVALID ACCESS'
    )

@app.route('/error', methods=['GET'])
def test_error(): 
    return j2_env.get_template('error.jinja').render(
        theme_colour = '#003371',
        sections = ['article', 'form', 'auth', 'files', 'error'], 
        error_message = 'THIS IS ERROR PAGE'
    )

@app.route('/exception', methods=['GET'])
def test_exception(): 
    raise Exception("SOMETHING")

if __name__ == '__main__':
    app.run()