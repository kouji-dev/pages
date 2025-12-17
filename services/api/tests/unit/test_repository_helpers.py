"""Helper functions for repository unit tests."""

from unittest.mock import MagicMock


def create_mock_result(scalar_value=None, scalars_list=None):
    """Create a mock SQLAlchemy Result object.

    Args:
        scalar_value: Value to return from scalar_one_or_none()
        scalars_list: List of values to return from scalars().all()

    Returns:
        Mock Result object
    """

    mock_result = MagicMock()

    if scalar_value is not None:
        # scalar_one_or_none() is a synchronous method in SQLAlchemy
        mock_result.scalar_one_or_none = MagicMock(return_value=scalar_value)

    if scalars_list is not None:
        mock_scalars = MagicMock()
        mock_scalars.all = MagicMock(return_value=scalars_list)
        mock_result.scalars = MagicMock(return_value=mock_scalars)

    return mock_result
