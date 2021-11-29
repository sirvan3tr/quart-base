"""
IMPORTANT: This file is automatically generated. Do not edit directly.

Copyright (c) Sirvan Almasi. All rights reserved.
You must not remove this notice, or any other, from this software.
"""


from quart import current_app
from flask_login import AnonymousUserMixin, UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from werkzeug.security import check_password_hash, generate_password_hash
import json

from .. import db, login_manager, ma
from .base import BaseSchema

from datetime import date, datetime


class Permission:
    GENERAL = 0x01
    ADMINISTER = 0xff


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    index = db.Column(db.String(64))
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.GENERAL, 'main', True),
            'Administrator': (
                Permission.ADMINISTER,
                'admin',
                False  # grants all permissions
            )
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.index = roles[r][1]
            role.default = roles[r][2]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role \'%s\'>' % self.name


class User(UserMixin, db.Model):
    """n/a"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    confirmed = db.Column(db.Boolean, default=False)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    created_by_admin = db.Column(db.Boolean, default=False)
    premium = db.Column(db.Boolean, default=False)
    dob = db.Column(db.Date)
    gender = db.Column(db.String(32), default=None)
    twitter_url = db.Column(db.String(64))
    linkedin_url = db.Column(db.String(64))
    facebook_url = db.Column(db.String(64))
    personal_url = db.Column(db.String(64))
    skillset = db.Column(db.String(255))
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN_EMAIL']:
                self.role = Role.query.filter_by(
                    permissions=Permission.ADMINISTER).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def get_field_permissions(user_type, method) -> list:
        """ IMPORTANT: This function is generated programmatically. Do not
        modify this directly here.

        For a given user type, e.g. admin, get the fields that the user is
        able to interact with using the various HTTP methods."""
        data = {
    "admin": {
        "GET": [
            "id",
            "confirmed",
            "first_name",
            "last_name",
            "email",
            "role_id",
            "date_created",
            "last_login",
            "created_by_admin",
            "premium",
            "dob",
            "gender"
        ],
        "PUT": [
            "twitter_url",
            "linkedin_url",
            "facebook_url",
            "personal_url",
            "skillset"
        ]
    },
    "auth": {
        "GET": [
            "id",
            "first_name",
            "last_name",
            "last_login",
            "twitter_url",
            "linkedin_url",
            "facebook_url",
            "personal_url",
            "skillset"
        ],
        "POST": [
            "first_name",
            "last_name",
            "email",
            "dob",
            "gender",
            "twitter_url",
            "linkedin_url",
            "facebook_url",
            "personal_url",
            "skillset"
        ]
    },
    "owner": {
        "GET": [
            "confirmed",
            "email",
            "date_created",
            "created_by_admin",
            "premium",
            "dob",
            "gender"
        ],
        "PUT": [
            "twitter_url",
            "linkedin_url",
            "facebook_url",
            "personal_url",
            "skillset"
        ]
    }
}
        return data[user_type][method]

    def get_user_types() -> list:
        """ IMPORTANT: This function is generated programmatically. Do not
        modify this directly here.

        User types are in order of importance:
            * admin: Can fetch or has most power.
            * owner: Can fetch most of their own fields.
            * dynamic: Filter based on other tables.
            * auth: Authenticated user, i.e. logged in.
            * anon: Anonymous user, i.e. not logged in.
        """
        return [["static", "admin"], ["static", "auth"], ["static", "owner"]]

    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_public_user(self):
        """Get public information for a user.
        TODO: Implement error handling"""
        return {'id': self.id,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'email': self.email}

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_admin(self):
        return self.can(Permission.ADMINISTER)

    def get_id(self):
        try:
            return str(self.id)
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')

    @property
    def password(self):
        raise AttributeError('`password` is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=604800):
        """Generate a confirmation token to email a new user."""

        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def generate_email_change_token(self, new_email, expiration=3600):
        """Generate an email change token to email an existing user."""
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def generate_password_reset_token(self, expiration=3600):
        """
        Generate a password reset change token to email to an existing user.
        """
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def confirm_account(self, token):
        """Verify that the provided token is for this user's id."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except (BadSignature, SignatureExpired):
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def change_email(self, token):
        """Verify the new email for this user."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except (BadSignature, SignatureExpired):
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        db.session.commit()
        return True

    def reset_password(self, token, new_password):
        """Verify the new password for this user."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except (BadSignature, SignatureExpired):
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        db.session.commit()
        return True

    @staticmethod
    def generate_fake(count=100, **kwargs):
        """Generate a number of fake users for testing."""
        from sqlalchemy.exc import IntegrityError
        from random import seed, choice
        from faker import Faker

        fake = Faker()
        roles = Role.query.all()

        seed()
        for i in range(count):
            u = User(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                password='password',
                confirmed=True,
                role=choice(roles),
                **kwargs)
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return '<User \'%s\'>' % self.full_name()


class AnonymousUser(AnonymousUserMixin):
    def can(self, _):
        return False

    def is_admin(self):
        return False


login_manager.anonymous_user = AnonymousUser


class UserSchema(BaseSchema):
    class Meta:
        model = User
        include_fk = True


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class UserSchema(ma.SQLAlchemyAutoSchema):
    """Flask Marshmallow class for the user table"""
    class Meta:
        model = User 
        include_fk = True

    def get_dict(self, the_query):
        """Gets a json version of model and then convert it back into
        a python object."""
        the_dump = self.dumps(the_query)
        return json.loads(the_dump)