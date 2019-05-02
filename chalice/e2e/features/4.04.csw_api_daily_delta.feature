# Cloud Security Watch - API /daily/delta
# Check that a status=ok response is returned and that the fields exists and have the correct types.
Feature: Cloud Security Watch - API /daily/delta
    Scenario: can load api/daily/delta endpoint
        When you make an unauthenticated http get request to "api/daily/delta"
        Then response code is "403"
        Then body is valid json
        Then "status" exists and has value "failed"
        Then "message" exists and has value "Unauthorised"
        When you make an authenticated http get request to "api/daily/delta"
        Then response code is "200"
        Then body is valid json
        Then "status" exists and has value "ok"
        Then "items.0.audit_date" exists and has datatype "str"
        Then "items.0.audit_date" exists and matches pattern "\d{4}\-\d{2}\-\d{2}"
        Then "items.0.resources_delta" exists and has datatype "float"
        Then "items.0.failures_delta" exists and has datatype "float"
        Then "items.0.avg_resources_delta" exists and has datatype "float"
        Then "items.0.avg_fails_delta" exists and has datatype "float"
        Then "items.0.avg_percent_fails_delta" exists and has datatype "float"
        Then "items.0.accounts_audited_delta" exists and has datatype "int"
