"""Tests for ClientProfile module"""
import pytest
import json
from pathlib import Path
from src.models.client_profile import ClientProfile, create_default_profile, PLATFORM_TEMPLATES


class TestClientProfile:
    """Test ClientProfile class"""

    def test_create_profile(self):
        """Test creating a basic profile"""
        profile = ClientProfile(
            client_id="TEST001",
            client_name="Test Client",
            platform="Shopify"
        )

        assert profile.client_id == "TEST001"
        assert profile.client_name == "Test Client"
        assert profile.platform == "Shopify"
        assert profile.column_mapping == {}
        assert profile.output_folder is None

    def test_create_profile_with_mapping(self):
        """Test creating profile with column mapping"""
        mapping = {
            "Order ID": "Name",
            "Ordered at": "Created at"
        }

        profile = ClientProfile(
            client_id="TEST002",
            client_name="WooCommerce Client",
            column_mapping=mapping,
            platform="WooCommerce"
        )

        assert profile.column_mapping == mapping
        assert profile.has_column_mapping() is True

    def test_create_profile_with_output_folder(self):
        """Test creating profile with output folder"""
        profile = ClientProfile(
            client_id="TEST003",
            client_name="Test Client",
            output_folder="/tmp/test_output"
        )

        assert profile.output_folder == "/tmp/test_output"

    def test_empty_client_id_raises_error(self):
        """Test that empty client_id raises ValueError"""
        with pytest.raises(ValueError, match="client_id cannot be empty"):
            ClientProfile(client_id="", client_name="Test")

    def test_empty_client_name_raises_error(self):
        """Test that empty client_name raises ValueError"""
        with pytest.raises(ValueError, match="client_name cannot be empty"):
            ClientProfile(client_id="TEST", client_name="")

    def test_to_dict(self):
        """Test converting profile to dictionary"""
        mapping = {"Order ID": "Name"}
        profile = ClientProfile(
            client_id="TEST004",
            client_name="Test Client",
            column_mapping=mapping,
            output_folder="/tmp/test",
            platform="Shopify"
        )

        data = profile.to_dict()

        assert data['client_id'] == "TEST004"
        assert data['client_name'] == "Test Client"
        assert data['column_mapping'] == mapping
        assert data['output_folder'] == "/tmp/test"
        assert data['platform'] == "Shopify"

    def test_from_dict(self):
        """Test creating profile from dictionary"""
        data = {
            'client_id': "TEST005",
            'client_name': "Test Client",
            'column_mapping': {"Order ID": "Name"},
            'output_folder': "/tmp/test",
            'platform': "WooCommerce"
        }

        profile = ClientProfile.from_dict(data)

        assert profile.client_id == "TEST005"
        assert profile.client_name == "Test Client"
        assert profile.column_mapping == {"Order ID": "Name"}
        assert profile.output_folder == "/tmp/test"
        assert profile.platform == "WooCommerce"

    def test_to_json(self):
        """Test converting profile to JSON"""
        profile = ClientProfile(
            client_id="TEST006",
            client_name="Test Client",
            column_mapping={"Order ID": "Name"},
            platform="Shopify"
        )

        json_str = profile.to_json()
        data = json.loads(json_str)

        assert data['client_id'] == "TEST006"
        assert data['client_name'] == "Test Client"

    def test_from_json(self):
        """Test creating profile from JSON"""
        json_str = json.dumps({
            'client_id': "TEST007",
            'client_name': "Test Client",
            'column_mapping': {},
            'output_folder': None,
            'platform': "Shopify"
        })

        profile = ClientProfile.from_json(json_str)

        assert profile.client_id == "TEST007"
        assert profile.client_name == "Test Client"

    def test_get_mapped_column(self):
        """Test getting mapped column name"""
        profile = ClientProfile(
            client_id="TEST008",
            client_name="Test Client",
            column_mapping={
                "Order ID": "Name",
                "Ordered at": "Created at"
            }
        )

        assert profile.get_mapped_column("Order ID") == "Name"
        assert profile.get_mapped_column("Ordered at") == "Created at"
        assert profile.get_mapped_column("Unknown") == "Unknown"  # Returns original if no mapping

    def test_has_column_mapping(self):
        """Test checking if profile has column mapping"""
        profile_with_mapping = ClientProfile(
            client_id="TEST009",
            client_name="Test Client",
            column_mapping={"Order ID": "Name"}
        )

        profile_without_mapping = ClientProfile(
            client_id="TEST010",
            client_name="Test Client"
        )

        assert profile_with_mapping.has_column_mapping() is True
        assert profile_without_mapping.has_column_mapping() is False

    def test_validate_output_folder_not_set(self):
        """Test validating output folder when not set"""
        profile = ClientProfile(
            client_id="TEST011",
            client_name="Test Client"
        )

        assert profile.validate_output_folder() is False

    def test_validate_output_folder_exists(self, tmp_path):
        """Test validating existing output folder"""
        profile = ClientProfile(
            client_id="TEST012",
            client_name="Test Client",
            output_folder=str(tmp_path)
        )

        assert profile.validate_output_folder() is True

    def test_validate_output_folder_not_exists(self):
        """Test validating non-existent output folder"""
        profile = ClientProfile(
            client_id="TEST013",
            client_name="Test Client",
            output_folder="/nonexistent/path"
        )

        assert profile.validate_output_folder() is False

    def test_ensure_output_folder_creates_folder(self, tmp_path):
        """Test that ensure_output_folder creates the folder"""
        new_folder = tmp_path / "test_output"
        profile = ClientProfile(
            client_id="TEST014",
            client_name="Test Client",
            output_folder=str(new_folder)
        )

        assert not new_folder.exists()
        result = profile.ensure_output_folder()
        assert new_folder.exists()
        assert result == new_folder

    def test_ensure_output_folder_not_set_raises_error(self):
        """Test that ensure_output_folder raises error when folder not set"""
        profile = ClientProfile(
            client_id="TEST015",
            client_name="Test Client"
        )

        with pytest.raises(ValueError, match="output_folder is not set"):
            profile.ensure_output_folder()


