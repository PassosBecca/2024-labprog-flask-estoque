from flask_wtf import FlaskForm
from wtforms.fields.simple import SubmitField, StringField
from wtforms.validators import InputRequired


class NovoCategoriaForm(FlaskForm):
    nome = StringField('Nome da Categoria', validators=[InputRequired(message="É obrigatório informar um nome para a categoria")])
    submit = SubmitField("Adicionar")