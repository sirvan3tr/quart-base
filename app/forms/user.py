

from wtforms.fields import (
    TextAreaField,
    BooleanField,
    StringField,
    SubmitField,
    IntegerField,
    DateTimeField,
    DateField
)
from wtforms.validators import InputRequired, Length


class NewUserForm(FlaskForm):
    first_name=StringField(validators=[InputRequired(),Length(1, 64)])
    last_name=StringField(validators=[InputRequired(),Length(1, 64)])
    email=StringField(validators=[InputRequired(),Length(1, 64)])
    dob=DateField(validators=[InputRequired(),])
    gender=StringField(validators=[InputRequired(),Length(1, 32)])
    twitter_url=StringField(validators=[InputRequired(),Length(1, 64)])
    linkedin_url=StringField(validators=[InputRequired(),Length(1, 64)])
    facebook_url=StringField(validators=[InputRequired(),Length(1, 64)])
    personal_url=StringField(validators=[InputRequired(),Length(1, 64)])
    skillset=TextAreaField(validators=[InputRequired(),])
    
    submit = SubmitField('Submit')
    

    
class NewUserRawForm(FlaskForm):
    first_name=StringField(validators=[InputRequired(),Length(1, 64)])
    last_name=StringField(validators=[InputRequired(),Length(1, 64)])
    email=StringField(validators=[InputRequired(),Length(1, 64)])
    dob=DateField(validators=[InputRequired(),])
    gender=StringField(validators=[InputRequired(),Length(1, 32)])
    twitter_url=StringField(validators=[InputRequired(),Length(1, 64)])
    linkedin_url=StringField(validators=[InputRequired(),Length(1, 64)])
    facebook_url=StringField(validators=[InputRequired(),Length(1, 64)])
    personal_url=StringField(validators=[InputRequired(),Length(1, 64)])
    skillset=TextAreaField(validators=[InputRequired(),])
    
    submit = SubmitField('Submit')
    
class NewUserAdminForm(FlaskForm):
    confirmed=BooleanField(validators=[InputRequired(),])
    first_name=StringField(validators=[InputRequired(),Length(1, 64)])
    last_name=StringField(validators=[InputRequired(),Length(1, 64)])
    email=StringField(validators=[InputRequired(),Length(1, 64)])
    password_hash=StringField(validators=[InputRequired(),Length(1, 128)])
    role_id=IntegerField(validators=[InputRequired(),])
    last_login=DateTimeField(validators=[InputRequired(),])
    created_by_admin=BooleanField(validators=[InputRequired(),])
    premium=BooleanField(validators=[InputRequired(),])
    dob=DateField(validators=[InputRequired(),])
    gender=StringField(validators=[InputRequired(),Length(1, 32)])
    twitter_url=StringField(validators=[InputRequired(),Length(1, 64)])
    linkedin_url=StringField(validators=[InputRequired(),Length(1, 64)])
    facebook_url=StringField(validators=[InputRequired(),Length(1, 64)])
    personal_url=StringField(validators=[InputRequired(),Length(1, 64)])
    skillset=TextAreaField(validators=[InputRequired(),])
    
    submit = SubmitField('Submit')
    

    