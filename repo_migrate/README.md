# REPO MIGRATE

This short script will assist you in migrating your repo from a sql dump file to a new schema.

## Usage

```bash
python3 migrate.py --db_host=**your db host** \
                   --db_port=3306 \
                   --db_username=**your db username** \
                   --db_password=**your db password** \
                   --repo_filename=**your repo sql dump** \
                   --target_schema=**your target schema**
```

### Variables

#### db_hostname
the dns name of your db.  It should resemble `<<unique-identifier>>.mariadb.database.azure.com`

#### db_port
default 3306.  database port to which you can connect.

#### db_username

administrator username you created your database with (this doesn't need to be the root user, it just needs permission to build a new schema, create and insert tables, triggers and views)

#### db_password

The password for the user stated above

#### repo_filename

upon downloading this script, download your sqldumpfile.sql file with your panintelligence repo into the same directory.

#### target_schema

The script with restore your sql dump file into this database schema.


## Notes
All variables are mandatory.
The file object is currently set to UTF-8 for reading UTF-8 type database dump files.
All contributions and updates are welcome to the script.