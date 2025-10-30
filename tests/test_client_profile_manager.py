"""Tests for ClientProfileManager module"""
import pytest
import json
from pathlib import Path
from src.models.client_profile import ClientProfile
from src.models.client_profile_manager import ClientProfileManager


class TestClientProfileManager:
    """Test ClientProfileManager class"""

    @pytest.fixture
    def temp_config_path(self, tmp_path):
        """Create temporary config directory"""
        config_dir = tmp_path / "profiles"
        config_dir.mkdir()
        return str(config_dir)

    @pytest.fixture
    def manager(self, temp_config_path):
        """Create profile manager with temp config path"""
        return ClientProfileManager(temp_config_path)

    @pytest.fixture
    def sample_profile(self):
        """Create sample profile for testing"""
        return ClientProfile(
            client_id="TEST001",
            client_name="Test Client",
            column_mapping={"Order ID": "Name"},
            platform="WooCommerce"
        )

    def test_manager_creates_config_directory(self, tmp_path):
        """Test that manager creates config directory if it doesn't exist"""
        config_dir = tmp_path / "new_profiles"
        assert not config_dir.exists()

        manager = ClientProfileManager(str(config_dir))

        assert config_dir.exists()
        assert manager.config_path == config_dir

    def test_manager_default_config_path(self):
        """Test manager uses default config path"""
        manager = ClientProfileManager()
        expected_path = Path.home() / '.decoder_tool' / 'profiles'

        assert manager.config_path == expected_path

    def test_add_profile(self, manager, sample_profile):
        """Test adding a profile"""
        manager.add_profile(sample_profile)

        assert manager.has_profile("TEST001")
        assert manager.count() == 1

        retrieved = manager.get_profile("TEST001")
        assert retrieved.client_id == "TEST001"
        assert retrieved.client_name == "Test Client"

    def test_add_profile_saves_to_disk(self, manager, sample_profile, temp_config_path):
        """Test that adding profile saves to disk"""
        manager.add_profile(sample_profile)

        # Check file exists
        profile_file = Path(temp_config_path) / "TEST001.json"
        assert profile_file.exists()

        # Check file contents
        with open(profile_file, 'r') as f:
            data = json.load(f)
            assert data['client_id'] == "TEST001"

    def test_add_duplicate_profile_raises_error(self, manager, sample_profile):
        """Test that adding duplicate profile raises error"""
        manager.add_profile(sample_profile)

        with pytest.raises(ValueError, match="already exists"):
            manager.add_profile(sample_profile)

    def test_update_profile(self, manager, sample_profile):
        """Test updating a profile"""
        manager.add_profile(sample_profile)

        # Update profile
        sample_profile.client_name = "Updated Name"
        manager.update_profile(sample_profile)

        # Check updated
        retrieved = manager.get_profile("TEST001")
        assert retrieved.client_name == "Updated Name"

    def test_update_nonexistent_profile_raises_error(self, manager, sample_profile):
        """Test that updating non-existent profile raises error"""
        with pytest.raises(ValueError, match="not found"):
            manager.update_profile(sample_profile)

    def test_delete_profile(self, manager, sample_profile, temp_config_path):
        """Test deleting a profile"""
        manager.add_profile(sample_profile)
        profile_file = Path(temp_config_path) / "TEST001.json"

        assert manager.has_profile("TEST001")
        assert profile_file.exists()

        manager.delete_profile("TEST001")

        assert not manager.has_profile("TEST001")
        assert not profile_file.exists()
        assert manager.count() == 0

    def test_delete_nonexistent_profile_raises_error(self, manager):
        """Test that deleting non-existent profile raises error"""
        with pytest.raises(ValueError, match="not found"):
            manager.delete_profile("NONEXISTENT")

    def test_get_profile_returns_none_if_not_found(self, manager):
        """Test get_profile returns None for non-existent profile"""
        result = manager.get_profile("NONEXISTENT")
        assert result is None

    def test_has_profile(self, manager, sample_profile):
        """Test has_profile method"""
        assert not manager.has_profile("TEST001")

        manager.add_profile(sample_profile)

        assert manager.has_profile("TEST001")

    def test_get_all_profiles(self, manager):
        """Test getting all profiles"""
        profile1 = ClientProfile("ID1", "Client 1")
        profile2 = ClientProfile("ID2", "Client 2")

        manager.add_profile(profile1)
        manager.add_profile(profile2)

        profiles = manager.get_all_profiles()

        assert len(profiles) == 2
        assert any(p.client_id == "ID1" for p in profiles)
        assert any(p.client_id == "ID2" for p in profiles)

    def test_get_profile_ids(self, manager):
        """Test getting profile IDs"""
        profile1 = ClientProfile("ID1", "Client 1")
        profile2 = ClientProfile("ID2", "Client 2")

        manager.add_profile(profile1)
        manager.add_profile(profile2)

        ids = manager.get_profile_ids()

        assert len(ids) == 2
        assert "ID1" in ids
        assert "ID2" in ids

    def test_get_profile_names(self, manager):
        """Test getting profile names dictionary"""
        profile1 = ClientProfile("ID1", "Client One")
        profile2 = ClientProfile("ID2", "Client Two")

        manager.add_profile(profile1)
        manager.add_profile(profile2)

        names = manager.get_profile_names()

        assert len(names) == 2
        assert names["ID1"] == "Client One"
        assert names["ID2"] == "Client Two"

    def test_count(self, manager):
        """Test counting profiles"""
        assert manager.count() == 0

        manager.add_profile(ClientProfile("ID1", "Client 1"))
        assert manager.count() == 1

        manager.add_profile(ClientProfile("ID2", "Client 2"))
        assert manager.count() == 2

        manager.delete_profile("ID1")
        assert manager.count() == 1

    def test_clear(self, manager, sample_profile, temp_config_path):
        """Test clearing profiles from memory"""
        manager.add_profile(sample_profile)
        profile_file = Path(temp_config_path) / "TEST001.json"

        assert manager.count() == 1
        assert profile_file.exists()

        manager.clear()

        assert manager.count() == 0
        assert profile_file.exists()  # File still exists on disk

    def test_reload(self, manager, temp_config_path):
        """Test reloading profiles from disk"""
        # Add profile directly to disk
        profile_data = {
            'client_id': "DISK001",
            'client_name': "Disk Client",
            'column_mapping': {},
            'output_folder': None,
            'platform': "Shopify"
        }

        profile_file = Path(temp_config_path) / "DISK001.json"
        with open(profile_file, 'w') as f:
            json.dump(profile_data, f)

        # Clear and reload
        manager.clear()
        assert manager.count() == 0

        manager.reload()

        assert manager.count() == 1
        assert manager.has_profile("DISK001")

    def test_set_config_path(self, manager, tmp_path):
        """Test changing config path"""
        new_config = tmp_path / "new_profiles"
        new_config.mkdir()

        # Add profile to new location
        profile_data = {
            'client_id': "NEW001",
            'client_name': "New Client",
            'column_mapping': {},
            'output_folder': None,
            'platform': "Shopify"
        }
        profile_file = new_config / "NEW001.json"
        with open(profile_file, 'w') as f:
            json.dump(profile_data, f)

        # Change config path
        manager.set_config_path(str(new_config))

        assert manager.config_path == new_config
        assert manager.has_profile("NEW001")

    def test_set_config_path_nonexistent_raises_error(self, manager):
        """Test setting non-existent config path raises error"""
        with pytest.raises(ValueError, match="does not exist"):
            manager.set_config_path("/nonexistent/path")

    def test_set_config_path_not_directory_raises_error(self, manager, tmp_path):
        """Test setting file as config path raises error"""
        file_path = tmp_path / "file.txt"
        file_path.write_text("test")

        with pytest.raises(ValueError, match="not a directory"):
            manager.set_config_path(str(file_path))

    def test_export_profile(self, manager, sample_profile, tmp_path):
        """Test exporting profile to file"""
        manager.add_profile(sample_profile)

        export_path = tmp_path / "export" / "profile.json"
        export_path.parent.mkdir()

        manager.export_profile("TEST001", str(export_path))

        assert export_path.exists()

        with open(export_path, 'r') as f:
            data = json.load(f)
            assert data['client_id'] == "TEST001"

    def test_export_nonexistent_profile_raises_error(self, manager, tmp_path):
        """Test exporting non-existent profile raises error"""
        export_path = tmp_path / "profile.json"

        with pytest.raises(ValueError, match="not found"):
            manager.export_profile("NONEXISTENT", str(export_path))

    def test_import_profile(self, manager, tmp_path):
        """Test importing profile from file"""
        # Create import file
        profile_data = {
            'client_id': "IMPORT001",
            'client_name': "Imported Client",
            'column_mapping': {"Order ID": "Name"},
            'output_folder': None,
            'platform': "WooCommerce"
        }

        import_path = tmp_path / "import.json"
        with open(import_path, 'w') as f:
            json.dump(profile_data, f)

        # Import
        profile = manager.import_profile(str(import_path))

        assert profile.client_id == "IMPORT001"
        assert manager.has_profile("IMPORT001")

    def test_import_profile_overwrite(self, manager, sample_profile, tmp_path):
        """Test importing profile with overwrite"""
        manager.add_profile(sample_profile)

        # Create import file with same ID but different data
        profile_data = {
            'client_id': "TEST001",
            'client_name': "Overwritten Client",
            'column_mapping': {},
            'output_folder': None,
            'platform': "Shopify"
        }

        import_path = tmp_path / "import.json"
        with open(import_path, 'w') as f:
            json.dump(profile_data, f)

        # Import with overwrite
        profile = manager.import_profile(str(import_path), overwrite=True)

        assert profile.client_name == "Overwritten Client"
        retrieved = manager.get_profile("TEST001")
        assert retrieved.client_name == "Overwritten Client"

    def test_import_duplicate_without_overwrite_raises_error(self, manager, sample_profile, tmp_path):
        """Test importing duplicate without overwrite raises error"""
        manager.add_profile(sample_profile)

        profile_data = sample_profile.to_dict()
        import_path = tmp_path / "import.json"
        with open(import_path, 'w') as f:
            json.dump(profile_data, f)

        with pytest.raises(ValueError, match="already exists"):
            manager.import_profile(str(import_path), overwrite=False)

    def test_import_nonexistent_file_raises_error(self, manager):
        """Test importing from non-existent file raises error"""
        with pytest.raises(FileNotFoundError):
            manager.import_profile("/nonexistent/file.json")

    def test_validate_profiles(self, manager):
        """Test validating profiles"""
        # Add valid profile
        valid_profile = ClientProfile("VALID001", "Valid Client")
        manager.add_profile(valid_profile)

        # Add profile with invalid output folder
        invalid_profile = ClientProfile(
            "INVALID001",
            "Invalid Client",
            output_folder="/nonexistent/folder"
        )
        manager.add_profile(invalid_profile)

        issues = manager.validate_profiles()

        assert len(issues) == 2
        assert issues["VALID001"] == []  # No issues
        assert len(issues["INVALID001"]) > 0  # Has issues
        assert any("Invalid output folder" in issue for issue in issues["INVALID001"])

    def test_save_all(self, manager, temp_config_path):
        """Test saving all profiles"""
        profile1 = ClientProfile("SAVE001", "Client 1")
        profile2 = ClientProfile("SAVE002", "Client 2")

        manager.add_profile(profile1, save=False)
        manager.add_profile(profile2, save=False)

        # Files should not exist yet
        assert not (Path(temp_config_path) / "SAVE001.json").exists()
        assert not (Path(temp_config_path) / "SAVE002.json").exists()

        # Save all
        manager.save_all()

        # Files should now exist
        assert (Path(temp_config_path) / "SAVE001.json").exists()
        assert (Path(temp_config_path) / "SAVE002.json").exists()

    def test_profile_file_path_sanitization(self, manager):
        """Test that client_id is sanitized for file path"""
        # Client ID with special characters
        profile = ClientProfile("TEST@#$%001", "Test Client")
        manager.add_profile(profile)

        # Check that file was created with sanitized name
        profile_files = list(Path(manager.config_path).glob("*.json"))
        assert len(profile_files) == 1
        # Sanitized name should only contain alphanumeric and -_
        assert all(c.isalnum() or c in ('-', '_', '.') for c in profile_files[0].name)

    def test_load_corrupted_profile_file(self, manager, temp_config_path, capsys):
        """Test loading corrupted profile file doesn't crash"""
        # Create corrupted JSON file
        corrupted_file = Path(temp_config_path) / "corrupted.json"
        corrupted_file.write_text("{ invalid json")

        # Reload should not crash
        manager.reload()

        # Should print warning but continue
        captured = capsys.readouterr()
        assert "Warning" in captured.out or "Could not load" in captured.out
