# Cloud Security Watch - Homepage Feature
Feature: Cloud Security Watch - Team Status page loads
    Scenario: can load homepage
        When visit url "https://2adjy710nc.execute-api.eu-west-1.amazonaws.com/app/team/1/status"
        Then the content of element with selector ".govuk-header__link--service-name" equals "Cloud Security Watch"