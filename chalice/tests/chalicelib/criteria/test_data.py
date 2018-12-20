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
    'very_red': {
        'describe_trusted_advisor_check_result': {



            'ResponseMetadata': {'HTTPHeaders': {'content-length': '2746',
                                                'content-type': 'application/x-amz-json-1.1',
                                                'date': 'Tue, 30 Oct 2018 15:43:50 GMT',
                                                'x-amzn-actiontrace': 'amzn1.tr.991be714-dc5a-11e8-8210-0a59a5bc0000.0..H@fyEL',
                                                'x-amzn-requestid': '991be6c7-dc5a-11e8-b778-f7d75fa3c65a'},
                                'HTTPStatusCode': 200,
                                'RequestId': '991be6c7-dc5a-11e8-b778-f7d75fa3c65a',
                                'RetryAttempts': 0},
            'result': {'categorySpecificSummary': {'costOptimizing': {'estimatedMonthlySavings': 0.0,
                                                                    'estimatedPercentMonthlySavings': 0.0}},
                        'checkId': 'vjafUGJ9H0',
                        'flaggedResources': [{'isSuppressed': False,
                                            'metadata': ['us-east-1',
                                                        None,
                                                        'Not enabled',
                                                        None,
                                                        None,
                                                        'Red'],
                                            'resourceId': 'mm_LXRRe1e53nMYeXfdPqoQrbITgzwAdoWYgfmrBDU4',
                                            'status': 'error'},
                                            {'isSuppressed': False,
                                            'metadata': ['us-east-2',
                                                        None,
                                                        'Not enabled',
                                                        None,
                                                        None,
                                                        'Red'],
                                            'resourceId': 'SNOEuKl2yypyCw56gLwDNnA_jNOU0dOgcUu1sHtcq-c',
                                            'status': 'error'},
                                            {'isSuppressed': False,
                                            'metadata': ['ca-central-1',
                                                        None,
                                                        'Not enabled',
                                                        None,
                                                        None,
                                                        'Red'],
                                            'resourceId': 'imxE5YNLzffilGTwrCYD8qNnaQIFnvCSmlHtgT4uZMk',
                                            'status': 'error'},
                                            {'isSuppressed': False,
                                            'metadata': ['us-west-1',
                                                        None,
                                                        'Not enabled',
                                                        None,
                                                        None,
                                                        'Red'],
                                            'resourceId': 'QOchtKcqfakxcfcC5VgWVfWDb-bXfyjmG1bBJS8-6tY',
                                            'status': 'error'},
                                            {'isSuppressed': False,
                                            'metadata': ['eu-west-1',
                                                        None,
                                                        'Not enabled',
                                                        None,
                                                        None,
                                                        'Red'],
                                            'resourceId': 'RB5NorEvo5GHF-upFuCJaaGuyoVoZjI3yRAfXQSfXzE',
                                            'status': 'error'},
                                            {'isSuppressed': False,
                                            'metadata': ['eu-west-2',
                                                        None,
                                                        'Not enabled',
                                                        None,
                                                        None,
                                                        'Red'],
                                            'resourceId': '46ggFsEuZ5uRdhSm_xUa-R1kud1f1TGP8yDwdI3nPd4',
                                            'status': 'error'},
                                            {'isSuppressed': False,
                                            'metadata': ['eu-west-3',
                                                        None,
                                                        'Not enabled',
                                                        None,
                                                        None,
                                                        'Red'],
                                            'resourceId': 'YOdTSMJpNgp1Wgkemh9JmABoM25T4zo3fwmGP8xLwZ8',
                                            'status': 'error'},
                                            {'isSuppressed': False,
                                            'metadata': ['eu-central-1',
                                                        None,
                                                        'Not enabled',
                                                        None,
                                                        None,
                                                        'Red'],
                                            'resourceId': 'pHmR-GVCnOMCSJbi08JnHjUFdTEzo9zyDJfhDtnpimA',
                                            'status': 'error'},
                                            {'isSuppressed': False,
                                            'metadata': ['us-west-2',
                                                        None,
                                                        'Not enabled',
                                                        None,
                                                        None,
                                                        'Red'],
                                            'resourceId': '9i5oyuaDhlQ4Ch6DcnSeijNF6nBZ5AvshfaMkkT8yJk',
                                            'status': 'error'},
                                            {'isSuppressed': False,
                                            'metadata': ['sa-east-1',
                                                        None,
                                                        'Not enabled',
                                                        None,
                                                        None,
                                                        'Red'],
                                            'resourceId': 'Q1Qk2TemcP51hmTnzAKIMifAFkN86a6DbvDWS8EpqSQ',
                                            'status': 'error'},
                                            {'isSuppressed': False,
                                            'metadata': ['ap-northeast-1',
                                                        None,
                                                        'Not enabled',
                                                        None,
                                                        None,
                                                        'Red'],
                                            'resourceId': '_fg6Xb3obq1jjwSL53tMyrdObB_Q5ubG7CoFX-UmjYw',
                                            'status': 'error'},
                                            {'isSuppressed': False,
                                            'metadata': ['ap-south-1',
                                                        None,
                                                        'Not enabled',
                                                        None,
                                                        None,
                                                        'Red'],
                                            'resourceId': 'r6wXeHWOhkGBtkjqV8qYgYTchmhFt_FrkQKEVhaTo90',
                                            'status': 'error'},
                                            {'isSuppressed': False,
                                            'metadata': ['ap-northeast-2',
                                                        None,
                                                        'Not enabled',
                                                        None,
                                                        None,
                                                        'Red'],
                                            'resourceId': 'c6Wpo4HjyouDxkA5_7uw3A17FBbZllxIIAKKJAVuOBA',
                                            'status': 'error'},
                                            {'isSuppressed': False,
                                            'metadata': ['ap-southeast-2',
                                                        None,
                                                        'Not enabled',
                                                        None,
                                                        None,
                                                        'Red'],
                                            'resourceId': '-jaQgki6oCn_-E04GeFSp-APXgdffs8rVclosDlQwIY',
                                            'status': 'error'},
                                            {'isSuppressed': False,
                                            'metadata': ['ap-southeast-1',
                                                        None,
                                                        'Not enabled',
                                                        None,
                                                        None,
                                                        'Red'],
                                            'resourceId': 'kJBKTEwFm-85Z1qht71me2YXh2zdtAKOO7B7u9bGt50',
                                            'status': 'error'}],
                        'resourcesSummary': {'resourcesFlagged': 15,
                                            'resourcesIgnored': 0,
                                            'resourcesProcessed': 15,
                                            'resourcesSuppressed': 0},
                        'status': 'error',
                        'timestamp': '2018-10-30T15:42:36Z'}



        },
        'describe_trails': {
            'ResponseMetadata': {
                'HTTPHeaders': {
                    'content-length': '16',
                    'content-type': 'application/x-amz-json-1.1',
                    'date': 'Tue, 30 Oct 2018 15:43:51 GMT',
                    'x-amzn-requestid': '3647565b-b98d-454d-aec4-b1ff3db77f3f'
                },
                'HTTPStatusCode': 200,
                'RequestId': '3647565b-b98d-454d-aec4-b1ff3db77f3f',
                'RetryAttempts': 0
            },
            'trailList': []
        },
        'get_trail_status': None,  # doesn't matter
    },
}

