from prefect import flow

if __name__ == "__main__":
    flow.from_source(
        source="https://github.com/TelRich/Prefect.git",
        entrypoint="mv.py:refresh_bfree",
    ).deploy(
        name="my-second-deployment",
        work_pool_name="my-work-pool",
        # work_pool_name="my-managed-pool",
        cron="5 * * * *",
    )