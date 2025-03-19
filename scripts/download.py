from kaggle.api.kaggle_api_extended import KaggleApi
from pathlib import Path
import zipfile
import logging

# Constants (uppercase for clarity)
ROOT_FOLDER = Path().cwd().parents[0]
DATA_FOLDER = ROOT_FOLDER / "data"
COMPETITION = "optiver-trading-at-the-close"
COMPETITION_ZIP_PATH = DATA_FOLDER / "optiver-trading-at-the-close.zip"
EXTRACT_FOLDER = DATA_FOLDER / "optiver_trading_at_the_close"
LOG_FOLDER = ROOT_FOLDER / "logs"
LOG_PATH = LOG_FOLDER / "download_data.log"


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


def download_competition_data(api: KaggleApi, competition: str, path: Path) -> None:
    """
    Downloads competition data using the Kaggle API.

    Args:
        api (KaggleApi): Authenticated Kaggle API instance.
        competition (str): Kaggle competition name.
        path (Path): Directory to save the files.

    Returns:
        None
    """
    try:
        logger.info(f"Downloading competition files for '{competition}'...")
        api.competition_download_files(competition, path=path)
        logger.info("Download completed.")
    except OSError as e:
        logger.error(f"Network error: {e}")
    except Exception as e:
        logger.error(f"Error downloading competition: {e}")


def extract_zip_file(zip_path: Path, extract_to: Path) -> None:
    """
    Extracts a ZIP file to the specified directory.

    Args:
        zip_path (Path): Path to the ZIP file.
        extract_to (Path): Destination directory.

    Returns:
        None
    """
    if not zip_path.exists():
        logger.warning(f"ZIP file {zip_path} not found. Skipping extraction.")
        return

    try:
        logger.info(f"Extracting files to {extract_to}...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)
        logger.info("Extraction completed.")
    except zipfile.BadZipFile:
        logger.error(f"Corrupted ZIP file: {zip_path}. Extraction failed.")
    except Exception as e:
        logger.error(f"Unexpected error during extraction: {e}")


def main() -> None:
    """
    Main function to handle downloading and extracting Kaggle competition data.
    """
    api = KaggleApi()
    api.authenticate()

    DATA_FOLDER.mkdir(parents=True, exist_ok=True)
    LOG_FOLDER.mkdir(parents=True, exist_ok=True)

    if not COMPETITION_ZIP_PATH.exists():
        download_competition_data(api, COMPETITION, DATA_FOLDER)
    else:
        logger.info("Competition files already exist, skipping download.")

    if COMPETITION_ZIP_PATH.exists():
        extract_zip_file(COMPETITION_ZIP_PATH, EXTRACT_FOLDER)
    else:
        logger.warning("Skipping extraction, ZIP file not found.")


if __name__ == "__main__":
    main()