IAM_KEY_ROTATION_ITEMS = {
    'green': {
        'ResponseMetadata': {
            'HTTPHeaders': {
                'content-length': '689',
                'content-type': 'application/x-amz-json-1.1',
                'date': 'Fri, 26 Oct 2018 11:32:27 GMT',
                'x-amzn-requestid': 'd1d0a2c8-d912-11e8-a086-d93a9fdaa2c8'
            },
            'HTTPStatusCode': 200,
            'RequestId': 'd1d0a2c8-d912-11e8-a086-d93a9fdaa2c8',
            'RetryAttempts': 0
        },
        'result': {
            'categorySpecificSummary': {
                'costOptimizing': {
                    'estimatedMonthlySavings': 0.0,
                    'estimatedPercentMonthlySavings': 0.0
                }
            },
            'checkId': 'DqdJqYeRm5',
            'flaggedResources': [
                {
                    'isSuppressed': False,
                    'metadata': [
                        'Green',
                        'tester',
                        'Access Key 1',
                        '2018-10-26T09:50:56.000Z',
                        '< 90 days'
                    ],
                    'resourceId':
                        'bUdRaf51cqo8zLA1zvADO3kU48Rw6RPYtXllVn4da6k',
                    'status': 'ok'
                },
                {
                    'isSuppressed': False,
                    'metadata': [
                        'Green',
                        'tester',
                        'Access Key 2',
                        '2018-10-12T11:47:55.000Z',
                        '< 90 days'
                    ],
                    'resourceId':
                        'L0kTMFl0_9sppZLOP7wgMSgvywOjeuMBWtorW5HQx_o',
                    'status': 'ok'
                }
            ],
            'resourcesSummary': {
                'resourcesFlagged': 0,
                'resourcesIgnored': 0,
                'resourcesProcessed': 2,
                'resourcesSuppressed': 0
            },
            'status': 'ok',
            'timestamp': '2018-10-26T11:31:33Z'
        }
    },
    'yellow': {
        'ResponseMetadata': {
            'HTTPHeaders': {
                'content-length': '689',
                'content-type': 'application/x-amz-json-1.1',
                'date': 'Fri, 26 Oct 2018 11:32:27 GMT',
                'x-amzn-requestid': 'd1d0a2c8-d912-11e8-a086-d93a9fdaa2c8'
            },
            'HTTPStatusCode': 200,
            'RequestId': 'd1d0a2c8-d912-11e8-a086-d93a9fdaa2c8',
            'RetryAttempts': 0
        },
        'result': {
            'categorySpecificSummary': {
                'costOptimizing': {
                    'estimatedMonthlySavings': 0.0,
                    'estimatedPercentMonthlySavings': 0.0
                }
            },
            'checkId': 'DqdJqYeRm5',
            'flaggedResources': [
                {
                    'isSuppressed': False,
                    'metadata': [
                        'Green',
                        'tester',
                        'Access Key 1',
                        '2018-10-26T09:50:56.000Z',
                        '< 90 days'
                    ],
                    'resourceId':
                        'bUdRaf51cqo8zLA1zvADO3kU48Rw6RPYtXllVn4da6k',
                    'status': 'ok'
                },
                {
                    'isSuppressed': False,
                    'metadata': [
                        'Yellow',
                        'tester',
                        'Access Key 2',
                        '2018-10-12T11:47:55.000Z',
                        '> 90 days'
                    ],
                    'resourceId':
                        'L0kTMFl0_9sppZLOP7wgMSgvywOjeuMBWtorW5HQx_o',
                    'status': 'warning'
                }
            ],
            'resourcesSummary': {
                'resourcesFlagged': 0,
                'resourcesIgnored': 0,
                'resourcesProcessed': 2,
                'resourcesSuppressed': 0
            },
            'status': 'warning',
            'timestamp': '2018-10-26T11:31:33Z'
        }
    },
    'red': {
        'ResponseMetadata': {
            'HTTPHeaders': {
                'content-length': '689',
                'content-type': 'application/x-amz-json-1.1',
                'date': 'Fri, 26 Oct 2018 11:32:27 GMT',
                'x-amzn-requestid': 'd1d0a2c8-d912-11e8-a086-d93a9fdaa2c8'
            },
            'HTTPStatusCode': 200,
            'RequestId': 'd1d0a2c8-d912-11e8-a086-d93a9fdaa2c8',
            'RetryAttempts': 0
        },
        'result': {
            'categorySpecificSummary': {
                'costOptimizing': {
                    'estimatedMonthlySavings': 0.0,
                    'estimatedPercentMonthlySavings': 0.0
                }
            },
            'checkId': 'DqdJqYeRm5',
            'flaggedResources': [
                {
                    'isSuppressed': False,
                    'metadata': [
                        'Green',
                        'tester',
                        'Access Key 1',
                        '2018-10-26T09:50:56.000Z',
                        '< 90 days'
                    ],
                    'resourceId':
                        'bUdRaf51cqo8zLA1zvADO3kU48Rw6RPYtXllVn4da6k',
                    'status': 'ok'
                },
                {
                    'isSuppressed': False,
                    'metadata': [
                        'Red',
                        'tester',
                        'Access Key 2',
                        '2018-10-12T11:47:55.000Z',
                        '> 2 years'
                    ],
                    'resourceId':
                        'L0kTMFl0_9sppZLOP7wgMSgvywOjeuMBWtorW5HQx_o',
                    'status': 'error'
                }
            ],
            'resourcesSummary': {
                'resourcesFlagged': 0,
                'resourcesIgnored': 0,
                'resourcesProcessed': 2,
                'resourcesSuppressed': 0
            },
            'status': 'error',
            'timestamp': '2018-10-26T11:31:33Z'
        }
    },
}

