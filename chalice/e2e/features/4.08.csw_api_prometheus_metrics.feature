# Cloud Security Watch - API /prometheus/metrics
# Check that a status=ok response is returned and the mime type of the response
Feature: Cloud Security Watch - API /prometheus/metrics
    Scenario: can load api/prometheus/metrics endpoint
        When you make an unauthenticated http get request to "api/prometheus/metrics"
        Then response code is "200"
        Then response mime type is "text/plain"
