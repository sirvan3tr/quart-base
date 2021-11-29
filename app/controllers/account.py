from quart import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    session,
    jsonify,
)
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)
# from flask_rq import get_queue

from app import db
from app.controllers.forms_account import (
    ChangeEmailForm,
    ChangePasswordForm,
    CreatePasswordForm,
    LoginForm,
    RegistrationForm,
    RequestResetPasswordForm,
    ResetPasswordForm,
)
from app.email import send_email
from app.models import User
from app import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from werkzeug.utils import secure_filename
import os
from PIL import Image
from quart_cors import route_cors
from app.decorators import jwt_required
from quart import make_response
from flask_wtf.csrf import generate_csrf

account = Blueprint('account', __name__, url_prefix='/account')

@account.route('/cognito', methods=['GET'])
@route_cors()
@jwt_required
def cognito(**kwargs):
    print(kwargs['jwt_claim']['sub'])
    print(">>>>>>>>> COGNITO", request.headers)
    return jsonify({"status": "OK"})

async def _build_cors_preflight_response():
    response = await make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify_actual_response(response):
    response.headers.add("access-control-allow-origin", "*")
    return response


@account.route('/csrf')
@route_cors()
def get_csrf():
    return {"csrftoken": generate_csrf() }


@account.route('/logx', methods=['GET', 'POST'])
@login_required
def loginneeded():
    return "HELLORORORE"
    # return jsonify(current_user.get_public_user())


@account.route('/idea1', methods=['GET', 'POST', 'OPTIONS'])
@route_cors(
    allow_headers=["access-control-allow-origin", "Access-Control-Allow-Origin", "x-amz-date", "authorization", "x-amz-security-token", "DNT",
    "User-Agent", "X-Requested-With", "If-Modified-Since", "Cache-Control", "Content-Type",
    "Range"],
    allow_origin=["*"],
    allow_methods=['GET', 'PUT', 'POST', 'OPTIONS'])
async def idea1():
    # if request.method == "POST": # CORS preflight
    #     return await _build_cors_preflight_response()
    print(">>>>>>>>> IDEA", request.headers)
    return jsonify({"tick": 1})

@account.route('/idea', methods=['GET', 'POST', 'OPTIONS'])
async def idea():
    print(">>>>>>>>> IDEA", request.headers)
    return jsonify({"tick": 1})

# 'headers': {
#     'Access-Control-Allow-Headers': 'Content-Type',
#     'Access-Control-Allow-Origin': '*',
#     'Access-Control-Allow-Methods': 'OPTIONS,PUT',
#     'Content-Type': 'application/json',
# }    resp.headers = 

@account.route('/login/json', methods=['POST'])
async def login_json():
    """Log in an existing user."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.password_hash is not None and \
                user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)

            session['user'] = user.get_public_user()
            await flash('You are now logged in. Welcome back!', 'success')
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            return jsonify({'error': 'sum ting went wong'})
    return jsonify({'status': 'logged in'})


@account.route('/login', methods=['GET', 'POST', 'OPTIONS'])
async def login():
    """Log in an existing user."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.password_hash is not None and \
                user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)

            session['user'] = user.get_public_user()
            await flash('You are now logged in. Welcome back!', 'success')
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            await flash('Invalid email or password.', 'error')
    return await render_template('account/login.html', form=form)


@account.route('/register', methods=['GET', 'POST'])
async def register():
    """Register a new user, and send them a confirmation email."""
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        confirm_link = url_for('account.confirm', token=token, _external=True)
        await flash('A confirmation link has been sent to {}.'.format(user.email),
              'warning')
        await send_email(recipient=user.email,
            subject='Confirm Your Account',
            template='account/email/confirm',
            user=user,
            confirm_link=confirm_link)
        """
        TODO: use redis for sending email.
        get_queue().enqueue(
            send_email,
            recipient=user.email,
            subject='Confirm Your Account',
            template='account/email/confirm',
            user=user,
            confirm_link=confirm_link)
        """
        return redirect(url_for('main.index'))
    # image = ImageCaptcha()
    # data = image.generate('1234')
    # image.write('1234', os.path.join(UPLOAD_FOLDER, 'out.jpg'))
    return await render_template('account/register.html', form=form)


@account.route('/logout')
@login_required
async def logout():
    logout_user()
    session.clear()
    await flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@account.route('/manage', methods=['GET', 'POST'])
@login_required
def manage():
    """Display a user's account information."""
    return render_template('account/manage.html', user=current_user, form=None)


@account.route('/reset-password', methods=['GET', 'POST'])
async def reset_password_request():
    """Respond to existing user's request to reset their password."""
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = RequestResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_password_reset_token()
            reset_link = url_for(
                'account.reset_password', token=token, _external=True)
            # TODO: Fix redis integration
            # get_queue().enqueue(
            #     send_email,
            #     recipient=user.email,
            #     subject='Reset Your Password',
            #     template='account/email/reset_password',
            #     user=user,
            #     reset_link=reset_link,
            #     next=request.args.get('next'))
        await flash('A password reset link has been sent to {}.'.format(
            form.email.data), 'warning')
        return redirect(url_for('account.login'))
    return await render_template('account/reset_password.html', form=form)


@account.route('/reset-password/<token>', methods=['GET', 'POST'])
async def reset_password(token):
    """Reset an existing user's password."""
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            await flash('Invalid email address.', 'form-error')
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.new_password.data):
            await flash('Your password has been updated.', 'form-success')
            return redirect(url_for('account.login'))
        else:
            await flash('The password reset link is invalid or has expired.',
                  'form-error')
            return redirect(url_for('main.index'))
    return await render_template('account/reset_password.html', form=form)