IAM_KEY_EXPOSED_ITEMS = {
    'green': {
        'ResponseMetadata': {'HTTPHeaders': {'content-length': '675',
                                      'content-type': 'application/x-amz-json-1.1',
                                      'date': 'Fri, 09 Nov 2018 11:24:52 GMT',
                                      'x-amzn-requestid': '145d6774-e412-11e8-98f4-f39aaca3d0a7'},
                      'HTTPStatusCode': 200,
                      'RequestId': '145d6774-e412-11e8-98f4-f39aaca3d0a7',
                      'RetryAttempts': 0},
        'result': {'categorySpecificSummary': {},
                    'checkId': '12Fnkpl8Y5',
                    'flaggedResources': [],
                    'resourcesSummary': {'resourcesFlagged': 0,
                                        'resourcesIgnored': 0,
                                        'resourcesProcessed': 0,
                                        'resourcesSuppressed': 0},
                    'status': 'ok',
                    'timestamp': '2018-12-05T11:35:42Z'}
    },
    'yellow': {
        'ResponseMetadata': {'HTTPHeaders': {'content-length': '675',
                                      'content-type': 'application/x-amz-json-1.1',
                                      'date': 'Fri, 09 Nov 2018 11:24:52 GMT',
                                      'x-amzn-requestid': '145d6774-e412-11e8-98f4-f39aaca3d0a7'},
                      'HTTPStatusCode': 200,
                      'RequestId': '145d6774-e412-11e8-98f4-f39aaca3d0a7',
                      'RetryAttempts': 0},
        'result': {'categorySpecificSummary': {'costOptimizing': {'estimatedMonthlySavings': 0.0,
                                                                'estimatedPercentMonthlySavings': 0.0}},
                    'checkId': '12Fnkpl8Y5',
                    'flaggedResources': [{'isSuppressed': False,
                                        'metadata': ['AKIAIT3MHLMW6C3JPDAA',
                                                    'Key_leaked',
                                                    'Suspected',
                                                    None,
                                                    '1541762581240',
                                                    'https://github.com/alphagov/cst-test-security-failure-detection/blob/37b8b773cb7dc1941e9affa2be30e105de04f324/Access_Key_leaked_Intentionally',
                                                    '1542194577411',
                                                    '0'],
                                        'resourceId': 'XHiaKLkFPYAEcHt8FYMMOLo2SzoISdr8vFKPPgYzhVc',
                                        'status': 'error'}],
                    'resourcesSummary': {'resourcesFlagged': 1,
                                        'resourcesIgnored': 0,
                                        'resourcesProcessed': 1,
                                        'resourcesSuppressed': 0},
                    'status': 'error',
                    'timestamp': '2018-11-09T11:24:53Z'}},
    'red': {
        'ResponseMetadata': {'HTTPHeaders': {'content-length': '675',
                                      'content-type': 'application/x-amz-json-1.1',
                                      'date': 'Fri, 09 Nov 2018 11:24:52 GMT',
                                      'x-amzn-requestid': '145d6774-e412-11e8-98f4-f39aaca3d0a7'},
                      'HTTPStatusCode': 200,
                      'RequestId': '145d6774-e412-11e8-98f4-f39aaca3d0a7',
                      'RetryAttempts': 0},
        'result': {'categorySpecificSummary': {'costOptimizing': {'estimatedMonthlySavings': 0.0,
                                                                'estimatedPercentMonthlySavings': 0.0}},
                    'checkId': '12Fnkpl8Y5',
                    'flaggedResources': [{'isSuppressed': False,
                                        'metadata': ['AKIAIT3MHLMW6C3JPDAA',
                                                    'Key_leaked',
                                                    'Exposed',
                                                    None,
                                                    '1541762581240',
                                                    'https://github.com/alphagov/cst-test-security-failure-detection/blob/37b8b773cb7dc1941e9affa2be30e105de04f324/Access_Key_leaked_Intentionally',
                                                    '1542194577411',
                                                    '0'],
                                        'resourceId': 'XHiaKLkFPYAEcHt8FYMMOLo2SzoISdr8vFKPPgYzhVc',
                                        'status': 'error'}],
                    'resourcesSummary': {'resourcesFlagged': 1,
                                        'resourcesIgnored': 0,
                                        'resourcesProcessed': 1,
                                        'resourcesSuppressed': 0},
                    'status': 'error',
                    'timestamp': '2018-11-09T11:24:53Z'}},
}

