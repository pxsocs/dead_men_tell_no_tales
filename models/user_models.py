import json
from flask import current_app
from flask_login import UserMixin
from datetime import datetime

db = current_app.db

#  Models -------------


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(1000), nullable=False)

    def as_dict(self):
        dict_return = {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
        }
        return (dict_return)

    def __repr__(self):
        return (json.dumps(self.as_dict(), default=str))
