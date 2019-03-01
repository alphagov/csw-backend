# Google Feature
Feature: Google Search Functionality
    Scenario: can find search results
        When visit url "http://www.google.com"
        When field with name "q" is given "Cloud Security Watch"
        Then title becomes "Cloud Security Watch - Google Search"
