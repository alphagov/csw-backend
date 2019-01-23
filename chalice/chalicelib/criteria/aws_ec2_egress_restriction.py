"""
"""

from chalicelib.criteria.criteria_default import CriteriaDefault

class EgressRestrition(CriteriaDefault):
    active = True

    def evaluate(self, event, item, whitelist=[]):
        """
        """
        raise
