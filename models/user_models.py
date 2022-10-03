import json
import os
from flask import current_app
from flask_login import UserMixin
from datetime import datetime

db = current_app.db

#  Models -------------


# An User is a unique login id that will be attached to Assets, Triggers and
# all other data
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    # This is the app login password
    password = db.Column(db.String(1000), nullable=False)
    # A tip to remind the user about the decryption key
    # this password is not stored anywhere and cannot be forgotten.
    # It is used to decrypt all messages and files
    decrypt_tip = db.Column(db.String())
    # This is an encrypted data with the text: "Encrypted Data"
    # and can be used to test if the decryption key is valid.
    # When decrypted this should output: "Encrypted Data"
    decrypt_test = db.Column(db.String())

    def as_dict(self):
        dict_return = {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
        }
        return (dict_return)

    def __repr__(self):
        return (json.dumps(self.as_dict(), default=str))


# Email Servers Used for communication in case of trigger events
class EmailServers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(db.DateTime,
                              nullable=False,
                              default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    mail_server = db.Column(db.String(), default="smtp.googlemail.com")
    mail_port = db.Column(db.Integer, default=587)
    mail_use_tls = db.Column(db.Boolean, default=True)
    mail_use_ssl = db.Column(db.Boolean, default=True)
    mail_username = db.Column(db.String(),
                              default=os.environ.get("EMAIL_USER"))
    mail_password = db.Column(db.String(),
                              default=os.environ.get("EMAIL_PASSWORD"))


# An Asset is a piece of data to be sent to a receiver or list of
# receivers. It could be an e-mail message, a file, a pre-signed Bitcoin TX,
# or any other data that the user would like to send in case of a trigger event.
class Assets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(db.DateTime,
                              nullable=False,
                              default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    notes = db.Column(db.Text(), default=None)
    file_path = db.Column(db.String(), default=None)
    additional_data = db.Column(db.PickleType(), default=None)

    def as_dict(self):
        dict_return = {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
        }
        return (dict_return)

    def __repr__(self):
        return (json.dumps(self.as_dict(), default=str))
