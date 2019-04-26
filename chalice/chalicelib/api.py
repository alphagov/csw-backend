"""
API LAMBDAS
"""
import os
import re
import json
from datetime import datetime
# from peewee import Case, fn
# from botocore.exceptions import ClientError
# from chalice import Rate

from app import app
from chalicelib.database_handle import DatabaseHandle


def read_script(script_path):
    try:
        commands = []
        abs_path = os.path.join(os.getcwd(), script_path)
        print(abs_path)
        with open(abs_path,'r') as script:
            command = ""
            lines = script.readlines()
            for line in lines:
                # Ignore script comments
                if not re.match("^\-{2}", line):
                    # Treat empty lines as breaks between commands
                    if re.match("^\s*$", line):

                        if len(command) > 0:
                            # Only add command to array if it's non-empty
                            commands.append(command)
                            command = ""

                    else:
                        # If non-empty and not a comment then it's part of the previous command
                        command += line
            # If there's no new line at the end of the script
            # then the last command gets missed if you don't do this
            if len(command) > 0:
                commands.append(command)
    except Exception as err:
        print (f"Failed to open script: {script_path}: " + str(err))

    return commands


def execute_update_stats_tables(event, context):
    status = 0
    try:
        dbh = DatabaseHandle(app)
        commands = read_script('api/sql/summary_stats.sql')
        dbh.execute_commands(commands)
        status = 1
    except Exception as err:
        app.log.error("Update stats tables error: " + app.utilities.to_json(data))
    return {
        "status": status
    }


# @app.schedule(Rate(24, unit=Rate.HOURS))
@app.lambda_function()
def update_stats_tables(event, context):
    return execute_update_stats_tables(event, context)