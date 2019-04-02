import fire
from classes.aws_audit import AwsAudit
from classes.progress_bar import ProgressBar
from classes.divider import Divider

app = AwsAudit()


def audit():

  criteria = app.get_criteria()
  session = app.get_session()
  divider = Divider()

  for criterion_class in criteria:
      #print(criterion_class)
      check = app.get_check_instance(criterion_class)

      if check and check.title:
        divider.line()
        print(check.title)
        calls = 0
        summary = None
        progress = ProgressBar()
        progress.start('Progress')
        requests = app.get_check_requests(check)
        check_passed = (check.aggregation_type == "all")
        is_all = (check_passed)

        for request in requests:
          evaluated = []
          calls += 1
          data = check.get_data(session, **request)
          for item in data:
            compliance = check.evaluate({}, item)

            audit_item = app.build_audit_resource_item(
              api_item=item,
              check=check,
              params=request
            )
            audit_item["resource_compliance"] = compliance
            item_passed = (compliance['status_id'] == 2)
            evaluated.append(audit_item)

            check_passed = (check_passed and item_passed) if is_all else (check_passed or item_passed)
          # print(app.utilities.to_json(data))
          progress.update(100*calls/len(requests))
          summary = check.summarize(evaluated, summary)

        progress.end()
        #print(app.utilities.to_json(summary))
        app.show_check_summary(summary)

if __name__ == '__main__':
  fire.Fire()