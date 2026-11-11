from unittest.mock import patch

from app.services.cv_processing_service import extract_application_cv


def test_cv_extraction_failure():

    with patch(
        "app.services.cv_processing_service.extract_cv_text"
    ) as mock_extractor:

        mock_extractor.side_effect = RuntimeError(
            "Simulated extraction failure"
        )

        print("Mock extractor configured successfully")