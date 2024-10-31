import asyncio
from prefect import task, flow
from prefect import get_run_logger
import psycopg2
from psycopg2 import OperationalError
import time
from prefect.blocks.system import Secret

@task
async def get_secrets():
    pw = await Secret.load("prod-whs-pw")
    host = await Secret.load("prod-whs-host")
    return pw.get(), host.get()

# @task
# async def load_secrets():
#     """
#     Load secrets from prefect block
#     """
#     prod_whs_pw = await Secret.load("prod-warehouse-password")
#     prod_whs_host = await Secret.load("prod-warehouse-host")
#     prod_instafin_key_id = await Secret.load("prod-instafin-key-id")
#     prod_instafin_key_secret = await Secret.load("prod-instafin-key-secret")
#     return prod_whs_pw.get(), prod_whs_host.get(), prod_instafin_key_id.get(), prod_instafin_key_secret.get()


@task
def connect(pw, host):
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
async def refresh_bfree():
    logger = get_run_logger()
    logger.info('Refreshing BFREE Materialized View... Please hold on...')
    start_time = time.time()
    
    pw, host = await get_secrets()
    conn, cur = connect(pw, host)
    
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
    asyncio.run(refresh_bfree())
