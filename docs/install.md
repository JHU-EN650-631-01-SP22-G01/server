## Install and run the documentation

#### 1. Overall

The server (called this program in this article) is developed based on Python 3.6, and we do not guarantee that this program will work in any version of Python lower than this.
The required libraries that this program depends on are `flask` ​​and `PyMySQL`. The following table details all third-party libraries and their versions used by this program:

| LIBs | Flask | PyMySQl | Python-dotenv |
|:----:|:-----:|:-------:|:-------------:|
| VERs | 1.1.2 | 0.10.1 | 0.14.0 |

#### 2. Download

You can download this program using Git commands,
````
$ git clone https://github.com/JHU-EN650-631-01-SP22-G01/server.git
````

#### 3. Virtual environment (Optional but suggested)

To download the necessary third-party Python libraries, we recommend using a virtual environment. The virtual environment can be initialized and activated with the following commands,

```bash
// install virtualenv
$ pip install virtualenv
// create virtual environment
$ virtualenv name_for_the_venv
// activate the virtual environment
$ source path_to_venv/bin/activate
````

#### 4. Installation packages

We recommend using the `requirement.txt` file directly to install the necessary third-party libraries. It can be installed by the following command

````
(venv)$ pip install -r requirement.txt
````

When all the dependent third-party libraries are fully installed, some environment variables need to be set in advance before running the server. If the python-dotenv library is installed, you can set it by adding the `.env` file. If you need to customize the `.env` file, please assign values ​​to the following variables. For more information about DB_URI, please refer to [official documentation](https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/). For development only , you can not configure this file, the system will automatically use the SQLite database.

````
// database URI
DB_URI=?
````

#### 5. Running

Please use the following command to run this program

````
(venv)$ flask run