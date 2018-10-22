"""
implements aws::couldtrail::logging
"""

from chalicelib.criteria.criteria_default import CriteriaDefault


class AwsCouldtrailLogging(CriteriaDefault):
    """
    """

    def get_data(self, session, **kwargs):
        """
        """
        return
    
    def translate(self, data):
        """
        """
        return

    def evaluate(self, event, item, whitelist=[]):
        """
        """
        return []

    ###
    # helpers
    ###

    # def rule_is_compliant(self, rule):
    #     """
    #     """
    #     return

    # def rule_applies_to_ssh(self, rule):
    #     """
    #     """
    #     return

    # def rule_applies_to_flagged_port(self, rule):
    #     """
    #     """
    #     return

    # def get_current_policy_version(self, session):
    #     """
    #     """
    #     return

    # def get_port_list(self):
    #     """
    #     """
    #     return
