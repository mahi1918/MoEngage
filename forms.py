from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class AddReviewForm(FlaskForm):
    brewery_name = StringField('Brewery Name', validators=[DataRequired()])
    review_text = TextAreaField('Review Text', validators=[DataRequired()])
    submit = SubmitField('Save Review')