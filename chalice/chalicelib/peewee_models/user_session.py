import datetime
import peewee
from app import app  # used only for logging
from chalicelib import database_handle


class UserSession(database_handle.BaseModel):
    """
    UserSession records login sessions against users so we can track things
    like how often and for how long the tool is being used
    """

    date_opened = peewee.DateTimeField(default=datetime.datetime.now)
    date_accessed = peewee.DateTimeField(default=datetime.datetime.now)
    date_closed = peewee.DateTimeField(null=True)

    user_id = peewee.ForeignKeyField(User, backref="sessions")

    class Meta:
        table_name = "user_session"

    @classmethod
    def start(cls, user):
        """
        Create a new session for the current user

        Raises Exception(Not sure which one)
        :param user:
        :return:
        """

        now = datetime.datetime.now()

        session = cls.create(
            user_id=user, date_opened=now, date_accessed=now, date_closed=None
        )

        return session

    @classmethod
    def accessed(cls, user):
        """
        Update the date_accessed field with the current time

        :param user:
        :return:
        """
        session = cls.get(user_id=user, date_closed=None)

        now = datetime.datetime.now()

        # session.update(date_accessed = now)
        session.date_accessed = now
        session.save()

        return session

    @classmethod
    def close(cls, user):
        """
        Update the current session date_closed with the current time
        :param user:
        :return:
        """
        session = cls.get(user_id=user, date_closed=None)

        now = datetime.datetime.now()

        # session.update(date_accessed=now, date_closed=now)
        session.date_accessed = now
        session.date_closed = now
        session.save()

        return session


