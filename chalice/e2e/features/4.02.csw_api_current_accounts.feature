# Cloud Security Watch - API /current/accounts
# Check that a status=ok response is returned and that the fields exists and have the correct types.
Feature: Cloud Security Watch - API /current/accounts
    Scenario: can load api/current/accounts endpoint
        When you make an unauthenticated http get request to "api/current/accounts"
        Then response code is "403"
        Then body is valid json
        Then "status" exists and has value "failed"
        Then "message" exists and has value "Unauthorised"
        When you make an authenticated http get request to "api/current/accounts"
        Then response code is "200"
        Then body is valid json
        Then "status" exists and has value "ok"
        Then "items.0.audit_date" exists and matches pattern "\d{4}\-\d{2}\-\d{2}"
        Then "items.0.account_id.id" exists and has datatype "int"
        Then "items.0.account_id.account_id" exists and has datatype "int"
        Then "items.0.account_id.account_name" exists and has datatype "str"
        Then "items.0.account_id.product_team_id.id" exists and has datatype "int"
        Then "items.0.account_id.product_team_id.team_name" exists and has datatype "str"
        Then "items.0.account_id.product_team_id.active" exists and has datatype "bool"
        Then "items.0.account_id.active" exists and has datatype "bool"
        Then "items.0.resources" exists and has datatype "int"
        Then "items.0.failed" exists and has datatype "int"
        Then "items.0.ratio" exists and has datatype "float"