ELB_LISTENER_SECURITY = {  # result dictionaries for each key below
    'no_elb': {'categorySpecificSummary': {},
            'checkId': 'a2sEc6ILx',
            'flaggedResources': [],
            'resourcesSummary': {'resourcesFlagged': 0,
                                 'resourcesIgnored': 0,
                                 'resourcesProcessed': 0,
                                 'resourcesSuppressed': 0},
            'status': 'ok',
            'timestamp': '2018-12-09T11:43:49Z'},
    'all_clear': {'categorySpecificSummary': {'costOptimizing': {'estimatedMonthlySavings': 0.0,
                                                           'estimatedPercentMonthlySavings': 0.0}},
            'checkId': 'a2sEc6ILx',
            'flaggedResources': [{'isSuppressed': False,
                                  'metadata': ['us-west-2',
                                               'cloudgoat-elb',
                                               '443',
                                               'Green',
                                               '-'],
                                  'region': 'us-west-2',
                                  'resourceId': 'LE_xZ-s3Ndiz-Vg5Pn-kiRUGTFKBpZILsZSEYE2Ur9A',
                                  'status': 'ok'}],
            'resourcesSummary': {'resourcesFlagged': 0,
                                 'resourcesIgnored': 0,
                                 'resourcesProcessed': 1,
                                 'resourcesSuppressed': 0},
            'status': 'ok',
            'timestamp': '2018-12-05T16:34:16Z'},
    'no_listener': {'categorySpecificSummary': {'costOptimizing': {'estimatedMonthlySavings': 0.0,
                                                           'estimatedPercentMonthlySavings': 0.0}},
            'checkId': 'a2sEc6ILx',
            'flaggedResources': [{'isSuppressed': False,
                                  'metadata': ['us-west-2',
                                               'cloudgoat-elb',
                                               '-',
                                               'Yellow',
                                               'No listener uses a secure '
                                               'protocol'],
                                  'region': 'us-west-2',
                                  'resourceId': 'LE_xZ-s3Ndiz-Vg5Pn-kiRUGTFKBpZILsZSEYE2Ur9A',
                                  'status': 'warning'}],
            'resourcesSummary': {'resourcesFlagged': 1,
                                 'resourcesIgnored': 0,
                                 'resourcesProcessed': 1,
                                 'resourcesSuppressed': 0},
            'status': 'warning',
            'timestamp': '2018-12-05T11:35:46Z'},
    'predifined_outdated': {'categorySpecificSummary': {'costOptimizing': {'estimatedMonthlySavings': 0.0,
                                                           'estimatedPercentMonthlySavings': 0.0}},
            'checkId': 'a2sEc6ILx',
            'flaggedResources': [{'isSuppressed': False,
                                  'metadata': ['us-west-2',
                                               'cloudgoat-elb',
                                               '443',
                                               'Yellow',
                                               'A listener uses an outdated '
                                               'predefined SSL security '
                                               'policy'],
                                  'region': 'us-west-2',
                                  'resourceId': 'LE_xZ-s3Ndiz-Vg5Pn-kiRUGTFKBpZILsZSEYE2Ur9A',
                                  'status': 'warning'}],
            'resourcesSummary': {'resourcesFlagged': 1,
                                 'resourcesIgnored': 0,
                                 'resourcesProcessed': 1,
                                 'resourcesSuppressed': 0},
            'status': 'warning',
            'timestamp': '2018-12-05T16:39:40Z'},
    'protocol_discouraged': {'categorySpecificSummary': {'costOptimizing': {'estimatedMonthlySavings': 0.0,
                                                           'estimatedPercentMonthlySavings': 0.0}},
            'checkId': 'a2sEc6ILx',
            'flaggedResources': [{'isSuppressed': False,
                                  'metadata': ['us-west-2',
                                               'cloudgoat-elb',
                                               '443',
                                               'Yellow',
                                               'A listener uses a deprecated '
                                               'cipher or protocol'],
                                  'region': 'us-west-2',
                                  'resourceId': 'LE_xZ-s3Ndiz-Vg5Pn-kiRUGTFKBpZILsZSEYE2Ur9A',
                                  'status': 'warning'}],
            'resourcesSummary': {'resourcesFlagged': 1,
                                 'resourcesIgnored': 0,
                                 'resourcesProcessed': 1,
                                 'resourcesSuppressed': 0},
            'status': 'warning',
            'timestamp': '2018-12-05T16:52:32Z'},
    'insecure_protocol': {'categorySpecificSummary': {'costOptimizing': {'estimatedMonthlySavings': 0.0,
                                                           'estimatedPercentMonthlySavings': 0.0}},
            'checkId': 'a2sEc6ILx',
            'flaggedResources': [{'isSuppressed': False,
                                  'metadata': ['us-west-2',
                                               'cloudgoat-elb',
                                               '443',
                                               'Red',
                                               'A listener uses a cipher or '
                                               'protocol that does not follow '
                                               'security best practices'],
                                  'region': 'us-west-2',
                                  'resourceId': 'LE_xZ-s3Ndiz-Vg5Pn-kiRUGTFKBpZILsZSEYE2Ur9A',
                                  'status': 'error'}],
            'resourcesSummary': {'resourcesFlagged': 1,
                                 'resourcesIgnored': 0,
                                 'resourcesProcessed': 1,
                                 'resourcesSuppressed': 0},
            'status': 'error',
            'timestamp': '2018-12-05T17:30:59Z'},
}

