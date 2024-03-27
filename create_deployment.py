from prefect import flow

if __name__ == "__main__":
    flow.from_source(
        source="https://github.com/TelRich/Prefect.git",
        entrypoint="git_wrkflw.py:repo_info",
    ).deploy(
        name="my-first-deployment",
        work_pool_name="my-managed-pool",
        cron="0 1 * * *",
    )