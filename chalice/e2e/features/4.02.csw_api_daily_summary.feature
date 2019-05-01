# Cloud Security Watch - API /daily/summary
# Check that a status=ok response is returned and that the fields exists and have the correct types.
Feature: Cloud Security Watch - API /current/summary
    Scenario: can load api/current/summary endpoint
        When you make an authenticated http get request to "api/daily/summary"
        Then response code is "200"
        Then body is valid json
        Then "status" exists and has value "ok"
        Then "items.0.audit_date" exists and matches pattern "\d{4}\-\d{2}\-\d{2}"
        Then "items.0.audit_date" exists and has datatype "str"
        #"total_resources": 597.0,
        #"total_failures": 189.0,
        #"avg_resources_per_account": 597.0,
        #"avg_fails_per_account": 189.0,
        #"avg_percent_fails_per_account": 0.316582914572864,
        #"accounts_audited": 1,
        #"percent_accounts_audited": 0.0125
