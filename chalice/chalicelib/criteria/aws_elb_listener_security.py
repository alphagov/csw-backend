"""
implements aws::elb::listener_security
checkId: a2sEc6ILx
Checks on the Elastic Load Balancer HTTPS/SSL listener's security configuration.
"""
from chalicelib.criteria.criteria_default import TrustedAdvisorCriterion


class ELBListenerSecurity(TrustedAdvisorCriterion):
    """
    Subclass Criterion checking for the four ELB listener checks
    """
    def __init__(self, app):
        self.resource_type = 'AWS::elb::listener_security'
        self.check_id = 'a2sEc6ILx'
        super(ELBListenerSecurity, self).__init__(app)


class ELBListenerSecurityNoListener(ELBListenerSecurity):
    """
    Subclass Criterion checking for no listener
    """
    active = True

    def __init__(self, app):
        self.title = 'ELB Listener Security: No listener that uses a secure protocol (HTTPS or SSL).'
        self.description = 'A load balancer does not have any listeners that use a secure protocol (HTTPS, SSL, etc)'
        self.why_is_it_important = (
            'If the listeners do not use a secure protocol, '
            'the requests between your clients and the load balancer are unencrypted and less secure.'
        )
        self.how_do_i_fix_it = (
            'Either add an HTTPS listener with an up-to-date security policy to the ELB, '
            'or edit an existing one to use HTTPS. Further instructions and information can be found here: '
            'https://docs.aws.amazon.com/elasticloadbalancing/latest/application/create-https-listener.html'
        )
        super(ELBListenerSecurityNoListener, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        """
        TODO
        """
        compliance_type = 'NON_COMPLIANT'
        if item["metadata"][4] == 'No listener uses a secure protocol':
            self.annotation = (
                f'"{item["metadata"][1]}" load balancer in region "{item["metadata"][0]}" with resource ID: '
                f'"{item["resourceId"]}" has no listener that uses a secure protocol (HTTPS or SSL).'
            )
        else:
            compliance_type = 'COMPLIANT'
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
        self.title = 'ELB Listener uses an outadated predefined SSL security policy.'
        self.description = 'The security policy on one of the listeners to a load balancer is outdated.'
        self.why_is_it_important = (
            'The security policy of a listener defines ciphers and protocols it uses when communicating with the ELB. '
            'Policies get updated when protocols are found to be not as secure as once thought, '
            'so an outdated security policy may be leave the connection between a listener and an ELB vulnerable.'
        )
        self.how_do_i_fix_it = (
            'Change the security policy on the listener to a more recent one. '
            'Further instructions and information can be found here: '
            'https://docs.aws.amazon.com/elasticloadbalancing/latest/application/create-https-listener.html'
        )
        super(ELBListenerSecurityPredefinedOutdated, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        """
        TODO
        """
        compliance_type = 'NON_COMPLIANT'
        if item["metadata"][4] == 'A listener uses an outdated predefined SSL security policy':
            self.annotation = (
                f'"{item["metadata"][1]}" load balancer in region "{item["metadata"][0]}" with resource ID: '
                f'"{item["resourceId"]}" uses an outdated predefined SSL security policy.'
            )
        else:
            compliance_type = 'COMPLIANT'
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
        self.title = 'An ELB listener uses a cipher or protocol that is not recommended.'
        self.description = 'A load balancer uses a cipher or protocol that is not recommended.'
        self.why_is_it_important = (
            'Vulnerabilities can be found in ciphers and protocols, '
            'and so they may become deprecated in favour of more secure ones. '
            'It is important to make sure that a listener does not use outdated ciphers or protocols, '
            'as otherwise they will be insecure.'
        )
        self.how_do_i_fix_it = (
            'Change the security policy on the listener to one that is recommended. '
            'Further instructions and information can be found here: '
            'https://docs.aws.amazon.com/elasticloadbalancing/latest/application/create-https-listener.html'
        )
        super(ELBListenerSecurityProtocolDiscouraged, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        """
        TODO
        """
        compliance_type = 'NON_COMPLIANT'
        if item["metadata"][4] == 'A listener uses a deprecated cipher or protocol':
            self.annotation = (
                f'"{item["metadata"][1]}" load balancer in region "{item["metadata"][0]}" with resource ID: '
                f'"{item["resourceId"]}" uses a cipher or protocol that is not recommended.'
            )
        else:
            compliance_type = 'COMPLIANT'
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
        self.title = 'An ELB Listener uses an insecure cipher or protocol.'
        self.description = 'A load balancer uses an insecure cipher or protocol.'
        self.why_is_it_important = (
            'Vulnerabilities can be found in ciphers and protocols, '
            'and so they may become deprecated in favour of more secure ones. '
            'It is important to make sure that a listener does not use outdated ciphers or protocols, '
            'as otherwise they will be insecure.'
        )
        self.how_do_i_fix_it = (
            'Change the security policy on the listener to a more recent one. '
            'Further instructions and information can be found here: '
            'https://docs.aws.amazon.com/elasticloadbalancing/latest/application/create-https-listener.html'
        )
        super(ELBListenerSecurityInsecureProtocol, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        """
        TODO
        """
        compliance_type = 'NON_COMPLIANT'
        if item["metadata"][3] == 'Red':
            self.annotation = (
                f'"{item["metadata"][1]}" load balancer in region "{item["metadata"][0]}" with resource ID: '
                f'"{item["resourceId"]}" uses an insecure cipher or protocol.'
            )
        else:
            compliance_type = 'COMPLIANT'
        return self.build_evaluation(
            item['resourceId'],
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )
