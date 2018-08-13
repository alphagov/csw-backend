import os
from peewee import PostgresqlDatabase, Model
from peewee import CharField, TextField, DateField, BooleanField, IntegerField, ForeignKeyField


class DatabaseHandle():

    handle = None
    models = dict()

    def get_env_var(self, var_name):

        try:
            value = os.environ[var_name]
        except Exception:
            value = ""

        return value

    def get_handle(self):

        if self.handle is None:
            db_host = self.get_env_var('CSW_HOST')
            db_port = self.get_env_var('CSW_PORT')
            db_user = self.get_env_var('CSW_USER')
            db_password = self.get_env_var('CSW_PASSWORD')

            self.handle = PostgresqlDatabase(
                'csw',
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port
            )

        return self.handle

    def create_tables(self, tables):

        try:
            db = self.get_handle()
            db.connect()

            db.create_tables(
                tables,
                safe=True
            )

            db.close()

            status = True

        except Exception as e:
            status = False

        return status

    def add_model(self, model_name, model_class):
        self.models[model_name] = model_class

    def get_model(self, model_name):

        return self.models[model_name]


dbh = DatabaseHandle()
db = dbh.get_handle()

'''
-- table to store
CREATE TABLE cloud_security_watch.csw_aws_api_cache (
    id SERIAL,
    account_id REFERENCES cloud_security_watch.csw_subscription(account_id),
    domain VARCHAR(100) NOT NULL,
    method VARCHAR(100) NOT NULL,
    params VARCHAR(100) NOT NULL,
    response JSON,
    expires DATETIME
);
'''

'''
-- Create a product team reference table to link AWS
-- accounts to the teams who they belong to
CREATE TABLE cloud_security_watch.csw_product_team (
    id SERIAL,
    team_name VARCHAR(80) NOT NULL,
    active BOOLEAN DEFAULT FALSE
);
'''


class BaseModel(Model):

    class Meta:
        database = db
        schema = "public"


class ProductTeam(BaseModel):
    team_name = CharField()
    active = BooleanField()

    class Meta:
        table_name = "product_team"


dbh.add_model("ProductTeam", ProductTeam)


'''
-- Create a subscriptions table which designates
-- which AWS accounts we should scan
CREATE TABLE cloud_security_watch.csw_subscription (
    id SERIAL,
    account_id  INT UNSIGNED,
    team_id INT UNSIGNED REFERENCES cloud_security_watch.csw_product_team(id),
    active BOOLEAN DEFAULT FALSE
);
'''


class AccountSubscription(BaseModel):
    account_id = IntegerField(),
    account_name = CharField(),
    product_team_id = ForeignKeyField(ProductTeam, backref='product_team'),
    active = BooleanField()

    class Meta:
        table_name = "account_subscription"


dbh.add_model("AccountSubscription", AccountSubscription)


'''
-- eg Trusted Advisor, Config ...
-- invoke_class_name like GdsSupportClient for Trusted Advisor
CREATE TABLE cloud_security_watch.csw_metric_provider (
    id SERIAL,
    provider_name VARCHAR(100) NOT NULL,
    invoke_class_name VARCHAR(100) NOT NULL
);
'''


class MetricProvider(BaseModel):
    provider_name = CharField(),
    invoke_class_name = CharField()

    class Meta:
        table_name = "metric_provider"


dbh.add_model("MetricProvider", MetricProvider)


'''
-- eg Trusted Advisor - Security Groups - Specific Ports Unrestricted
-- invoke_class_method like describe_trusted_advisor_check_result
CREATE TABLE cloud_security_watch.csw_metric (
    id SERIAL,
    metric_name VARCHAR(100) NOT NULL,
    metric_provider_id INT UNSIGNED REFERENCES cloud_security_watch.cst_metric_provider(id),
    invoke_class_method VARCHAR(100) NOT NULL
);
'''


class Metric(BaseModel):
    metric_name = CharField(),
    metric_provider_id = ForeignKeyField(MetricProvider, backref='metric_provider'),
    invoke_class_get_data_method = CharField(),
    evaluation_lambda_function = CharField()

    class Meta:
        table_name = "metric"


dbh.add_model("Metric", Metric)

