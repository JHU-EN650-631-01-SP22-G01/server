import os, dotenv, datetime, json

from typing import List, Dict

from flask import Flask, request, redirect, send_from_directory
from flask_login import UserMixin, login_required
from jinja2 import Environment, FileSystemLoader
from flask_wtf import CSRFProtect

from src.auth import utils as login_utils
from src.expymysql import utils as db_utils
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
db_tables = db_utils.init_dbmanager(app, 
    db_uri=os.environ['DB_URI'],
    init_users=[{"username": "root", "password":"123456789"}], 
    init_records= [{"type":"TOP SECRET"} for _ in range(50)] \
        + [{"type": "SECRET"} for _ in range(50)] \
        + [{"type": "PUBLIC"} for _ in range(50)]
)

# login manager initialise
login_manager = login_utils.init_manager(app, login_route='/login')

templates_dir = os.path.join(project_root_dir, 'templates')
j2_env = Environment(loader=FileSystemLoader(templates_dir), trim_blocks=True)

def get_section(by_user: UserMixin)-> List[str]:
    if by_user.is_authenticated: return ['records', 'files', 'logout']
    else: return ['articles', 'login'] 

# route
@app.route('/', methods=['GET'])
def department_main(): 
    return j2_env.get_template('index.jinja').render(
        theme_colour = '#082567',
        sections = get_section(login_utils.current_user), 
        department_name = 'large mecha'
    )

@app.route('/articles', methods=['GET'])
def articles(): 
    return j2_env.get_template('section_article.jinja').render(
        theme_colour = '#082567',
        sections = get_section(login_utils.current_user), 
        section_name = 'articles', 
        date_time = 'ANY TIME', 
        subsections = {
            'subsection1': 'content for subjection', 
            'subsection2': 'content for subjection', 
            'subsection3': 'content for subjection', 
        }
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if login_utils.current_user.is_authenticated: return redirect('/logout')
    if request.method == 'GET': 
        return j2_env.get_template('section_basic_form.jinja').render(
            theme_colour = '#082567',
            sections = get_section(login_utils.current_user), 
            section_name = 'login', 
            date_time = 'ANY TIME', 
            form = LoginForm(),
            submit_to = '/login'
        )
    login_form = LoginForm()
    if not login_form.validate_on_submit(): 
        return j2_env.get_template('error.jinja').render(
            theme_colour = '#082567',
            section_name = 'login', 
            sections = get_section(login_utils.current_user), 
            error_message = 'NOT VALID ON SUBMIT', 
        )
    if not db_utils.is_correct(login_form.username.data, login_form.password.data): 
        return j2_env.get_template('error.jinja').render(
            theme_colour = '#082567',
            section_name = 'login', 
            sections = get_section(login_utils.current_user), 
            error_message = 'INCORRECT PASSWORD OR USERNAME'
        )
    user_session = login_utils.load_user_by_name(login_form.username.data)
    login_utils.login_user(user_session)
    return j2_env.get_template('notify.jinja').render(
        theme_colour = '#082567',
        section_name = 'login', 
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

@app.route('/records', methods=['GET', 'POST'])
@login_required
def records(): 
    search_form = SearchForm()
    if request.method == 'GET': 
        search_form.input.render_kw = {"placeholder": "Search for experiments records"}
        return j2_env.get_template('section_basic_form.jinja').render(
            theme_colour = '#082567',
            sections = get_section(login_utils.current_user), 
            section_name = 'records', 
            form = search_form,
            submit_to = '/records'
        ) 
    json_data: Dict = {}
    try: json_data.update(json.loads(search_form.input.data))
    except (ValueError, TypeError):json_data.update({'id': search_form.input.data})
    query_result = []
    try: 
        if 'id' in json_data: 
            out = db_tables.records.get_record_by_id(int(json_data['id']))
            if 'type' not in json_data or out['type'] == json_data['type']: query_result.append(out)
        elif 'type' in json_data: 
            print(f'DATA IS {json_data}')
            out = db_tables.records.get_records_by_type(json_data['type'])
            query_result.extend(out)
        else: 
            raise AttributeError('UNSUPPORT QUERY')
    except Exception as e: 
        return j2_env.get_template('error.jinja').render(
            theme_colour = '#082567',
            sections = get_section(login_utils.current_user), 
            section_name = 'records', 
            error_message = f'UNSUPPORT QUERY FORMAT: {search_form.input.data}, </br> ERROR: {e}'
        )
    return j2_env.get_template('section_list.jinja').render(
        theme_colour = '#082567',
        sections = get_section(login_utils.current_user), 
        section_name = 'records',
        query_str = json_data,
        query_result = query_result
    )
    
@app.route('/records/<path:id>', methods=['GET'])
@login_required
def access_record(id: str): 
    record = db_tables.records.get_record_by_id(id)
    if record is None: 
        return j2_env.get_template('error.jinja').render(
            theme_colour = '#082567',
            sections = get_section(login_utils.current_user), 
            section_name = 'records', 
            error_message = f'NOT EXIST ID {id}'
        ) 
    else: return j2_env.get_template('section_article.jinja').render(
        theme_colour = '#082567',
        sections = get_section(login_utils.current_user), 
        section_name = 'records', 
        date_time = datetime.datetime.now(), 
        subsections = {
            'RECORD ID': record['id'], 
            'EXPERIMENT TIMES': record['created_time'], 
            'SECURITY CLEARNANCE': record['type'] 
        }
    )


@app.route('/files', methods=['GET'])
@login_utils.login_required
def filesystem():
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
        theme_colour = '#082567',
        sections = get_section(login_utils.current_user), 
        section_name = f'files',
        username = login_utils.current_user.name,
        tree = make_tree(abs_usr_dir)
    )

@app.route('/files/<path:filename>', methods=['GET'])
@login_utils.login_required
def download_file(filename: str):
    if filename.startswith(login_utils.current_user.name): 
        return send_from_directory(app.config['FILE_SYSTEM_ROOT'], filename)
    else: return j2_env.get_template('error.jinja').render(
        theme_colour = '#082567',
        sections = get_section(login_utils.current_user), 
        error_message = 'INVALID ACCESS'
    )


if __name__ == '__main__':
    app.run()