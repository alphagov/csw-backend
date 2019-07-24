import peewee
from app import app  # used only for logging
from chalicelib import database_handle
from chalicelib.peewee_models.user import User
from chalicelib.peewee_models.product_team import ProductTeam


class ProductTeamUser(database_handle.BaseModel):
    """
    Link product team records to user accounts in order to limit access
    """

    user_id = peewee.ForeignKeyField(User, backref="sessions")
    team_id = peewee.ForeignKeyField(ProductTeam, backref="account_subscriptions")

    class Meta:
        table_name = "product_team_user"


