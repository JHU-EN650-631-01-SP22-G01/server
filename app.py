import os, dotenv, datetime
from typing import List

from flask import Flask, request, send_from_directory
from flask_login import UserMixin
from jinja2 import Environment, FileSystemLoader
from flask_wtf import CSRFProtect

from src.auth import utils as login_utils
from src.sqlalchemy import utils as db_utils
from src.forms import LoginForm

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

db_manager = db_utils.init_dbmanager(app, init_json='[{"username": "Erfan", "password":"StupidPW"}]')

login_manager = login_utils.init_manager(app, login_route='/auth')

templates_dir = os.path.join(project_root_dir, 'templates')
j2_env = Environment(loader=FileSystemLoader(templates_dir), trim_blocks=True)

def get_section(by_user: UserMixin)-> List[str]:
    if by_user.is_authenticated: return ['files', 'logout']
    else: return ['auth'] 

# route
@app.route('/', methods=['GET'])
def department_main(): 
    return j2_env.get_template('index.jinja').render(
        theme_colour = '#8E5D00',
        sections = get_section(login_utils.current_user),
        department_name = 'Erfan’s department'
    )

@app.route('/auth', methods=['GET', 'POST'])
def authentication():
    if request.method == 'GET': 
        return j2_env.get_template('section_basic_form.jinja').render(
            theme_colour = '#8E5D00',
            sections = get_section(login_utils.current_user),
            section_name = 'AUTH', 
            form = LoginForm(),
            submit_to = '/auth'
        )
    login_form = LoginForm()
    if not login_form.validate_on_submit(): 
        return j2_env.get_template('error.jinja').render(
            theme_colour = '#8E5D00',
            section_name = 'auth', 
            sections = get_section(login_utils.current_user),
            error_message = 'NOT VALID ON SUBMIT', 
        )
    if not db_utils.is_correct(login_form.username.data, login_form.password.data): 
        return j2_env.get_template('error.jinja').render(
            theme_colour = '#8E5D00',
            section_name = 'auth', 
            sections = get_section(login_utils.current_user),
            error_message = 'INCORRECT PASSWORD OR USERNAME', 
        )
    user_session = login_utils.UserSession(login_form.username.data)
    login_utils.login_user(user_session)
    return j2_env.get_template('notify.jinja').render(
        theme_colour = '#8E5D00',
        section_name = 'auth', 
        sections = get_section(login_utils.current_user), 
        notification = 'LOGIN SUCCESS'
    )

@app.route('/logout', methods=['GET'])
@login_utils.login_required
def logout_user(): 
    login_utils.logout_user()
    return j2_env.get_template('notify.jinja').render(
        theme_colour = '#082567',
        section_name = 'logout', 
        sections = get_section(login_utils.current_user), 
        notification = 'LOGOUT SUCCESS'
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
        theme_colour = '#8E5D00',
        sections = get_section(login_utils.current_user),
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
        theme_colour = '#8E5D00',
        sections = get_section(login_utils.current_user),
        error_message = 'INVALID ACCESS'
    )

if __name__ == '__main__':
    app.run()