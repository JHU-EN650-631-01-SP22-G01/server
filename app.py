import os, dotenv, datetime

from flask import Flask, request, redirect, send_file, send_from_directory
from jinja2 import Environment, FileSystemLoader

from src.auth import utils as login_utils
from src.sqlalchemy import utils as db_utils
from src.forms import LoginForm, SearchForm
from PIL import Image
import binascii
import optparse

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
login_manager.login_view = '/user'

# CORS to allow the cross-domain issues
# CORS(app, supports_credentials=True)
templates_dir = os.path.join(project_root_dir, 'templates')
j2_env = Environment(loader=FileSystemLoader(templates_dir), trim_blocks=True)

# route
@app.route('/', methods=['GET'])
def department_main(): 
    return j2_env.get_template('index.jinja').render(
        theme_colour = 'darkgreen',
        original_colour = 'black',
        department_name = 'Spiritual Force',
        sections = ['puzzle', 'error'],

    )

@app.route('/puzzle', methods=['GET'])
def test_article(): 
    return j2_env.get_template('section_article.jinja').render(
        theme_colour = 'darkgreen',
        original_colour = 'black',
        sections = ['puzzle', 'error'], 
        section_name = 'puzzle', 
        date_time = 'Thu, Apr 20th, 2023', 
        subsections = {
            'story premise': 'Regardless of the programming language being used, the functionality, logic, and efficiency of the language are always paramount — unless, of course, some programming language that champions purposefully overcomplicated code and was created for hurt your brain. [hint: The appearance of beginning does not mean the real beginning.]',
            'now your turn': '-----[------->+<]>++.-----[-->+++<]>.[--->+<]>---.[-->+++++<]>-.--[--->+<]>---.-----------.[->+++<]>--.-.---[->+++<]>.+++[->++++<]>.-------.--[--->+<]>-.[---->+<]>+++.-[--->++<]>+.--.+++++.----------.-[--->+<]>-.+++++[->+++<]>.---------.[--->+<]>--.---[->++++<]>-.+.+.++[->+++<]>+..[--->+<]>--.+[->+++<]>.--.+++++++++++++.-[->+++++<]>-.[->+++<]>++.+++.--[--->+<]>-.+[->+++<]>++.----.--[--->+<]>-.+++[->+++<]>.+++++++++.[----->++<]>.------------.+[->+++<]>.++++++++++++.--..++++++++.-------.-----.------.--.--[--->+<]>-.+++[->+++<]>.-.-[--->+<]>-.[->+++<]>+.+++++++++++++.----------.-[--->+<]>-.--[->++++<]>-.-[->+++<]>-.--[--->+<]>-.++[->+++<]>+.+++++.---.-.-[--->++<]>---.', 
        }

    )

@app.route('/error', methods=['GET'])
def test_error(): 
    return j2_env.get_template('error.jinja').render(
        theme_colour = 'darkgreen',
        original_colour = 'black',
        sections = ['puzzle', 'error'], 
        section_call = 'error', 
        error_message = 'THIS IS ERROR PAGE'
    )

@app.route('/exception', methods=['GET'])
def test_exception(): 
    raise Exception("SOMETHING")

if __name__ == '__main__':
    app.run(debug = True)
