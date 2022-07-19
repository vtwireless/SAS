from .. import database


class User(database.Model):
    """Data model for user accounts."""

    __tablename__ = 'users'

    username = database.Column(
        database.String(64),
        index=False,
        unique=False,
        nullable=False
    )

    email = database.Column(
        database.String(80),
        index=True,
        unique=True,
        nullable=False,
        primary_key=True
    )

    admin = database.Column(
        database.Boolean,
        index=False,
        unique=False,
        nullable=False
    )

    password = database.Column(
        database.String(80),
        index=False,
        unique=False,
        nullable=False
    )

    def __repr__(self):
        return {
            "username": self.username,
            "email": self.email
        }