@account.route('/manage/change-password', methods=['GET', 'POST'])
@login_required
async def change_password():
    """Change an existing user's password."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            await flash('Your password has been updated.', 'form-success')
            return redirect(url_for('main.index'))
        else:
            await flash('Original password is invalid.', 'form-error')
    return await render_template('account/manage.html', user=current_user, form=form)


@account.route('/manage/change-email', methods=['GET', 'POST'])
@login_required
async def change_email_request():
    """Respond to existing user's request to change their email."""
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            change_email_link = url_for(
                'account.change_email', token=token, _external=True)
            # TODO: Fix redis integration
            # get_queue().enqueue(
            #     send_email,
            #     recipient=new_email,
            #     subject='Confirm Your New Email',
            #     template='account/email/change_email',
            #     # current_user is a LocalProxy, we want the underlying user
            #     # object
            #     user=current_user._get_current_object(),
            #     change_email_link=change_email_link)
            await flash('A confirmation link has been sent to {}.'.format(new_email),
                  'warning')
            return redirect(url_for('main.index'))
        else:
            await flash('Invalid email or password.', 'form-error')
    return await render_template('account/manage.html', user=current_user, form=form)


@account.route('/manage/change-email/<token>', methods=['GET', 'POST'])
@login_required
async def change_email(token):
    """Change existing user's email with provided token."""
    if current_user.change_email(token):
        await flash('Your email address has been updated.', 'success')
    else:
        await flash('The confirmation link is invalid or has expired.', 'error')
    return redirect(url_for('main.index'))


@account.route('/confirm-account')
@login_required
async def confirm_request():
    """Respond to new user's request to confirm their account."""
    # db.session.expunge_all()
    token = current_user.generate_confirmation_token()
    confirm_link = url_for('account.confirm', token=token, _external=True)
    user = current_user._get_current_object()
    await send_email(recipient=current_user.email,
        subject='Confirm Your Account',
        template='account/email/confirm',
        # current_user is a LocalProxy, we want the underlying user object
        user=user,
        confirm_link=confirm_link)
    await flash('A new confirmation link has been sent to {}.'.format(
        current_user.email), 'warning')
    return redirect(url_for('main.index'))


@account.route('/confirm-account/<token>')
@login_required
async def confirm(token):
    """Confirm new user's account with provided token."""
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm_account(token):
        await flash('Your account has been confirmed.', 'success')
    else:
        await flash('The confirmation link is invalid or has expired.', 'error')
    return redirect(url_for('main.index'))


@account.route(
    '/join-from-invite/<int:user_id>/<token>', methods=['GET', 'POST'])
async def join_from_invite(user_id, token):
    """
    Confirm new user's account with provided token and prompt them to set
    a password.
    """
    if current_user is not None and current_user.is_authenticated:
        await flash('You are already logged in.', 'error')
        return redirect(url_for('main.index'))

    new_user = User.query.get(user_id)
    if new_user is None:
        return redirect(404)

    if new_user.password_hash is not None:
        await flash('You have already joined.', 'error')
        return redirect(url_for('main.index'))

    if new_user.confirm_account(token):
        form = CreatePasswordForm()
        if form.validate_on_submit():
            new_user.password = form.password.data
            db.session.add(new_user)
            db.session.commit()
            await flash('Your password has been set. After you log in, you can '
                  'go to the "Your Account" page to review your account '
                  'information and settings.', 'success')
            return redirect(url_for('account.login'))
        return await render_template('account/join_invite.html', form=form)
    else:
        await flash('The confirmation link is invalid or has expired. Another '
              'invite email with a new link has been sent to you.', 'error')
        token = new_user.generate_confirmation_token()
        invite_link = url_for(
            'account.join_from_invite',
            user_id=user_id,
            token=token,
            _external=True)
        # TODO: Fix redis integration
        # get_queue().enqueue(
        #     send_email,
        #     recipient=new_user.email,
        #     subject='You Are Invited To Join',
        #     template='account/email/invite',
        #     user=new_user,
        #     invite_link=invite_link)
    return redirect(url_for('main.index'))


@account.before_app_request
def before_request():
    """Force user to confirm email before accessing login-required routes."""
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint[:8] != 'account.' \
            and request.endpoint != 'static':
        return redirect(url_for('account.unconfirmed'))


@account.route('/unconfirmed')
def unconfirmed():
    """Catch users with unconfirmed emails."""
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('account/unconfirmed.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_extension(filename):
    return filename.rsplit('.', 1)[1].lower()


@account.route('/avatar', methods=['POST'])
@login_required
async def upload_avatar():
    # check if the post request has the file part
    data = await request.files
    if 'file' not in data:
        await flash('No file part')
        return "No file part"
        # return redirect(request.url)
    file = data['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        await flash('No selected file')
        return "No file selected"
        # return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # filename = f'avatar_{current_user.get_id()}.{get_extension(filename)}'
        filename = f'avatar_{current_user.get_id()}.jpg'
        # resize the image
        basewidth = 260
        img = Image.open(file)
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((basewidth, hsize), Image.ANTIALIAS)
        # save the image
        img.save(os.path.join(UPLOAD_FOLDER, filename))

        return {'filename': filename}
        # return redirect(url_for('uploaded_file',
        #                        filename=filename))
