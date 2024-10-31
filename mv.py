from prefect import task, flow
from prefect import get_run_logger
import psycopg2
from psycopg2 import OperationalError
import time
from prefect.blocks.system import Secret

# Load secrets
pw = Secret.load("db-pw").get()
host = Secret.load("host").get()

@task
def connect():
    """Connect to the PostgreSQL database server"""
    try:
        logger = get_run_logger()
        logger.info("Connecting to the database...")
        db_config = {
            "dbname": "warehouse",
            "user": "goodrich_okoro",
            "password": pw,
            "host": host
        }
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        logger.info("Connection Successful 👍")
        return conn, cur
    except OperationalError as e:
        logger = get_run_logger()
        logger.error(f"Error: {e}")
        return None, None

@task
def close_connection(conn, cur):
    if conn and cur:
        cur.close()
        conn.close()

@flow
def refresh_bfree():
    logger = get_run_logger()
    logger.info('Refreshing BFREE Materialized View... Please hold on...')
    start_time = time.time()
    
    conn, cur = connect()
    if conn and cur:
        try:
            query = "REFRESH MATERIALIZED VIEW bi.bfree"
            logger.info('Refreshing view...')
            cur.execute(query)
            conn.commit()
            logger.info("Done refreshing the view.")
        finally:
            close_connection(conn, cur)
    
    duration = round((time.time() - start_time) / 60.0, 2)
    logger.info(f"Execution time: {duration} minutes")

if __name__ == "__main__":
    refresh_bfree()
