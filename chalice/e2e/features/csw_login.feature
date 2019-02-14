# Cloud Security Watch - Homepage Feature
Feature: Cloud Security Watch - Homepage loads
    Scenario: can load homepage
        Given the credentials
        When login post to "https://2adjy710nc.execute-api.eu-west-1.amazonaws.com/app/temp-login"
        Then wait "5" seconds