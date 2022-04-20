from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm): 
    input = StringField('Input', validators=[DataRequired(message='⚠️ QUERY CANNOT BE EMPTY')])
    submit = SubmitField('Submit')