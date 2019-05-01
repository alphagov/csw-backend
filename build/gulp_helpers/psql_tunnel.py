"""
Wrapper script to execute commands against a PosgreSQL database inside a VPC
by invoking an SSH tunnel through a bastion server
"""
import sys
import os
import re
import json
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import argparse
from sshtunnel import SSHTunnelForwarder


parser = argparse.ArgumentParser()
parser.add_argument(
    "--tunnel", help="The host IP to tunnel through", action="store", dest="tunnel"
)
parser.add_argument(
    "--key", help="The SSH private key path", action="store", dest="ssh_key"
)
parser.add_argument(
    "--host", help="The target database connection string", action="store", dest="host"
)
parser.add_argument(
    "--database", help="The database to connect to", action="store", dest="database"
)
parser.add_argument(
    "--user", help="The database user name", action="store", dest="user"
)
parser.add_argument(
    "--password", help="The database user password", action="store", dest="password"
)
parser.add_argument(
    "--command", help="The command to execute", action="store", dest="command"
)
parser.add_argument(
    "--script",
    help="The path to an SQL script to be executed",
    action="store",
    dest="script",
)
args = parser.parse_args()

# print (os.getcwd())

# for key,val in args.__dict__.items():
#     print (f"{key} = {val}")

# exit(1)


def read_script(script_path):
    try:
        commands = []
        abs_path = os.path.join(os.getcwd(), script_path)
        print(abs_path)
        with open(abs_path, "r") as script:
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
        print(f"Failed to open script: {script_path}: " + str(err))

    return commands


try:

    with SSHTunnelForwarder(
        (args.tunnel, 22),
        ssh_private_key=args.ssh_key,
        ssh_username="ubuntu",
        remote_bind_address=(args.host, 5432),
    ) as server:

        server.start()
        # print ("Server connected")

        params = {
            "database": args.database,
            "user": args.user,
            "password": args.password,
            "host": "localhost",
            "port": server.local_bind_port,
        }

        conn = psycopg2.connect(**params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        curs = conn.cursor()

        # print ("Database connected")

        if args.command is not None:
            # curs.execute(args.command)
            commands = [args.command]

        if args.script is not None:
            commands = read_script(args.script)
            # print (*commands, sep='\n')

        for index, command in enumerate(commands, start=1):

            try:
                print(f"{index} Executing command:\n{command}\n\n", file=sys.stderr)
                curs.execute(command)
                if re.match("^SELECT", command):
                    results = curs.fetchall()
                    # print(*results, sep='\n')
                    print(json.dumps(results))
            except Exception as err:
                print("Failed to execute command: " + str(err), file=sys.stderr)

        # print ("Close connection")
        curs.close()
        conn.close()

except Exception as err:
    print("Connection Failed: " + str(err))
