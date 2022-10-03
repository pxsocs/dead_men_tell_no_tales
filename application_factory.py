import logging
import os
import sys
import atexit
import warnings
import emoji
import configparser
from logging.handlers import RotatingFileHandler
from ansi.colour import fg
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

# Make sure current libraries are found in path
current_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(current_path)

# Local imports have to be below the path append above
# otherwise they will fail to load
from backend.ansi_management import (warning, success, error, info,
                                     clear_screen, muted, yellow, blue)


# ------------------------------------
# Application Factory
def init_app():

    from backend.config import Config
    warnings.filterwarnings('ignore')

    # Config of Logging
    formatter = "[%(asctime)s] {%(module)s:%(funcName)s:%(lineno)d} %(levelname)s in %(module)s: %(message)s"
    logging.basicConfig(handlers=[
        RotatingFileHandler(filename=str(Config.debug_file),
                            mode='w',
                            maxBytes=120000,
                            backupCount=0)
    ],
                        level=logging.INFO,
                        format=formatter,
                        datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.getLogger('apscheduler').setLevel(logging.CRITICAL)
    logging.getLogger('werkzeug').setLevel(logging.INFO)
    logging.info("Starting main program...")

    # Launch app & initial setup
    app = Flask(__name__)
    app.config.from_object(Config)
    app.logger = logging.getLogger()

    # Create empty instance to store app variables
    app.app_status = {'encryption_password': None}

    # Get Version
    with app.app_context():
        try:
            version_file = Config.version_file
            with open(version_file, 'r') as file:
                current_version = file.read().replace('\n', '')
        except Exception:
            current_version = 'unknown'
        with app.app_context():
            app.version = current_version
    print("")

    # Load config.ini into app
    # --------------------------------------------
    # Read Global Variables from warden.config(s)
    # Can be accessed like a dictionary like:
    # app.settings['SERVER']['host']
    # --------------------------------------------
    config_file = Config.config_file
    from backend.utils import create_config
    # Create empty instance of configparser
    config_settings = configparser.ConfigParser()
    # Load config.ini
    if os.path.isfile(config_file):
        config_settings.read(config_file)
        if config_settings.sections() != []:
            app.app_status['initial_setup'] = False
            app.settings = config_settings
            print(
                success(
                    "✅ Config Loaded from config.ini - edit it for customization"
                ))
    else:
        print(
            error(
                "  Config File could not be loaded or is empty, creating a new one with default values..."
            ))
        create_config(config_file)
        config_settings.read(config_file)
        app.settings = config_settings
        app.app_status['initial_setup'] = True

    # Login Manager

    with app.app_context():
        app = create_loginmanager(app)
        app = create_db(app)
        from routes.errors.handlers import errors
        from routes.main.main import main
        from routes.main.jinja_filters import jinja_filters
        from routes.api.api_routes import api

        app.register_blueprint(main)
        app.register_blueprint(errors)
        app.register_blueprint(jinja_filters)
        app.register_blueprint(api)

    # Check if home folder exists, if not create
    home = str(Path.home())
    home_path = os.path.join(home, '.dmtnt/')
    try:
        os.makedirs(os.path.dirname(home_path))
    except Exception:
        pass

    return app


def create_loginmanager(app):
    app.login_manager = LoginManager()
    # If login required - go to login:
    app.login_manager.login_view = "main.main_page"
    # To display messages - info class (Bootstrap)
    app.login_manager.login_message_category = "secondary"
    app.login_manager.init_app(app)

    @app.login_manager.user_loader
    def load_user(user_id):
        from models.user_models import User
        return User.query.get(int(user_id))

    return (app)


def create_db(app):
    # Create empty instance of SQLAlchemy
    app.db = SQLAlchemy()
    app.db.init_app(app)

    # Import models so tables are created
    from models.user_models import User

    try:
        app.db.create_all()
    except Exception:
        pass

    return (app)


def main(debug=False, reloader=False):

    # Make sure current libraries are found in path
    current_path = os.path.abspath(os.path.dirname(__file__))

    # CLS + Welcome
    print("")
    print("")
    print(yellow("Launching Application ..."))
    print("")

    app = init_app()
    app.app_context().push()
    app = create_loginmanager(app)
    app.app_context().push()

    def close_running_threads(app):
        print("")
        print("")
        print(yellow("[i] Please Wait... Shutting down."))
        # Delete Debug File
        try:
            from backend.config import Config
            os.remove(Config.debug_file)
        except FileNotFoundError:
            pass
        # Breaks background jobs
        # app.scheduler.shutdown(wait=False)
        goodbye()
        os._exit(1)

    # Register the def above to run at close
    atexit.register(close_running_threads, app)

    def onion_string():
        from backend.utils import pickle_it
        if app.settings['SERVER'].getboolean('onion_server'):
            try:
                pickle_it('save', 'onion_address.pkl',
                          app.tor_service_id + '.onion')
                return (f"""
        {emoji.emojize(':onion:')} Tor Onion server running at:
        {yellow(app.tor_service_id + '.onion')}
                    """)
            except Exception:
                return (yellow("[!] Tor Onion Server Not Running"))
        else:
            return ('')

    def local_network_string():
        from backend.utils import get_local_ip
        host = app.settings['SERVER'].get('host')
        port = str(app.settings['SERVER'].getint('port'))
        if host == '0.0.0.0':
            return (f"""
      Or through your network at address:
      {yellow('http://')}{yellow(get_local_ip())}{yellow(f':{port}/')}
                """)

    port = app.settings['SERVER'].getint('port')

    # Check if this port is available
    from backend.utils import is_port_in_use
    ports = [5000, 5001, 5002, 5003, 5004, 5005, 5006, 5007, 5008, 5009, 5010]
    if is_port_in_use(port) is True:
        # Ooops. Port in use... Let's try other ports...
        for p in ports:
            if is_port_in_use(p) is False:
                print(
                    warning(
                        f"[i] Please note that port {str(port)} is in use."))
                print(
                    warning(
                        f"[i] Port was automatically changed to {str(p)} which is free."
                    ))
                # Reassign port
                port = p
                app.settings['SERVER']['port'] = str(port)
                break

    print("")

    print(f"""
      Project Salazar
      {yellow("Dead Men Tell No Tales")} {emoji.emojize(':skull:')}

      {success("Server is Running")}
      Open your browser and navigate to one of these addresses:
      {yellow('http://localhost:' + str(port) + '/')}
      {yellow('http://127.0.0.1:' + str(port) + '/')}
      {local_network_string()}
      {onion_string()}
    ----------------------------------------------------------------
                         CTRL + C to quit server
    ----------------------------------------------------------------

    """)

    # Try to launch webbrowser and open the url
    # try:
    #     import webbrowser
    #     webbrowser.open('http://localhost:' + str(port) + '/')
    # except Exception:
    #     pass

    return app


def goodbye():
    for n in range(0, 100):
        print("")
    print(
        fg.brightgreen("""
   \ \ / (_)_ _ ___ ___
    \ V /| | '_/ -_|_-<
     \_/ |_|_| \___/__/
           (_)_ _
    _  _   | | '  |         _
   | \| |_ |_|_||_| ___ _ _(_)___
   | .` | || | '  \/ -_) '_| (_-<
   |_|\_|\_,_|_|_|_\___|_| |_/__/
"""))

    print("")
    print(fg.brightgreen("    Server Stopped. Goodbye."))
    print("")
