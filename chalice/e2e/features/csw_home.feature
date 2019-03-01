# Cloud Security Watch - Homepage Feature
Feature: Cloud Security Watch - Homepage loads
    Scenario: can load homepage
        When you navigate to CSW homepage
        Then the content of element with selector ".govuk-header__link--service-name" equals "Cloud Security Watch"