'''
-- Primarily for trusted advisor checks specifies arguments that need to be provided
-- eg 	region=us-east-1
--		language=en
--		checkId=HCP4007jGY (for Security Groups - Specific Ports Unrestricted)
-- region and possibly language could be hard-coded rather than passing them through the db each time
-- TODO ADD SEVERITY ?
CREATE TABLE cloud_security_watch.csw_metric_params (
    id SERIAL,
    metric_id INT UNSIGNED REFERENCES cloud_security_watch.cst_metric(id),
    param_name VARCHAR(100),
    param_value VARCHAR(100)
);
'''


class MetricParams(BaseModel):
    metric_id = ForeignKeyField(Metric, backref='metric'),
    param_name = CharField(),
    param_value = CharField()

    class Meta:
        table_name = "metric_params"


dbh.add_model("MetricParams", MetricParams)

'''
-- We may want more statuses than Red/Amber/Green
CREATE TABLE cloud_security_watch.csw_status (
    id SERIAL,
    status_name VARCHAR(20),
    description TEXT
);
'''


class Status(BaseModel):
    status_name = CharField(),
    description = TextField()

    class Meta:
        table_name = "status"


dbh.add_model("Status", Status)


'''
-- For metrics and accepted risks we can associate a severity which
-- allows us to float higher value issues to the top
CREATE TABLE cloud_security_watch.csw_severity (
    id SERIAL,
    severity_name VARCHAR(20),
    description TEXT
);
'''


class Severity(BaseModel):
    severity_name = CharField(),
    description = TextField()

    class Meta:
        table_name = "severity"


dbh.add_model("Severity", Severity)


'''
-- For metrics and accepted risks we can associate a severity which
-- allows us to float higher value issues to the top
-- notification classes should extend a base Notification class
-- and then override a notify method
CREATE TABLE cloud_security_watch.csw_notification_method (
    id SERIAL,
    system_name VARCHAR(20),
    description TEXT,
    class_name VARCHAR(100)
);
'''


# This is a stub that will need to be expanded to enable reporting to things like ZenDesk
class NotificationMethod(BaseModel):
    system_name = CharField(),
    description = TextField(),
    invoke_class_name = CharField()

    class Meta:
        table_name = "notification_method"


dbh.add_model("NotificationMethod", NotificationMethod)


'''
-- This is where we store the results of quering the API
-- This should include "green" status checks as well as
-- identified risks.
CREATE TABLE cloud_security_watch.csw_metric_status (
    id SERIAL,
    metric_id INT UNSIGNED REFERENCES cloud_security_watch.cst_metric(id),
    account_id REFERENCES cloud_security_watch.csw_subscription(account_id),
    resource_arn VARCHAR(100) NOT NULL,
    status_id INT UNSIGNED REFERENCES cloud_security_watch.csw_status(id),
    date_last_checked DATETIME,
    date_last_changed DATETIME
);
'''


class MetricStatus(BaseModel):
    metric_id = ForeignKeyField(Metric, backref='metric'),
    account_subscription_id = ForeignKeyField(AccountSubscription, backref='subscription'),
    resource_arn = CharField(),
    status_id = ForeignKeyField(Status, backref='status'),
    date_last_checked = DateField(),
    date_last_changed = DateField()

    class Meta:
        table_name = "metric_status"


dbh.add_model("MetricStatus", MetricStatus)


'''
-- For non-green status issues we record a risk record
CREATE TABLE cloud_security_watch.csw_metric_status_risk (
    id SERIAL,
    date_first_identified DATETIME,
    date_last_notified DATETIME,
    notification_method INT UNSIGNED REFERENCES cloud_security_watch.csw_notification_method(id),
    date_of_review DATETIME,
    accepted_risk BOOLEAN DEFAULT FALSE,
    analyst_assessed BOOLEAN DEFAULT FALSE,
    assessment_severity INT UNSIGNED REFERENCES cloud_security_watch.csw_severity(id)
);
'''


class MetricStatusRisk(BaseModel):
    metric_id = ForeignKeyField(Metric, backref='metric'),
    account_subscription_id = ForeignKeyField(AccountSubscription, backref='subscription'),
    resource_arn = CharField(),
    date_first_identifed = DateField(),
    date_last_notifier = DateField(),
    notification_method = ForeignKeyField(NotificationMethod, backref='notification_method'),
    date_of_review = DateField(),
    accepted_risk = BooleanField(),
    analyst_assessed = BooleanField(),
    assessment_severity = ForeignKeyField(Severity, backref='severity')

    class Meta:
        table_name = "metric_status_risk"


dbh.add_model("MetricStatusRisk", MetricStatusRisk)


'''
-- TODO - Do we calculate the aggregations or index the tables and aggregate on the fly ?
'''
