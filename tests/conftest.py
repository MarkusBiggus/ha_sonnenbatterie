"""Fixtures for testing."""

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.sonnenbatterie.const import DOMAIN

from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_IP_ADDRESS,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_API_TOKEN,
    CONF_DEVICE_ID,
    CONF_MODEL
)

#from tests.common import MockConfigEntry

@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Override async_setup_entry."""
    with patch(
        "custom_components.sonnenbatterie.async_setup_entry", return_value=True
    ) as mock_setup_entry:
        yield mock_setup_entry


@pytest.fixture
def mock_unload_entry() -> Generator[AsyncMock]:
    """Override async_unload_entry."""
    with patch(
        "custom_components.sonnenbatterie.async_unload_entry", return_value=True
    ) as mock_unload_entry:
        yield mock_unload_entry


# @pytest.fixture
# def mock_batterie_client() -> Generator[MagicMock]:
#     """Mock Batterie client."""
#     with (
#         patch("custom_components.sonnenbatterie", autospec=True) as mock_client,
#         patch(
#             "custom_components.sonnenbatterie.config_flow.SonnenbatterieFlowHandler",
#             new=mock_client,
#         ),
#     ):
#         client = mock_client.create.return_value
#     #    client.async_update.return_value = mock_sonnen

#         yield client


# @pytest.fixture
# def mock_config_entry() -> MockConfigEntry:
#     """Mock a config entry."""
#     return MockConfigEntry(
#         domain=DOMAIN,
#         title="192.168.100.200  (api token)",
#         unique_id="321123",
#         data={
#             CONF_USERNAME: '#api_token',
#             CONF_MODEL: 'Power unit Evo IP56',
#             CONF_DEVICE_ID: '321123',
#             CONF_API_TOKEN: 'token',
#             CONF_IP_ADDRESS: '192.168.100.200',
#             CONF_PORT: '80',
#             },
#     )
@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield
