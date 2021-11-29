from quart import Blueprint, render_template, render_template_string, redirect

from app.models import EditableHTML
from app.controllers.forms_account import RegistrationForm
from quart.globals import request
from app import db


main = Blueprint('main', __name__)


@main.route('/')
def index():
    form = RegistrationForm()
    return render_template('main/index.html', form=form)


@main.route('/about')
def about():
    return render_template('main/about.html')