import datetime
from dateutil.tz import tzlocal

EMPTY_SUMMARY = {
    'all': {
        'display_stat': 0,
        'category': 'all',
        'modifier_class': 'tested'
    },
    'applicable': {
        'display_stat': 0,
        'category': 'tested',
        'modifier_class': 'precheck'
    },
    'non_compliant': {
        'display_stat': 0,
        'category': 'failed',
        'modifier_class': 'failed'
    },
    'compliant': {
        'display_stat': 0,
        'category': 'passed',
        'modifier_class': 'passed'
    },
    'not_applicable': {
        'display_stat': 0,
        'category': 'ignored',
        'modifier_class': 'passed'
    },
    'regions': {
        'list': [],
        'count': 0
    }
}

CLOUDTRAIL_LOGGING_ITEMS = {
    'green': {
        'describe_trusted_advisor_check_result': {
            'ResponseMetadata': {
                'HTTPHeaders': {
                    'content-length': '3222',
                    'content-type': 'application/x-amz-json-1.1',
                    'date': 'Mon, 22 Oct 2018 13:59:24 GMT',
                    'x-amzn-requestid': 'af21b314-d602-11e8-b244-47eb8754bb40'
                },
                'HTTPStatusCode': 200,
                'RequestId': 'af21b314-d602-11e8-b244-47eb8754bb40',
                'RetryAttempts': 0
            },
            'result': {
                'categorySpecificSummary': {
                    'costOptimizing': {
                        'estimatedMonthlySavings': 0.0,
                        'estimatedPercentMonthlySavings': 0.0
                    }
                },
                'checkId': 'vjafUGJ9H0',
                'flaggedResources': [
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'us-east-2',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Green'
                        ],
                        'resourceId':
                            'VvC9ovd75N6104DTSYmObUVpXQQnHHtnHpN-iMxQbzo',
                        'status': 'ok'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'ca-central-1',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Green'
                        ],
                        'resourceId':
                            '_TKegn3HXXRwN3k9h1bGriclTrIVcBeAi_shbp-aU4A',
                        'status': 'ok'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'us-east-1',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Green'
                        ],
                        'resourceId':
                            'LGbPMx_BciQXdx9_gybBw4uJ0dSDP0w9_cj3CkpslG0',
                        'status': 'ok'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'us-west-1',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Green'
                        ],
                        'resourceId':
                            'yEauwulys9ZPV1ILSDjAkSgEL0QPuGKCzUDPvL-OtIA',
                        'status': 'ok'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'eu-west-3',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Green'
                        ],
                        'resourceId':
                            'qZ2O-WN6IB_1BWfs3AA0hgv30ZwNO3G_EHU-4dNLnl4',
                        'status': 'ok'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'eu-west-2',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Green'
                        ],
                        'resourceId':
                            'bn8DoncTHe33YFs8MwhGozEIJf57CLOKp3Na54rUbA0',
                        'status': 'ok'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'us-west-2',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Green'
                        ],
                        'resourceId':
                            'RDgxMLH58eesm1IKJxCwaJYMUnA2tq1KMkKRtuIx9gk',
                        'status': 'ok'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'eu-west-1',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Green'
                        ],
                        'resourceId':
                            '65ovE2uTkT1aCs2EazyT7Iq6r_OdfikxUWv6Mw5RK5o',
                        'status': 'ok'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'eu-central-1',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Green'
                        ],
                        'resourceId':
                            '0XLtiwkvb-L0NEMnlP5iAR-kKm74ei5FN2cw9PhRoqU',
                        'status': 'ok'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'sa-east-1',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Green'
                        ],
                        'resourceId':
                            's9ODasM-gWNDl2HdPYFPsb84cIRVZWtdnUE7_aX17GQ',
                        'status': 'ok'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'ap-northeast-1',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Green'
                        ],
                        'resourceId':
                            'IdvMsTEOxBREZIPEVHS7HQknsBzcwfwM0_fG4NQe0jM',
                        'status': 'ok'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'ap-south-1',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Green'
                        ],
                        'resourceId':
                            '200R2Z-zGcNO4QI0hOoVTvhVbv_D1f4Fl_Q6LIQFcbk',
                        'status': 'ok'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'ap-northeast-2',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Green'
                        ],
                        'resourceId':
                            'NY0Fv5zllfREOdu_-F2kJJiEE7glPVvCDNrf7NZmzHA',
                        'status': 'ok'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'ap-southeast-2',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Green'
                        ],
                        'resourceId':
                            '8NjMM8JQ-ZQKGVNXxuAY9iPjFXhshvfAq1SslDKBsww',
                        'status': 'ok'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'ap-southeast-1',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Green'
                        ],
                        'resourceId':
                            'VcSDwjxhLJ0wAew9_OrrGOjKzm3NYUI-DM5DCYHUmrg',
                        'status': 'ok'
                    }
                ],
                'resourcesSummary': {
                    'resourcesFlagged': 0,
                    'resourcesIgnored': 0,
                    'resourcesProcessed': 15,
                    'resourcesSuppressed': 0
                },
                'status': 'ok',
                'timestamp': '2018-10-22T13:37:41Z'
            }
        },
        'describe_trails': None,  # doesn't matter
        'get_trail_status': None,  # doesn't matter
    },
    'yellow': {
        'describe_trusted_advisor_check_result': {
            'ResponseMetadata': {
                'HTTPHeaders': {
                    'content-length': '3485',
                    'content-type': 'application/x-amz-json-1.1',
                    'date': 'Mon, 22 Oct 2018 15:30:02 GMT',
                    'x-amzn-requestid': '5833e6ba-d60f-11e8-9bd8-95380a6b36d9'
                },
                'HTTPStatusCode': 200,
                'RequestId': '5833e6ba-d60f-11e8-9bd8-95380a6b36d9',
                'RetryAttempts': 0
            },
            'result': {
                'categorySpecificSummary': {
                    'costOptimizing': {
                        'estimatedMonthlySavings': 0.0,
                        'estimatedPercentMonthlySavings': 0.0
                    }
                },
                'checkId': 'vjafUGJ9H0',
                'flaggedResources': [
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'us-east-1',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            'NoSuchBucket',
                            'Yellow'
                        ],
                        'resourceId':
                            'LGbPMx_BciQXdx9_gybBw4uJ0dSDP0w9_cj3CkpslG0',
                        'status': 'warning'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'us-east-2',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Green'
                        ],
                        'resourceId':
                            'VvC9ovd75N6104DTSYmObUVpXQQnHHtnHpN-iMxQbzo',
                        'status': 'ok'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'ca-central-1',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Green'
                        ],
                        'resourceId':
                            '_TKegn3HXXRwN3k9h1bGriclTrIVcBeAi_shbp-aU4A',
                        'status': 'ok'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'us-west-1',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Green'
                        ],
                        'resourceId':
                            'yEauwulys9ZPV1ILSDjAkSgEL0QPuGKCzUDPvL-OtIA',
                        'status': 'ok'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'eu-west-1',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            'Internal Server Error',
                            'Yellow'
                        ],
                        'resourceId':
                            '65ovE2uTkT1aCs2EazyT7Iq6r_OdfikxUWv6Mw5RK5o',
                        'status': 'warning'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'eu-west-2',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            'NoSuchBucket',
                            'Yellow'
                        ],
                        'resourceId':
                            'bn8DoncTHe33YFs8MwhGozEIJf57CLOKp3Na54rUbA0',
                        'status': 'warning'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'eu-west-3',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            'Internal Server Error',
                            'Yellow'
                        ],
                        'resourceId':
                            'qZ2O-WN6IB_1BWfs3AA0hgv30ZwNO3G_EHU-4dNLnl4',
                        'status': 'warning'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'us-west-2',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            'Internal Server Error',
                            'Yellow'
                        ],
                        'resourceId':
                            'RDgxMLH58eesm1IKJxCwaJYMUnA2tq1KMkKRtuIx9gk',
                        'status': 'warning'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'eu-central-1',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Green'
                        ],
                        'resourceId':
                            '0XLtiwkvb-L0NEMnlP5iAR-kKm74ei5FN2cw9PhRoqU',
                        'status': 'ok'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'sa-east-1',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            'Internal Server Error',
                            'Yellow'
                        ],
                        'resourceId':
                            's9ODasM-gWNDl2HdPYFPsb84cIRVZWtdnUE7_aX17GQ',
                        'status': 'warning'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'ap-northeast-1',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            'Internal Server Error',
                            'Yellow'
                        ],
                        'resourceId':
                            'IdvMsTEOxBREZIPEVHS7HQknsBzcwfwM0_fG4NQe0jM',
                        'status': 'warning'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'ap-south-1',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            'Internal Server Error',
                            'Yellow'
                        ],
                        'resourceId':
                            '200R2Z-zGcNO4QI0hOoVTvhVbv_D1f4Fl_Q6LIQFcbk',
                        'status': 'warning'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'ap-southeast-2',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            'Internal Server Error',
                            'Yellow'
                        ],
                        'resourceId':
                            '8NjMM8JQ-ZQKGVNXxuAY9iPjFXhshvfAq1SslDKBsww',
                        'status': 'warning'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'ap-southeast-1',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            'Internal Server Error',
                            'Yellow'
                        ],
                        'resourceId':
                            'VcSDwjxhLJ0wAew9_OrrGOjKzm3NYUI-DM5DCYHUmrg',
                        'status': 'warning'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'ap-northeast-2',
                            'CSW_Trail',
                            'On',
                            'cyber-security-staging-csw-cloudtrail',
                            'Internal Server Error',
                            'Yellow'
                        ],
                        'resourceId':
                            'NY0Fv5zllfREOdu_-F2kJJiEE7glPVvCDNrf7NZmzHA',
                        'status': 'warning'
                    }
                ],
                'resourcesSummary': {
                    'resourcesFlagged': 11,
                    'resourcesIgnored': 0,
                    'resourcesProcessed': 15,
                    'resourcesSuppressed': 0
                },
                'status': 'warning',
                'timestamp': '2018-10-22T15:29:15Z'
            }
        },
        'describe_trails': {
            'ResponseMetadata': {
                'HTTPHeaders': {
                    'content-length': '311',
                    'content-type': 'application/x-amz-json-1.1',
                    'date': 'Mon, 22 Oct 2018 15:30:02 GMT',
                    'x-amzn-requestid': '86518912-5824-4f8d-b0c9-d99fd157b47d'
                },
                'HTTPStatusCode': 200,
                'RequestId': '86518912-5824-4f8d-b0c9-d99fd157b47d',
                'RetryAttempts': 0
            },
            'trailList': [
                {
                    'HasCustomEventSelectors': False,
                    'HomeRegion': 'eu-west-2',
                    'IncludeGlobalServiceEvents': True,
                    'IsMultiRegionTrail': True,
                    'LogFileValidationEnabled': True,
                    'Name': 'CSW_Trail',
                    'S3BucketName': 'cyber-security-staging-csw-cloudtrail',
                    'TrailARN':
                        'arn:aws:cloudtrail:eu-west-2:'
                        '103495720024:trail/CSW_Trail'
                }
            ]
        },
        'get_trail_status': {
            'IsLogging': True,
            'LatestDeliveryAttemptSucceeded': '2018-10-22T15:25:15Z',
            'LatestDeliveryAttemptTime': '2018-10-22T15:28:30Z',
            'LatestDeliveryError': 'NoSuchBucket',
            'LatestDeliveryTime': datetime.datetime(
                2018, 10, 22, 16, 25, 15, 818000, tzinfo=tzlocal()
            ),
            'LatestDigestDeliveryTime': datetime.datetime(
                2018, 10, 22, 15, 14, 46, 4000, tzinfo=tzlocal()
            ),
            'LatestNotificationAttemptSucceeded': '',
            'LatestNotificationAttemptTime': '',
            'ResponseMetadata': {
                'HTTPHeaders': {
                    'content-length': '478',
                    'content-type': 'application/x-amz-json-1.1',
                    'date': 'Mon, 22 Oct 2018 15:30:02 GMT',
                    'x-amzn-requestid': '3fb47b60-c004-452a-95f2-248e92dd0fe5'
                },
                'HTTPStatusCode': 200,
                'RequestId': '3fb47b60-c004-452a-95f2-248e92dd0fe5',
                'RetryAttempts': 0
            },
            'StartLoggingTime': datetime.datetime(
                2018, 10, 22, 16, 24, 26, 353000, tzinfo=tzlocal()
            ),
            'StopLoggingTime': datetime.datetime(
                2018, 10, 22, 15, 6, 5, 949000, tzinfo=tzlocal()
            ),
            'TimeLoggingStarted': '2018-10-22T15:24:26Z',
            'TimeLoggingStopped': '2018-10-22T14:06:05Z'
        },
    },
    'red': {
        'describe_trusted_advisor_check_result': {
            'ResponseMetadata': {
                'HTTPHeaders': {
                    'content-length': '3256',
                    'content-type': 'application/x-amz-json-1.1',
                    'date': 'Mon, 22 Oct 2018 15:04:09 GMT',
                    'x-amzn-requestid': 'ba655ef0-d60b-11e8-9c7b-179361cbf5ed'
                },
                'HTTPStatusCode': 200,
                'RequestId': 'ba655ef0-d60b-11e8-9c7b-179361cbf5ed',
                'RetryAttempts': 0
            },
            'result': {
                'categorySpecificSummary': {
                    'costOptimizing': {
                        'estimatedMonthlySavings': 0.0,
                        'estimatedPercentMonthlySavings': 0.0
                    }
                },
                'checkId': 'vjafUGJ9H0',
                'flaggedResources': [
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'us-east-1',
                            'CSW_Trail',
                            'Off',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Red'
                        ],
                        'resourceId':
                            'LGbPMx_BciQXdx9_gybBw4uJ0dSDP0w9_cj3CkpslG0',
                        'status': 'error'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'us-east-2',
                            'CSW_Trail',
                            'Off',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Red'
                        ],
                        'resourceId':
                            'VvC9ovd75N6104DTSYmObUVpXQQnHHtnHpN-iMxQbzo',
                        'status': 'error'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'ca-central-1',
                            'CSW_Trail',
                            'Off',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Red'
                        ],
                        'resourceId':
                            '_TKegn3HXXRwN3k9h1bGriclTrIVcBeAi_shbp-aU4A',
                        'status': 'error'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'us-west-1',
                            'CSW_Trail',
                            'Off',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Red'
                        ],
                        'resourceId':
                            'yEauwulys9ZPV1ILSDjAkSgEL0QPuGKCzUDPvL-OtIA',
                        'status': 'error'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'eu-west-1',
                            'CSW_Trail',
                            'Off',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Red'
                        ],
                        'resourceId':
                            '65ovE2uTkT1aCs2EazyT7Iq6r_OdfikxUWv6Mw5RK5o',
                        'status': 'error'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'eu-west-2',
                            'CSW_Trail',
                            'Off',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Red'
                        ],
                        'resourceId':
                            'bn8DoncTHe33YFs8MwhGozEIJf57CLOKp3Na54rUbA0',
                        'status': 'error'},
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'eu-west-3',
                            'CSW_Trail',
                            'Off',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Red'
                        ],
                        'resourceId':
                            'qZ2O-WN6IB_1BWfs3AA0hgv30ZwNO3G_EHU-4dNLnl4',
                        'status': 'error'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'us-west-2',
                            'CSW_Trail',
                            'Off',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Red'
                        ],
                        'resourceId':
                            'RDgxMLH58eesm1IKJxCwaJYMUnA2tq1KMkKRtuIx9gk',
                        'status': 'error'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'eu-central-1',
                            'CSW_Trail',
                            'Off',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Red'
                        ],
                        'resourceId':
                            '0XLtiwkvb-L0NEMnlP5iAR-kKm74ei5FN2cw9PhRoqU',
                        'status': 'error'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'sa-east-1',
                            'CSW_Trail',
                            'Off',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Red'
                        ],
                        'resourceId':
                            's9ODasM-gWNDl2HdPYFPsb84cIRVZWtdnUE7_aX17GQ',
                        'status': 'error'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'ap-northeast-1',
                            'CSW_Trail',
                            'Off',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Red'
                        ],
                        'resourceId':
                            'IdvMsTEOxBREZIPEVHS7HQknsBzcwfwM0_fG4NQe0jM',
                        'status': 'error'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'ap-south-1',
                            'CSW_Trail',
                            'Off',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Red'
                        ],
                        'resourceId':
                            '200R2Z-zGcNO4QI0hOoVTvhVbv_D1f4Fl_Q6LIQFcbk',
                        'status': 'error'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'ap-northeast-2',
                            'CSW_Trail',
                            'Off',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Red'
                        ],
                        'resourceId':
                            'NY0Fv5zllfREOdu_-F2kJJiEE7glPVvCDNrf7NZmzHA',
                        'status': 'error'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'ap-southeast-2',
                            'CSW_Trail',
                            'Off',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Red'
                        ],
                        'resourceId':
                            '8NjMM8JQ-ZQKGVNXxuAY9iPjFXhshvfAq1SslDKBsww',
                        'status': 'error'
                    },
                    {
                        'isSuppressed': False,
                        'metadata': [
                            'ap-southeast-1',
                            'CSW_Trail',
                            'Off',
                            'cyber-security-staging-csw-cloudtrail',
                            None,
                            'Red'
                        ],
                        'resourceId':
                            'VcSDwjxhLJ0wAew9_OrrGOjKzm3NYUI-DM5DCYHUmrg',
                        'status': 'error'
                    }
                ],
                'resourcesSummary': {
                    'resourcesFlagged': 15,
                    'resourcesIgnored': 0,
                    'resourcesProcessed': 15,
                    'resourcesSuppressed': 0
                },
                'status': 'error',
                'timestamp': '2018-10-22T14:06:38Z'
            }
        },
        'describe_trails': {
            'ResponseMetadata': {
                'HTTPHeaders': {
                    'content-length': '311',
                    'content-type': 'application/x-amz-json-1.1',
                    'date': 'Mon, 22 Oct 2018 15:04:09 GMT',
                    'x-amzn-requestid': '911b4f66-c6bc-46e6-b6ac-217e2576c8cf'
                },
                'HTTPStatusCode': 200,
                'RequestId': '911b4f66-c6bc-46e6-b6ac-217e2576c8cf',
                'RetryAttempts': 0
            },
            'trailList': [
                {
                    'HasCustomEventSelectors': False,
                    'HomeRegion': 'eu-west-2',
                    'IncludeGlobalServiceEvents': True,
                    'IsMultiRegionTrail': True,
                    'LogFileValidationEnabled': True,
                    'Name': 'CSW_Trail',
                    'S3BucketName': 'cyber-security-staging-csw-cloudtrail',
                    'TrailARN':
                        'arn:aws:cloudtrail:eu-west-2:'
                        '103495720024:trail/CSW_Trail'
                }
            ]
        },
        'get_trail_status': {
            'IsLogging': False,
            'LatestDeliveryAttemptSucceeded': '2018-10-22T14:18:20Z',
            'LatestDeliveryAttemptTime': '2018-10-22T14:18:20Z',
            'LatestDeliveryTime': datetime.datetime(
                2018, 10, 22, 15, 18, 20, 359000, tzinfo=tzlocal()
            ),
            'LatestDigestDeliveryTime': datetime.datetime(
                2018, 10, 22, 15, 14, 46, 4000, tzinfo=tzlocal()
            ),
            'LatestNotificationAttemptSucceeded': '',
            'LatestNotificationAttemptTime': '',
            'ResponseMetadata': {
                'HTTPHeaders': {
                    'content-length': '442',
                    'content-type': 'application/x-amz-json-1.1',
                    'date': 'Mon, 22 Oct 2018 15:04:09 GMT',
                    'x-amzn-requestid': 'f2547ec3-bd9e-44cd-99a4-6471c8bdd62b'
                },
                'HTTPStatusCode': 200,
                'RequestId': 'f2547ec3-bd9e-44cd-99a4-6471c8bdd62b',
                'RetryAttempts': 0
            },
            'StartLoggingTime': datetime.datetime(
                2018, 10, 22, 14, 12, 37, 395000, tzinfo=tzlocal()
            ),
            'StopLoggingTime': datetime.datetime(
                2018, 10, 22, 15, 6, 5, 949000, tzinfo=tzlocal()
            ),
            'TimeLoggingStarted': '2018-10-22T13:12:37Z',
            'TimeLoggingStopped': '2018-10-22T14:06:05Z'
        },
    },
}
