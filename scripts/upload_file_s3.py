import boto3
import logging
import json
from pathlib import Path
from botocore.exceptions import NoCredentialsError, EndpointConnectionError

CONFIG_PATH = Path(__file__).parent / "config.json"
DATA_FOLDER = Path(__file__).parents[1] / "data" / "optiver_trading_at_the_close"

def load_config() -> dict:
    """Loads configuration from JSON file."""
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


config = load_config()

# Configure Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialise S3
s3 = boto3.client(
    "s3",
    endpoint_url=config["s3_endpoint_url"],
    aws_access_key_id=config["aws_access_key_id"],
    aws_secret_access_key=config["aws_secret_access_key"],
    region_name=config["region_name"],
)


def ensure_bucket_exists(bucket_name: str) -> None:
    """
    Ensures that the specified S3 bucket exists, creating it if necessary.

    Args:
        bucket_name (str): Name of the S3 bucket.
    """
    try:
        s3.head_bucket(Bucket=bucket_name)  # Check if bucket exists
    except Exception:
        logger.warning(f"Bucket '{bucket_name}' not found. Creating it...")
        s3.create_bucket(Bucket=bucket_name)
        logger.info(f"Bucket '{bucket_name}' created successfully.")


def upload_file_to_s3(
    file_path: Path, bucket_name: str, object_name: str = None
) -> bool:
    """
    Uploads a file to an S3 bucket.

    Args:
        file_path (Path): Path to the file to upload.
        bucket_name (str): Name of the S3 bucket.
        object_name (str, optional): S3 object key. Defaults to filename.

    Returns:
        bool: True if upload succeeds, False otherwise.
    """
    if not file_path.exists():
        logger.error(f"File does not exist: {file_path}")
        return False

    if object_name is None:
        object_name = file_path.name  # Default to filename

    try:
        s3.upload_file(str(file_path), bucket_name, object_name)
        logger.info(
            f"Successfully uploaded {file_path} to s3://{bucket_name}/{object_name}"
        )
        return True
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
    except NoCredentialsError:
        logger.critical("AWS credentials not found! Check your configuration.")
    except EndpointConnectionError:
        logger.error("Failed to connect to S3. Check the endpoint URL.")
    except Exception as e:
        logger.exception(f"Unexpected error during upload: {e}")
    return False


if __name__ == "__main__":
    file_name = DATA_FOLDER / "train.csv"
    bucket_name = config["bucket_name"]

    ensure_bucket_exists(bucket_name)
    success = upload_file_to_s3(file_name, bucket_name)

    if success:
        logger.info("File uploaded successfully!")
    else:
        logger.error("File upload failed.")
