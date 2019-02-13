# Google Feature
Feature: Google Search Functionality
    Scenario: can find search results
        When visit url "http://www.google.com"
        Then header equals "Cloud Security Watch"
