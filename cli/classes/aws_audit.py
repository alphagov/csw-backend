import importlib
import inspect
import os
import pkgutil
import logging
from datetime import datetime
from chalicelib.utilities import Utilities
from chalicelib.aws.gds_aws_client import GdsAwsClient
from chalicelib.aws.gds_ec2_client import GdsEc2Client


class AwsAudit:
  def __init__(self):
    #self.app_name = name
    self.prefix = "aws"
    self.mode = "cli"
    self.log = logging.getLogger("CloudSecurityWatch")
    self.log.setLevel(logging.DEBUG)
    self.utilities = Utilities()
    self.caller = None
    self.regions = None

  def get_datetime(self):
    now = datetime.now()
    iso = now.isoformat()
    date_string = iso[0:19]
    return date_string

  def start_audit(self):
    """
    Create a default audit object and set the start time
    """
    now = self.get_datetime()
    caller = self.get_caller()
    self.audit = {
      "account": str(caller["Account"]),
      "started": now,
      "checks": []
    }

  def add_check_results(self, check):
    self.audit["checks"].append(check)

  def complete_audit(self):
    now = self.get_datetime()
    self.audit["completed"] = now
    caller = self.get_caller()
    account = str(caller["Account"])
    path = f"results/{account}/{now}/audit.json"
    data = self.utilities.to_json(self.audit, True)
    self.utilities.write_file(path, data)

  def get_criteria(self,parent_module_name='chalicelib.criteria'):
    """
    A helper function returning a set with all classes in the chalicelib.criteria submodules
    having a class attribute named active with value True.
    """
    parent_module = importlib.import_module(parent_module_name)
    criteria = []
    ignore_check_classes = [
        "AwsIamValidateInspectorPolicy"
    ]
    for loader, module_name, ispkg in pkgutil.iter_modules(parent_module.__path__):
      for name, cls in inspect.getmembers(importlib.import_module(f'{parent_module.__name__}.{module_name}')):
        is_class = inspect.isclass(cls)
        is_criterion = is_class and 'CriteriaDefault' in [supercls.__name__ for supercls in inspect.getmro(cls)]
        if is_criterion:
          criteria.append(f'{parent_module.__name__}.{module_name}.{name}')
    return criteria

  def get_active_criteria(self):
    criteria = self.get_criteria()
    active = []
    for criterion in criteria:
        instance = self.get_check_instance(criterion)
        if instance is not None and instance.active and instance.title:
            active.append(criterion)
    return active

  def get_check_instance(self, class_path):
    """
    The inspector policy check is only relevant when running in lambda chalice mode
    For the CLI version the assume is handled outside the script.
    """
    ignore_check_classes = [
      "AwsIamValidateInspectorPolicy"
    ]
    path = class_path.split(".")
    class_name = path.pop()
    module_name = ".".join(path)
    #print(f"{module_name} : {class_name}")
    if class_name not in ignore_check_classes:
      module = importlib.import_module(module_name)
      class_ = getattr(module, class_name)
      instance = class_(self)
    else:
      instance = None
    return instance

  def get_caller(self):
    aws = GdsAwsClient(self)
    if self.caller is None:
      self.caller = aws.get_caller_details()
    return self.caller

  def get_session(self):
    # Assume role session is not needed since the credentials are assumed from the
    # execution of the script through aws-vault or similar.
    session = {
      "SecretAccessKey": os.environ["AWS_SECRET_ACCESS_KEY"],
      "SessionToken": os.environ["AWS_SESSION_TOKEN"],
      "AccessKeyId": os.environ["AWS_ACCESS_KEY_ID"]
    }
    return session

  def get_regions(self):

    if self.regions is None:
      ec2 = GdsEc2Client(self)
      self.regions = ec2.describe_regions()
    return self.regions

  def get_check_requests(self, check):

    regions = self.get_regions()
    requests = []

    params = {}

    if check.is_regional:
      for region in regions:
        region_params = params.copy()
        region_params["region"] = region["RegionName"]
        self.log.debug("Create request from region: " + region_params["region"])
        requests.append(region_params)
    else:
      requests.append(params)
    return requests

  def build_audit_resource_item(self, api_item, check, params):

      item = check.translate(api_item)
      # store original API resource data
      item["resource_data"] = api_item

      # populate foreign keys
      item["criterion_id"] = check

      # set evaluated date
      item["date_evaluated"] = datetime.now()

      # for some TA checks the region will be populated from the
      # check.translate method.
      # for custom checks where an API call is made for each region
      # the region is added here.
      if "region" in params:
          item["region"] = params["region"]
          # item_raw["region"] = params["region"]

      # populate the resource_identifier field
      item['resource_persistent_id'] = self.get_resource_persistent_id(check, item)

      return item

  def get_resource_persistent_id(self, check, item):
    if 'resource_name' in item and item['resource_name'] is not None:
      name = item.get('resource_name', '')
    else:
      name = item.get('resource_id', '')

    return (check.resource_type + "::"
            + item.get('region', '') + "::"
            + str(self.audit["account"]) + "::"
            + name)

  def show_check_summary(self, summary):
      for key in summary:
          if key == "regions":
              print("regions: " + ", ".join(summary[key]["list"]))
          elif "display_stat" in summary[key]:
              print(f"{key}: " + str(summary[key]["display_stat"]))

  def has_exception(self, check, resource_id):
      return True