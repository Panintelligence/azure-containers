import logging
import traceback
import argparse

import pymysql
import pymysql.cursors


LOGGER = logging.getLogger("database")
LOGGER.setLevel(logging.INFO)


def should_execute_line(line):
    stripped_line = line.strip()
    blacklisted_strings_starts_with = ("DELIMITER", "END")
    blacklisted_strings_contains = ["TRIGGER",
                                    "recordTableInteraction",
                                    "`mis_last_table_interactions`",
                                    "RECORDTABLEINTERACTION",
                                    "recordtableinteraction",
                                    "`MIS_LAST_TABLE_INTERACTIONS`"]
    if stripped_line == "" or stripped_line.startswith(blacklisted_strings_starts_with) or any([item for item in blacklisted_strings_contains if item in stripped_line]):
        return False

    return True


def create_connection(rds_host, rds_port, rds_user, rds_password, db_name=None):
    return pymysql.connect(host=rds_host,
                           port=int(rds_port),
                           user=rds_user,
                           db=db_name,
                           password=rds_password,
                           cursorclass=pymysql.cursors.DictCursor)


def create_repo(schema_name, repo_file, host, port, username, password):
    LOGGER.info('Now attempting to create the repo for %s', schema_name)

    connection = create_connection(host, port, username, password)

    try:
        with connection.cursor() as cursor:
            LOGGER.info('creating new schema %s', schema_name)
            cursor.execute(f"CREATE SCHEMA {schema_name};")
            LOGGER.info('Schema %s created', schema_name)
    except Exception:
        LOGGER.error('problem when creating the database')
        traceback.print_exc()
        raise
    finally:
        connection.close()

    connection = create_connection(host, port, username, password, db_name=schema_name)

    try:
        LOGGER.info('reading data from %s', repo_file)
        with open(repo_file, 'r', encoding='utf-8-sig') as file:
            data = file.read()
            lines = data.split(';\n')
        LOGGER.info('Data read from %s', repo_file)
        with connection.cursor() as cursor:
            LOGGER.info('running through the dump file %s', repo_file)
            for line in lines:

                if should_execute_line(line):
                    LOGGER.info(line)
                    try:
                        statement = line.strip().replace("`dashboard`.", "")\
                                       .replace("/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */", "")\
                                       .replace("/*!50017 DEFINER=`root`@`localhost`*/", "") + ';'
                        cursor.execute(statement)
                    except Exception:
                        LOGGER.error('Exception has been caught when trying to build the repo database for %s',
                                     schema_name)
                        LOGGER.error(statement)
                        raise
            LOGGER.info('Completed running through dump file')
        LOGGER.info('committing database changes')
        connection.commit()
        LOGGER.info('database changes committed')
    except Exception as e:
        LOGGER.error('Found error when configuring data connections.')
        LOGGER.error(e)
        raise
    finally:
        connection.close()


def main():
    create_repo()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="panintelligence repo database Azure deployment")
    parser.add_argument('--db_host')
    parser.add_argument('--db_port', default="3306")
    parser.add_argument('--db_username')
    parser.add_argument('--db_password')
    parser.add_argument('--repo_filename', help="source database dump file")
    parser.add_argument('--target_schema', help="the schema to which you want to build and deploy your repo database")

    args = parser.parse_args()

    schema_name = args.target_schema
    host = args.db_host
    port = args.db_port
    username = args.db_username
    password = args.db_password
    repo_file = args.repo_filename

    create_repo(schema_name, repo_file, host, port, username, password)
