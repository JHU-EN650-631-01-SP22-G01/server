import os, dotenv, datetime, json

from random import randint
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
    init_users=[
        {"slevel": 10, "username": "D1", "password":"fadfagrqg"}, 
        {"slevel": 10, "username": "D2", "password":"fadfagrqg"}, 
        {"slevel": 5, "username": "M1", "password":"123456789"}, 
        {"slevel": 5, "username": "M2", "password":"feqfewqqff"}, 
        {"slevel": 1, "username": "Jiachao", "password":"f8042c52fa5d97160a4c7f644740d30e"}, 
        {"slevel": 0, "username": "root", "password":"£fafaf#awefae"}, 
    ], 
    init_records= [
        {"type":"experiment", 'security_level': randint(1, 10), 'content': '▪️ '*randint(50,150)} for _ in range(50)
    ] + [
        {"type": "meeting", 'security_level': randint(1, 10), 'content': '▪️ '*randint(50,150)} for _ in range(50)
    ] + [
        {"type": "notification", 'security_level': randint(1, 10), 'content': '▪️ '*randint(50,150)} for _ in range(50)
    ]
)

# login manager initialise
login_manager = login_utils.init_manager(app, login_route='/login')

templates_dir = os.path.join(project_root_dir, 'templates')
j2_env = Environment(loader=FileSystemLoader(templates_dir), trim_blocks=True)

def get_section(by_user: UserMixin)-> List[str]:
    if by_user.is_authenticated: return ['records', 'files', 'logout']
    else: return ['exhibits', 'login'] 

# route
@app.route('/', methods=['GET'])
def department_main(): 
    return j2_env.get_template('index.jinja').render(
        theme_colour = '#082567',
        sections = get_section(login_utils.current_user), 
        department_name = 'large mecha'
    )

@app.route('/exhibits', methods=['GET'])
def articles(): 
    return j2_env.get_template('section_article.jinja').render(
        theme_colour = '#082567',
        sections = get_section(login_utils.current_user), 
        section_name = 'exhibit', 
        subsections = {
            'Sky Striker Mecha Modules - Multirole': {
                'text': 'As its name, multirole, it has multipurpose. This is the key equipment that allows our fighter to jump from right above the battle field. It has a magnitic power to recycle the used equipment and give a quick repair so that our fighters have infinite fire power.', 
                'image': 'Sky Striker Mecha Modules - Multirole.webp'
            }, 
            'Sky Striker Mecharmory - Hercules Base': {
                'text': 'Hercules is the Roman equivalent of the Greek divine hero Heracles, son of Jupiter and the mortal Alcmene. In classical mythology, Hercules is famous for his strength and for his numerous far-ranging adventures. We give our moving base this name for it remarkable ability of carrying all the supplies that out two ACE fighters need.', 
                'image': 'Sky Striker Mecharmory - Hercules Base.png'
            },
            'Sky Striker Ace - Zeke': {
                'text': 'Zeke is a super weapon that designed for Roze. Different from the power suit that Raye has, Roze is designed to destroy and move a whole city into the dust.\nHight: 39.13 M\nWeight: 104.23 T', 
                'image': 'Sky Striker Ace - Zeke.png'

            }
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
        search_form.input.render_kw = {'placeholder': 'id or {"type": "meeting"|"experiments|"notification"}'}
        return j2_env.get_template('section_basic_form.jinja').render(
            theme_colour = '#082567',
            sections = get_section(login_utils.current_user), 
            section_name = 'records', 
            form = search_form,
            submit_to = '/records'
        ) 
    cur_user = db_tables.users.get_user_by_id(login_utils.current_user.get_id())
    security_level = int(cur_user['slevel'])
    json_data: Dict = {}
    try: json_data.update(json.loads(search_form.input.data))
    except (ValueError, TypeError):json_data.update({'id': search_form.input.data})
    query_result = []
    try: 
        if 'id' in json_data: 
            out = db_tables.records.get_record_by_id(json_data['id'])
            if 'type' not in json_data or out['type'] == json_data['type']: query_result.append(out)
        elif 'type' in json_data: 
            out = db_tables.records.get_records_by_type(json_data['type'], security_level)
            query_result.extend(out)
        else: 
            raise AttributeError('UNSUPPORT QUERY')
        print(query_result)
        if query_result is None or query_result == [None]: 
            return j2_env.get_template('notify.jinja').render(
            theme_colour = '#082567',
            sections = get_section(login_utils.current_user), 
            section_name = 'records', 
            notification = f'NOTHING FOUND </br> QUERY STRING: {json_data}'
        )
    except Exception as e: 
        return j2_env.get_template('error.jinja').render(
            theme_colour = '#082567',
            sections = get_section(login_utils.current_user), 
            section_name = 'records', 
            error_message = f'UNSUPPORT QUERY FORMAT: {search_form.input.data}, </br> ERROR: {e} </br> RESULT: {query_result}'
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
    cur_user = db_tables.users.get_user_by_id(login_utils.current_user.get_id())
    record = None
    try: record = db_tables.records.get_record_by_id(id)
    except: pass #IGNORE EVERYTHINGS
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
        date_time = f'ACCESSER ID: {cur_user["id"]} \t PERMISSION: {cur_user["slevel"]}', 
        subsections = { 
            'SECURITY LEVEL': record['slevel'], 
            'RECORD ID': record['id'], 
            'RECORD TYPE': record['type'], 
            'EXPERIMENT TIMES': record['created_time'], 
            'CONTENT': record['content']
            
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
    tree = make_tree(abs_usr_dir)
    print(tree)
    return j2_env.get_template('section_filesystem.jinja').render(
        theme_colour = '#082567',
        sections = get_section(login_utils.current_user), 
        section_name = f'files',
        username = login_utils.current_user.name,
        tree = tree
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