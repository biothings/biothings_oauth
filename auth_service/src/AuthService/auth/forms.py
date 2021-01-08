from wtforms import (
    # Field types
    StringField, TextAreaField, SelectField,
    # Other
    Form, validators
)

from auth.models import ClientType


class ApiForm(Form):
    """
    API model form.
    """
    name = StringField(
        'Name', [validators.Length(max=256)], render_kw={"maxlength": 256}
    )
    identifier = StringField(
        'Identifier',
        [validators.Length(max=256), validators.DataRequired()],
        render_kw={"maxlength": 256}
    )
    description = TextAreaField(
        'Description',
        [validators.Length(max=512)],
        render_kw={"maxlength": 512}
    )


class ClientForm(Form):
    """
    Client model form.
    """
    name = StringField(
        'Name',
        [validators.Length(max=256), validators.DataRequired()],
        render_kw={"maxlength": 256}
    )
    type = SelectField(
        "Type",
        [validators.DataRequired()],
        choices=[(choice.name, choice.value) for choice in ClientType]
    )

    # user = todo
