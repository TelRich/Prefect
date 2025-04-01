#%%
from prefect import flow, task
from sqlalchemy import create_engine, text
from prefect.logging import get_run_logger
from prefect.variables import Variable
from prefect.blocks.system import Secret
import asyncio

# Load the database URI from a Prefect variable
# username = Variable.get("render_username")
# host = Variable.get("render_host")
# dbname = Variable.get("render_dbname")

# @task
# async def load_secret():
#     logger = get_run_logger()
#     password = await Secret.load("render-password")
#     logger.info("�� Password loaded from Secret Manager")
#     return password.get()

@task
async def load_secret():
    logger = get_run_logger()
    password = await Secret.load("render-password")
    username = await Variable.get("render_username")
    host = await Variable.get("render_host")
    dbname = await Variable.get("render_dbname")
    logger.info("�� Password loaded from Secret Manager")
    return password.get(), username, host, dbname

@task(retries=3, retry_delay_seconds=5)
def test_connection(DATABASE_URI):
    logger = get_run_logger()
    try:
        engine = create_engine(
            DATABASE_URI
        )
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful!")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        return False

@task(retries=2)
def create_cities_table(DATABASE_URI):
    logger = get_run_logger()
    try:
        engine = create_engine(
            DATABASE_URI
        )
        create_table_query = """
        CREATE TABLE IF NOT EXISTS cities (
            name VARCHAR PRIMARY KEY,
            country_code VARCHAR,
            city_proper_pop REAL,
            metroarea_pop REAL,
            urbanarea_pop REAL
        );
        """
        with engine.connect() as conn:
            conn.execute(text(create_table_query))
            conn.commit()
            logger.info("✅ Cities table created successfully!")
    except Exception as e:
        logger.error(f"❌ Error creating cities table: {str(e)}")
        raise

@task(retries=2)
def create_countries_table(DATABASE_URI):
    logger = get_run_logger()
    try:
        engine = create_engine(
            DATABASE_URI
        )
        create_table_query = """
        CREATE TABLE IF NOT EXISTS countries (
            code VARCHAR PRIMARY KEY,
            name VARCHAR,
            continent VARCHAR,
            region VARCHAR,
            surface_area REAL,
            indep_year INTEGER,
            local_name VARCHAR,
            gov_form VARCHAR,
            capital VARCHAR,
            cap_long REAL,
            cap_lat REAL
        );
        """
        with engine.connect() as conn:
            conn.execute(text(create_table_query))
            conn.commit()
            logger.info("✅ Countries table created successfully!")
    except Exception as e:
        logger.error(f"❌ Error creating countries table: {str(e)}")
        raise

@flow(name="Database Setup Flow")
async def main_flow():
    logger = get_run_logger()
    # password = await load_secret()
    password, username, host, dbname= await load_secret()
    DATABASE_URI = f"postgresql://{username}:{password}@{host}/{dbname}"
    logger.info("🚀 Starting database setup flow")
    if test_connection(DATABASE_URI):
        create_cities_table(DATABASE_URI)
        create_countries_table(DATABASE_URI)
        logger.info("✅ Database setup completed successfully!")
    else:
        logger.error("🛑 Aborting flow due to connection failure")

if __name__ == "__main__":
    asyncio.run(main_flow())