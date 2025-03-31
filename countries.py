#%%
from prefect import flow, task
from sqlalchemy import create_engine, text
from prefect.logging import get_run_logger

DATABASE_URI = "postgresql://telrich:P4nfdzFyIMXoyhUJ1gRfN4B9XAJze1nd@dpg-cvkrr4je5dus73bt9oog-a.oregon-postgres.render.com/countries_k13u"

@task(retries=3, retry_delay_seconds=5)
def test_connection():
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
def create_cities_table():
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
def create_countries_table():
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
def main_flow():
    logger = get_run_logger()
    logger.info("🚀 Starting database setup flow")
    if test_connection():
        create_cities_table()
        create_countries_table()
        logger.info("✅ Database setup completed successfully!")
    else:
        logger.error("🛑 Aborting flow due to connection failure")

if __name__ == "__main__":
    main_flow()