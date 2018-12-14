"""
implements aws::elb::listener_security
checkId: a2sEc6ILx
Checks on the Elastic Load Balancer HTTPS/SSL listener's security configuration.
"""
import json

from chalicelib.criteria.criteria_default import CriteriaDefault
from chalicelib.aws.gds_support_client import GdsSupportClient


class ELBListenerSecurity(CriteriaDefault):
    """
    Subclass Criterion checking for the four ELB listener checks
    """
    active = False

    def __init__(self, app):
        # attributes to overwrite in subclasses
        self.status_string = ''
        self.status_interval = ''
        # attributes common in both subclasses
        self.resource_type = 'AWS::elb::listener_security'
        self.ClientClass = GdsSupportClient
        self.check_id = 'a2sEc6ILx'
        self.language = 'en'
        self.region = 'us-east-1'
        self.annotation = ''
        super(ELBListenerSecurity, self).__init__(app)

    def get_data(self, session, **kwargs):
        output = self.client.describe_trusted_advisor_check_result(
            session,
            checkId=self.check_id,
            language=self.language
        )
        self.app.log.debug(json.dumps(output))
        return output['flaggedResources']  # will have len() == 0 if compliant

    def translate(self, data={}):
        return {
            'resource_id': 'root',
            'resource_name': 'Root Account',
        }


class ELBListenerSecurityNoListener(ELBListenerSecurity):
    """
    Subclass Criterion checking for no listener
    """
    active = True

    def __init__(self, app):
        self.title = 'ELB Listener Security'
        self.description = (
            ''
        )
        self.why_is_it_important = (
            ''
        )
        self.how_do_i_fix_it = (
            ''
        )
        super(ELBListenerSecurityNoListener, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        """
        TODO
        """
        compliance_type = 'NON_COMPLIANT'
        self.annotation = (
            ''
        )
        return self.build_evaluation(
            item['resourceId'],
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )


class ELBListenerSecurityPredefinedOutdated(ELBListenerSecurity):
    """
    Subclass Criterion checking for outdated predefined policy
    """
    active = True

    def __init__(self, app):
        self.title = 'ELB Listener Security'
        self.description = (
            ''
        )
        self.why_is_it_important = (
            ''
        )
        self.how_do_i_fix_it = (
            ''
        )
        super(ELBListenerSecurityPredefinedOutdated, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        """
        TODO
        """
        compliance_type = 'NON_COMPLIANT'
        self.annotation = (
            ''
        )
        return self.build_evaluation(
            item['resourceId'],
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )


class ELBListenerSecurityProtocolDiscouraged(ELBListenerSecurity):
    """
    Subclass Criterion checking for not recomended protocol or cipher
    """
    active = True

    def __init__(self, app):
        self.title = 'ELB Listener Security'
        self.description = (
            ''
        )
        self.why_is_it_important = (
            ''
        )
        self.how_do_i_fix_it = (
            ''
        )
        super(ELBListenerSecurityProtocolDiscouraged, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        """
        TODO
        """
        compliance_type = 'NON_COMPLIANT'
        self.annotation = (
            ''
        )
        return self.build_evaluation(
            item['resourceId'],
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )


class ELBListenerSecurityInsecureProtocol(ELBListenerSecurity):
    """
    Subclass Criterion checking for not insecure protocol or cipher
    """
    active = True

    def __init__(self, app):
        self.title = 'ELB Listener Security'
        self.description = (
            ''
        )
        self.why_is_it_important = (
            ''
        )
        self.how_do_i_fix_it = (
            ''
        )
        super(ELBListenerSecurityInsecureProtocol, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        """
        TODO
        """
        compliance_type = 'NON_COMPLIANT'
        self.annotation = (
            ''
        )
        return self.build_evaluation(
            item['resourceId'],
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )
