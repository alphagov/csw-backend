"""
Wrapper script to execute commands against a PosgreSQL database inside a VPC
by invoking an SSH tunnel through a bastion server
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import argparse
from sshtunnel import SSHTunnelForwarder


parser = argparse.ArgumentParser()
parser.add_argument('--tunnel', help='The host IP to tunnel through', action="store", dest="tunnel")
parser.add_argument('--key', help='The SSH private key path', action="store", dest="ssh_key")
parser.add_argument('--host', help='The target database connection string', action="store", dest="host")
parser.add_argument('--database', help='The database to connect to', action="store", dest="database")
parser.add_argument('--user', help='The database user name', action="store", dest="user")
parser.add_argument('--password', help='The database user password', action="store", dest="password")
parser.add_argument('--command', help='The command to execute', action="store", dest="command")
args = parser.parse_args()

# for key,val in args.__dict__.items():
#    print (f"{key} = {val}")

try:

    with SSHTunnelForwarder(
        (args.tunnel, 22),
        ssh_private_key=args.ssh_key,
        ssh_username="ubuntu",
        remote_bind_address=(args.host, 5432)) as server:

        server.start()
        print ("Server connected")

        params = {
            'database': args.database,
            'user': args.user,
            'password': args.password,
            'host': 'localhost',
            'port': server.local_bind_port
        }

        conn = psycopg2.connect(**params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        curs = conn.cursor()

        print ("Database connected")

        status = curs.execute(args.command)

        print ("Close connection")
        curs.close()
        conn.close()

except Exception as err:
    print ("Connection Failed: " + str(err))

