# Cloud Security Watch - API /daily/summary
# Check that a status=ok response is returned and that the fields exists and have the correct types.
Feature: Cloud Security Watch - API /daily/summary
    Scenario: can load api/daily/summary endpoint
        When you make an unauthenticated http get request to "api/daily/summary"
        Then response code is "403"
        Then body is valid json
        Then "status" exists and has value "failed"
        Then "message" exists and has value "Unauthorised"
        When you make an authenticated http get request to "api/daily/summary"
        Then response code is "200"
        Then body is valid json
        Then "status" exists and has value "ok"
        Then "items.0.audit_date" exists and has datatype "str"
        Then "items.0.audit_date" exists and matches pattern "\d{4}\-\d{2}\-\d{2}"
        Then "items.0.total_resources" exists and has datatype "float"
        Then "items.0.total_failures" exists and has datatype "float"
        Then "items.0.avg_resources_per_account" exists and has datatype "float"
        Then "items.0.avg_fails_per_account" exists and has datatype "float"
        Then "items.0.avg_percent_fails_per_account" exists and has datatype "float"
        Then "items.0.accounts_audited" exists and has datatype "int"
        Then "items.0.percent_accounts_audited" exists and has datatype "float"
