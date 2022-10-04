# Monitors several health stats about this node, app and server
# Stores the health checkpoints to the database
import logging
from backend.connections import internet_connected
from models.user_models import HealthCheck
from backend.comm import ntp_time
from flask_login import current_user


def check_app_running(app):
    try:
        with app.app_context():
            db = app.db
            check_point = HealthCheck()
            check_point.check_time = ntp_time()
            check_point.check_type = 'app_running'
            check_point.data = True
            try:
                check_point.user_id = current_user.user_id
            except Exception:
                check_point.user_id = 0
            db.session.add(check_point)
            db.session.commit()
    except Exception as e:
        logging.error(f"Check_app returned an error on background:\n {e}")


def check_internet(app):
    try:
        with app.app_context():
            db = app.db
            check_point = HealthCheck()
            check_point.check_time = ntp_time()
            check_point.check_type = 'internet_connected'
            check_point.data = internet_connected()
            try:
                check_point.user_id = current_user.user_id
            except Exception:
                check_point.user_id = 0
            db.session.add(check_point)
            db.session.commit()
    except Exception as e:
        logging.error(f"Check_internet returned an error on background:\n {e}")