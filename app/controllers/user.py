"""
IMPORTANT: This file is automatically generated. Do not edit directly.

Copyright (c) Sirvan Almasi. All rights reserved.
You must not remove this notice, or any other, from this software.
"""


from quart import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    jsonify,
    url_for,
)

from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)

from app import db
from datetime import date, datetime
from app.decorators import admin_required
from app.models import User, UserSchema
from app.forms import NewUserForm, NewUserAdminForm, NewUserRawForm
import json
from .resource import get_resource

user = Blueprint('user', __name__, url_prefix='/user')

"""
GET
many and one
"""
@user.route('/', methods=['GET'])
@login_required
def get_user():
    """Endpoint to GET resources from database"""
    # Parameters
    id = request.args.get('id', default = None, type = int)
    owner = request.args.get('owner', default = 'False', type = str)
    response_format = request.args.get('format', default = 'json', type = str)
    owner = True if owner == 'True' else False
    # Get the model as a dictionary
    schema = get_resource(User,
                    UserSchema,
                    force_owner=owner,
                    resource_id=id)

    if response_format == 'json':
        return json.dumps(schema)
    else:
        return json.dumps(schema)

"""
POST
"""
@user.route('/js', methods=['POST'])
@login_required
def create_user():
    data = request.form
    obj = User(
        first_name = data['first_name'],
        last_name = data['last_name'],
        email = data['email'],
        dob = data['dob'],
        gender = data['gender'],
        twitter_url = data['twitter_url'],
        linkedin_url = data['linkedin_url'],
        facebook_url = data['facebook_url'],
        personal_url = data['personal_url'],
        skillset = data['skillset'],
        )
    db.session.add(obj)
    db.session.commit()
    obj_id = {"status": "OK", "id": obj.id}
    return obj_id


@user.route('/', methods=['POST'])
@login_required
async def create_item():
    """ This endpoint is generated automatically. DO NOT edit here."""
    form = NewUserRawForm()
    if form.validate_on_submit():
        user_id = int(current_user.get_id())

        

        
        obj = User(
            first_name = form.first_name.data,
            last_name = form.last_name.data,
            email = form.email.data,
            dob = form.dob.data,
            gender = form.gender.data,
            twitter_url = form.twitter_url.data,
            linkedin_url = form.linkedin_url.data,
            facebook_url = form.facebook_url.data,
            personal_url = form.personal_url.data,
            skillset = form.skillset.data,
            )

        db.session.add(obj)
        db.session.commit()

    return jsonify({'status': 'OK'})


@user.route('/post', methods=['GET', 'POST'])
@login_required
async def new_user_form():
    """ This endpoint is generated automatically. DO NOT edit here."""
    form = NewUserForm()
    if form.validate_on_submit():
        user_id = int(current_user.get_id())

        

        
        obj = User(
            first_name = form.first_name.data,
            last_name = form.last_name.data,
            email = form.email.data,
            dob = form.dob.data,
            gender = form.gender.data,
            twitter_url = form.twitter_url.data,
            linkedin_url = form.linkedin_url.data,
            facebook_url = form.facebook_url.data,
            personal_url = form.personal_url.data,
            skillset = form.skillset.data,
            )

        db.session.add(obj)
        db.session.commit()
        await flash('User successfully created', 'form-success')
    return await render_template('forms/user.html', form=form, admin=False)


@user.route('/post/admin', methods=['GET', 'POST'])
@login_required
@admin_required
async def new_user_admin_form():
    """ This endpoint is generated automatically. DO NOT edit here."""
    form = NewUserAdminForm()
    if form.validate_on_submit():
        user_id = int(current_user.get_id())
        
        obj = User(
            confirmed = form.confirmed.data,
            first_name = form.first_name.data,
            last_name = form.last_name.data,
            email = form.email.data,
            password_hash = form.password_hash.data,
            role_id = form.role_id.data,
            last_login = form.last_login.data,
            created_by_admin = form.created_by_admin.data,
            premium = form.premium.data,
            dob = form.dob.data,
            gender = form.gender.data,
            twitter_url = form.twitter_url.data,
            linkedin_url = form.linkedin_url.data,
            facebook_url = form.facebook_url.data,
            personal_url = form.personal_url.data,
            skillset = form.skillset.data,
            )
        db.session.add(obj)
        db.session.commit()
        await flash('User successfully created', 'form-success')
    return await render_template('forms/user.html', form=form, admin=True)

"""
DELETE
"""
@user.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    pass

"""
PUT
"""

# INSERT YOUR CUSTOM CODE BELOW. DO NOT EDIT THIS OR THE ABOVE.
################################################################################
from .advert import get_advert_items
from app.models import Idea, IdeaSchema, Advert, AdvertSchema

@user.route('/<int:user_id>')
def get_user_profile(user_id):
    schema = get_resource(User,
                UserSchema,
                force_owner=False,
                resource_id=user_id)

    posts = get_advert_items(post_owner_id=user_id)
    posts_count = len(posts)

    ideas_count = Idea.query.filter_by(owner_id=int(user_id)).count()

    return render_template('profile/user_profile.html',
                           user=schema[0],
                           posts_count=posts_count,
                           ideas_count=ideas_count,
                           current_page='posts',
                           posts=posts)


@user.route('/<int:user_id>/ideas')
def get_user_profile_ideas(user_id):
    """Get the ideas for the public user profile"""
    schema = get_resource(User,
                UserSchema,
                force_owner=False,
                resource_id=user_id)


    ideas_query = Idea.query.filter_by(owner_id=int(user_id))
    ideas_count = ideas_query.count()
    ideas_all = ideas_query.all()
    ideas = IdeaSchema(many=True).get_dict(ideas_all)

    posts_count = Advert.query.filter_by(owner_id=int(user_id)).count()

    return render_template('profile/user_profile_ideas.html',
                           user=schema[0],
                           ideas_count=ideas_count,
                           posts_count=posts_count,
                           current_page='ideas',
                           ideas=ideas)