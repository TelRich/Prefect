from prefect import flow, task
from prefect.logging import get_run_logger

@task
def say_hello(name: str) -> str:
    """A simple task that says hello"""
    logger = get_run_logger()
    message = f"Hello, {name}!"
    logger.info(message)
    return message

@flow(name="Hello Flow", log_prints=True)
def hello_flow(name: str = "World") -> None:
    """A simple flow that demonstrates basic Prefect functionality"""
    message = say_hello(name)
    print(f"🎉 {message}")

if __name__ == "__main__":
    hello_flow()