class TestPlatformTemplates:
    """Test platform templates"""

    def test_shopify_template_exists(self):
        """Test Shopify template exists"""
        assert 'Shopify' in PLATFORM_TEMPLATES
        template = PLATFORM_TEMPLATES['Shopify']
        assert template.platform == 'Shopify'
        assert template.column_mapping == {}  # Shopify is the standard

    def test_woocommerce_template_exists(self):
        """Test WooCommerce template exists"""
        assert 'WooCommerce' in PLATFORM_TEMPLATES
        template = PLATFORM_TEMPLATES['WooCommerce']
        assert template.platform == 'WooCommerce'
        assert 'Order ID' in template.column_mapping
        assert template.column_mapping['Order ID'] == 'Name'

    def test_create_default_profile_shopify(self):
        """Test creating default Shopify profile"""
        profile = create_default_profile("CLIENT001", "Test Client", "Shopify")

        assert profile.client_id == "CLIENT001"
        assert profile.client_name == "Test Client"
        assert profile.platform == "Shopify"
        assert profile.column_mapping == {}

    def test_create_default_profile_woocommerce(self):
        """Test creating default WooCommerce profile"""
        profile = create_default_profile("CLIENT002", "Test Client", "WooCommerce")

        assert profile.client_id == "CLIENT002"
        assert profile.client_name == "Test Client"
        assert profile.platform == "WooCommerce"
        assert 'Order ID' in profile.column_mapping
        assert profile.column_mapping['Order ID'] == 'Name'

    def test_create_default_profile_unknown_platform(self):
        """Test creating profile with unknown platform defaults to Shopify"""
        profile = create_default_profile("CLIENT003", "Test Client", "UnknownPlatform")

        assert profile.platform == "UnknownPlatform"
        assert profile.column_mapping == {}  # Uses Shopify template as default