S3_BUCKET_PERMISSIONS = {  # result dictionaries for each key below
    # TODO: non_applicable and compliant are exactly the same?
    'non_applicable': {'categorySpecificSummary': {},
            'checkId': 'Pfx0RwqBli',
            'flaggedResources': [],
            'resourcesSummary': {'resourcesFlagged': 0,
                                 'resourcesIgnored': 0,
                                 'resourcesProcessed': 0,
                                 'resourcesSuppressed': 0},
            'status': 'ok',
            'timestamp': '2018-12-18T12:50:43Z'},
    'compliant': {'categorySpecificSummary': {},
            'checkId': 'Pfx0RwqBli',
            'flaggedResources': [],
            'resourcesSummary': {'resourcesFlagged': 0,
                                 'resourcesIgnored': 0,
                                 'resourcesProcessed': 9,
                                 'resourcesSuppressed': 0},
            'status': 'ok',
            'timestamp': '2018-12-18T12:50:43Z'},
    'read_all_fails': {'categorySpecificSummary': {'costOptimizing': {'estimatedMonthlySavings': 0.0,
                                                           'estimatedPercentMonthlySavings': 0.0}},
            'checkId': 'Pfx0RwqBli',
            'flaggedResources': [{'isSuppressed': False,
                                  'metadata': ['eu-west-2',
                                               'eu-west-2',
                                               's3-test-perm-public',
                                               'Yes',
                                               'No',
                                               'Yellow',
                                               'No bucket policy',
                                               None],
                                  'region': 'eu-west-2',
                                  'resourceId': 'akFa8Oue9qENJBdb36OrHAhV2oSlHY2vIaiN8xqzlt4',
                                  'status': 'warning'}],
            'resourcesSummary': {'resourcesFlagged': 1,
                                 'resourcesIgnored': 0,
                                 'resourcesProcessed': 3,
                                 'resourcesSuppressed': 0},
            'status': 'warning',
            'timestamp': '2018-11-07T16:24:29Z'},
    'write_all_fails': {'categorySpecificSummary': {'costOptimizing': {'estimatedMonthlySavings': 0.0,
                                                           'estimatedPercentMonthlySavings': 0.0}},
            'checkId': 'Pfx0RwqBli',
            'flaggedResources': [{'isSuppressed': False,
                                  'metadata': ['eu-west-2',
                                               'eu-west-2',
                                               's3-test-perm-public',
                                               'Yes',
                                               'Yes',
                                               'Red',
                                               'No bucket policy',
                                               None],
                                  'region': 'eu-west-2',
                                  'resourceId': 'akFa8Oue9qENJBdb36OrHAhV2oSlHY2vIaiN8xqzlt4',
                                  'status': 'error'}],
            'resourcesSummary': {'resourcesFlagged': 1,
                                 'resourcesIgnored': 0,
                                 'resourcesProcessed': 3,
                                 'resourcesSuppressed': 0},
            'status': 'error',
            'timestamp': '2018-11-07T16:31:55Z'},
    # TODO: open access for the 1st flagged resource?
    'open_access': {'categorySpecificSummary': {'costOptimizing': {'estimatedMonthlySavings': 0.0,
                                                           'estimatedPercentMonthlySavings': 0.0}},
            'checkId': 'Pfx0RwqBli',
            'flaggedResources': [{'isSuppressed': False,
                                  'metadata': ['us-east-1',
                                               'us-east-1',
                                               'csw-public1',
                                               'No',
                                               'No',
                                               'Yellow',
                                               'Yes',
                                               None],
                                  'region': 'us-east-1',
                                  'resourceId': '1EAf5bDXcZrPuybjLu6ABIv_M5eAutNd-TJzO4nSHGg',
                                  'status': 'warning'},
                                 {'isSuppressed': False,
                                  'metadata': ['us-west-2',
                                               'us-west-2',
                                               '3259010061256201323449972815118619257441690513188165121052',
                                               'Yes',
                                               'No',
                                               'Yellow',
                                               'No bucket policy',
                                               None],
                                  'region': 'us-west-2',
                                  'resourceId': '1dEUebG7EUKOsCTEV2_VMVsbtNGSsZp1PVcl-SBn_VI',
                                  'status': 'warning'},
                                 {'isSuppressed': False,
                                  'metadata': ['us-west-2',
                                               'us-west-2',
                                               '3546608648696891181282835720908295085358201982508128105',
                                               'Yes',
                                               'No',
                                               'Yellow',
                                               'No bucket policy',
                                               None],
                                  'region': 'us-west-2',
                                  'resourceId': '8Wk3xDgIPpZaYOG8y0vhLchaiMTxkHZaSrPCTK0urYg',
                                  'status': 'warning'},
                                 {'isSuppressed': False,
                                  'metadata': ['us-west-2',
                                               'us-west-2',
                                               '96989431201531441216798282632865023614200443217904522454',
                                               'Yes',
                                               'No',
                                               'Yellow',
                                               'No bucket policy',
                                               None],
                                  'region': 'us-west-2',
                                  'resourceId': 'xamV8kez6MT0E-uZbrbSYxMBOye4rSQX187RNidXQSE',
                                  'status': 'warning'}],
            'resourcesSummary': {'resourcesFlagged': 4,
                                 'resourcesIgnored': 0,
                                 'resourcesProcessed': 13,
                                 'resourcesSuppressed': 0},
            'status': 'warning',
            'timestamp': '2018-12-18T14:59:14Z'},
}