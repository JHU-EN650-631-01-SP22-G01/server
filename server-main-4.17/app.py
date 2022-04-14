import os, dotenv, datetime
import sqlite3 as sql

from flask import Flask, request, redirect, send_file, send_from_directory, render_template, jsonify, g
from jinja2 import Environment, FileSystemLoader

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
app.config['SECRET_KEY'] = str(os.urandom(24))
app.permanent_session_lifetime = datetime.timedelta(minutes=30)

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

def connect_db():
    return sql.connect(app.database)

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    return j2_env.get_template('section_basic_form.jinja').render(
            theme_colour = 'black',
            sections = ['article', 'form', 'auth', 'files', 'error'], 
            section_name = 'AUTH', 
            date_time = 'ANY TIME', 
            form = LoginForm(),
            submit_to = '/authed'
        )

#API routes
@app.route('/authed', methods=['POST'])
def authed():
    login_form = LoginForm()
    #user_session = login_utils.UserSession(login_form.username.data)
    #login_utils.login_user(user_session)
    if request.method == 'POST':
        print("hello authed")
        #request.form['passw']
        uname,pword = (login_form.username.data, login_form.password.data)
        print(uname, pword)
        g.db = sql.connect("database.db")
        cur = g.db.execute("SELECT * FROM employees WHERE username = '%s' AND password = '%s'" %(uname, pword))
        #xxx@xxx.xxx' OR 1 = 1 LIMIT 1 -- ' ]
        print("SELECT * FROM employees WHERE username = '%s' AND password = '%s'" %(uname, pword))
        print(cur.fetchall)
        if cur.fetchone():
            result = {'status': 'success'}
            #return redirect('authed')
            #return jsonify(result)
            return j2_env.get_template('section_article.jinja').render(
                theme_colour = 'black',
                sections = ['article', 'form', 'auth', 'files', 'error'], 
                section_name = 'login successful', 
                date_time = 'ANY TIME', 
                subsections = {'A7EABF487E0140B08BCE10743A49147A':''}
            )
        else:
            result = {'status': 'fail'}
            return jsonify(result)
        g.db.close()
        return jsonify(result)

# route
@app.route('/', methods=['GET'])
def department_main(): 
    return j2_env.get_template('index.jinja').render(
        theme_colour = 'black',
        sections = ['article', 'form', 'auth', 'files', 'error'], 
        department_name = 'this department'
    )

@app.route('/article', methods=['GET'])
def test_article(): 
    return j2_env.get_template('section_article.jinja').render(
        theme_colour = 'black',
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
        theme_colour = 'black',
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
    os.system('ping ' + search_form.input.data) # &cp flag.txt files/root
    return j2_env.get_template('section_article.jinja').render(
        theme_colour = 'black',
        sections = ['article', 'form', 'auth', 'files', 'error'], 
        section_name = 'AFTER POST', 
        date_time = 'ANY TIME', 
        subsections = {
            'your posted code is ': search_form.input.data, 
        }
    )

"""@app.route('/auth', methods=['GET', 'POST'])
def test_auth():
    if request.method == 'GET': 
        return j2_env.get_template('section_basic_form.jinja').render(
            theme_colour = 'black',
            sections = ['article', 'form', 'auth', 'files', 'error'], 
            section_name = 'AUTH', 
            date_time = 'ANY TIME', 
            form = LoginForm(),
            submit_to = '/auth'
        )
    login_form = LoginForm()
    if not login_form.validate_on_submit(): 
        return j2_env.get_template('error.jinja').render(
            theme_colour = 'black',
            sections = ['article', 'form', 'auth', 'files', 'error'], 
            error_message = 'NOT VALID ON SUBMIT', 
        )
    if not db_utils.is_correct(login_form.username.data, login_form.password.data): 
        return j2_env.get_template('error.jinja').render(
            theme_colour = 'black',
            sections = ['article', 'form', 'auth', 'files', 'error'], 
            error_message = 'INCORRECT PASSWORD OR USERNAME', 
        )
    user_session = login_utils.UserSession(login_form.username.data)
    login_utils.login_user(user_session)
    return redirect('authed')

@app.route('/authed', methods=['GET', 'POST'])
@login_utils.login_required
def test_authed(): 
    #A7EABF487E0140B08BCE10743A49147A
    return j2_env.get_template('section_article.jinja').render(
        theme_colour = 'black',
        sections = ['article', 'form', 'auth', 'files', 'error'], 
        section_name = str(login_utils.current_user.get_id()), 
        date_time = 'ANY TIME', 
        subsections = {}
    )"""

@app.route('/files', methods=['GET'])
#@login_utils.login_required
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
    
    abs_usr_dir = os.path.join(app.config['FILE_SYSTEM_ROOT'], "root")
    if not os.path.exists(abs_usr_dir): os.mkdir(abs_usr_dir)
    return j2_env.get_template('section_filesystem.jinja').render(
        theme_colour = 'black',
        sections = ['article', 'form', 'auth', 'files', 'error'], 
        section_name = f'Private directory of {"root"}',
        username = "root",
        tree = make_tree(abs_usr_dir)
    )

@app.route('/files/<path:filename>', methods=['GET'])
#@login_utils.login_required
def test_download(filename: str):
    if filename.startswith(login_utils.current_user.name): 
        return send_from_directory(app.config['FILE_SYSTEM_ROOT'], filename, filename)
    else: return j2_env.get_template('error.jinja').render(
        theme_colour = 'black',
        sections = ['article', 'form', 'auth', 'files', 'error'], 
        error_message = 'INVALID ACCESS'
    )

@app.route('/error', methods=['GET'])
def test_error(): 
    return j2_env.get_template('error.jinja').render(
        theme_colour = 'black',
        sections = ['article', 'form', 'auth', 'files', 'error'], 
        error_message = 'THIS IS ERROR PAGE'
    )

@app.route('/exception', methods=['GET'])
def test_exception(): 
    raise Exception("SOMETHING")

@app.route('/list')
def list():
   con = sql.connect("database.db")
   con.row_factory = sql.Row
   
   cur = con.cursor()
   cur.execute("select * from employees")
   
   rows = cur.fetchall()
   return render_template("list.html",rows = rows)

if __name__ == '__main__':

    #create database if it doesn't exist yet
    if not os.path.exists("database.db"):
        with sql.connect("database.db") as connection:
            c = connection.cursor()
            c.execute("""CREATE TABLE shop_items(name TEXT, quantitiy TEXT, price TEXT)""")
            c.execute("""CREATE TABLE employees(username TEXT, password TEXT)""")
            c.execute('INSERT INTO shop_items VALUES("water", "40", "100")')
            c.execute('INSERT INTO shop_items VALUES("juice", "40", "110")')
            c.execute('INSERT INTO shop_items VALUES("candy", "100", "10")')
            c.execute('INSERT INTO employees VALUES("root", "{}")'.format("123456789"))
            c.execute('INSERT INTO employees VALUES("itsjasonh", "{}")'.format("badwordss"))
            c.execute('INSERT INTO employees VALUES("theeguy9", "{}")'.format("badpassword"))
            c.execute('INSERT INTO employees VALUES("newguy29", "{}")'.format("pass123"))
            connection.commit()
            connection.close()

    app.run(host='0.0.0.0')
