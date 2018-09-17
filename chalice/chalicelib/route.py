from chalicelib.models import DatabaseHandle
import chalicelib.collate


def route_team_dashboard(app, team_id):

    dbh = DatabaseHandle(app)
    db = dbh.get_handle()
    db.connect()

    AccountSubscription = dbh.get_model("AccountSubscription")

    accounts = (AccountSubscription.select().where(AccountSubscription.product_team_id.id == team_id))

    app.log.debug(app.utilities.to_json(accounts))

    # team_stats = collate.get_team_stats(accounts)

    response = {
        "body": app.utilities.to_json(accounts.serialize())
    }

    # response = app.templates.render_authorized_route_template('/team/{id}/dashboard', app.current_request)

    return response


def route_overview_dashboard(app):
    dbh = DatabaseHandle(app)
    db = dbh.get_handle()
    db.connect()

    ProductTeam = dbh.get_model("ProductTeam")
    AccountLatestAudit = dbh.get_model("AccountLatestAudit")
    AccountSubscription = dbh.get_model("AccountSubscription")
    AccountAudit = dbh.get_model("AccountAudit")

