import os
import argparse
import string

parser = argparse.ArgumentParser(description="Generate Panintelligence docker-compose.yml script")

parser.add_argument('--template', dest='template', default='panintelligence-separarates-template.yml')
parser.add_argument('--target', dest='target', default='docker-compose-panintelligence-separates.yml')
parser.add_argument('--host', dest='host', required=True)
parser.add_argument('--username', dest='username', required=True)
parser.add_argument('--password', dest='password', required=True)
parser.add_argument('--licence', dest='licence', required=True)

class MyFormatter(string.Formatter):
    def __init__(self, default='{{{0}}}'):
        self.default=default

    def get_value(self, key, args, kwds):
        if isinstance(key, str):
            return kwds.get(key, self.default.format(key))
        
        return string.Formatter.get_value(key, args, kwds)

cli_args = parser.parse_args()

path = os.path.abspath(os.path.dirname(__file__))
source_path = os.path.join(path, cli_args.template)

with open(source_path, 'r') as source_file:
    template = source_file.read()

formatter = MyFormatter()    

output = formatter.format(template, DATABASEHOST=cli_args.host, DATABASEUSERNAME=cli_args.username, DATABASEPASSWORD=cli_args.password, PANINTELLIGENCELICENCE=cli_args.licence)

target_path = os.path.join(path, cli_args.target)

with open(target_path, 'w') as target_file:
    target_file.write(output)
    print('Completed template build to {}'.format(target_path))