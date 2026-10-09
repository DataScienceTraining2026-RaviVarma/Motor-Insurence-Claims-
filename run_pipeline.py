"""Load, validate, clean, and save the motor insurance data."""

from src.data_cleaner import clean_data, save_cleaned_data
from src.data_loader import load_all_data
from src.logger import setup_logger
from src.validation import validate_all_tables


def run_pipeline():
    """Execute the complete data pipeline and return cleaned tables."""
    logger = setup_logger()
    try:
        logger.info("Loading raw insurance data")
        data = load_all_data("data/raw")

        logger.info("Validating insurance data")
        validate_all_tables(data)

        logger.info("Cleaning insurance data")
        cleaned_data = clean_data(data)

        logger.info("Saving cleaned insurance data")
        save_cleaned_data(cleaned_data, "data/cleaned")
        logger.info("Insurance data pipeline completed successfully")
        return cleaned_data
    except Exception:
        logger.exception("Insurance data pipeline failed")
        raise


if __name__ == "__main__":
    run_pipeline()