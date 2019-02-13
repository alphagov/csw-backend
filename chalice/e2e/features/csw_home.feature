# Google Feature
Feature: Google Search Functionality
    Scenario: can find search results
        When visit url "https://2adjy710nc.execute-api.eu-west-1.amazonaws.com/app"
        Then header with class "govuk-header__link--service-name" equals "Cloud Security Watch"
