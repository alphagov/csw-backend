# Cloud Security Watch - Homepage Feature
Feature: Cloud Security Watch - Team Status page loads
    Scenario: can load homepage
        When you navigate to CSW page "team/1/status"
        Then the content of element with selector ".govuk-header__link--service-name" equals "Cloud Security Watch"