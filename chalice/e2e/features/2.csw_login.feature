# Cloud Security Watch - Homepage Feature
Feature: Cloud Security Watch - Homepage loads
    Scenario: can load homepage
        Given the credentials
        When you login to CSW
        Then wait "2" seconds
        Then we have a session cookie