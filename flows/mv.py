from prefect import task, flow
from prefect import get_run_logger
import psycopg2
from psycopg2 import OperationalError
import time

from prefect.blocks.system import Secret

secret_block = Secret.load("db-pw")

# Access the stored secret
pw = secret_block.get()


secret_block1 = Secret.load("host")

# Access the stored secret
host = secret_block1.get()


@task
def connect():
    """Connect to the PostgreSQL database server\n"""
    try:
        start_time = time.time()
        logger = get_run_logger()
        logger.info("""Connecting to the database.......\n""")
        db_config = {
            "dbname": "warehouse",
            "user": "goodrich_okoro",
            "password": f"{pw}",
            "host": f"{host}"
        }   
        
        # Open a cursor to perform database operations
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        end_time = time.time()
        
        duration = round((end_time - start_time)/60.0,2)
        logger.info("Connection Suceessful 👍\n")
        logger.info(f"Execution time: {duration} minutes\n")
        return conn, cur
    
    except OperationalError as e:
        logger.info(f"Error: {e}")
        
        


@flow
def refresh_bfree():
    logger = get_run_logger()
    logger.info('\nRefreshing BFREE Materialized View..... Please hold on.....\n')
    start_time = time.time()
    conn,cur = connect()
    query = """
    REFRESH MATERIALIZED VIEW bi.bfree
    """
    logger.info('Refreshing view......\n')
    cur.execute(query)
    conn.commit()
    end_time = time.time()
    duration = round((end_time - start_time)/60.0,2)
    
    logger.info("Done refreshing the view \n")
    logger.info(f"Execution time: {duration} minutes\n")
    
# @flow
# def refresh_originations():
#     logger = get_run_logger()
#     logger.info('\nRefreshing Originations Materialized View..... Please hold on.....\n')
#     start_time = time.time()
#     conn,cur = connect()
#     query = """
#     REFRESH MATERIALIZED VIEW bi.originations
#     """
#     logger.info('Refreshing view......\n')
#     cur.execute(query)
#     conn.commit()
#     end_time = time.time()
#     duration = round((end_time - start_time)/60.0,2)
    
#     logger.info("Done refreshing the view \n")
#     logger.info(f"Execution time: {duration} minutes\n")
    
if __name__ == "__main__":
    refresh_bfree()
    # refresh_bfree.serve(
    #     name="bfree-deployment",
    #     cron="5 * * * *",
    #     work_pool_name="my-managed-pool",
    #     tags=["mv", "bfree"],
    #     description="refresh bfree materialized view",
    #     version="mv/deployments",
    # )
    
    # refresh_originations()
    
# if __name__ == "__main__":
#     get_repo_info.serve(
#         name="my-first-deployment",
#         cron="* * * * *",
#         tags=["testing", "tutorial"],
#         description="Given a GitHub repository, logs repository statistics for that repo.",
#         version="tutorial/deployments",
#     )
    

    


    