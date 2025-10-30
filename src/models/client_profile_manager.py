"""Client Profile Manager - manages client profiles with file server support"""
import json
from pathlib import Path
from typing import List, Optional, Dict
from .client_profile import ClientProfile


class ClientProfileManager:
    """
    Manages client profiles with support for local file server storage

    Profiles are stored as JSON files in a configurable location,
    allowing multiple PCs to share the same configuration.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize profile manager

        Args:
            config_path: Path to configuration directory (defaults to ~/.decoder_tool/profiles)
        """
        if config_path:
            self._config_path = Path(config_path)
        else:
            # Default to user's home directory
            self._config_path = Path.home() / '.decoder_tool' / 'profiles'

        # Ensure config directory exists
        self._config_path.mkdir(parents=True, exist_ok=True)

        # Profile storage
        self._profiles: Dict[str, ClientProfile] = {}

        # Load profiles from disk
        self._load_all_profiles()

    @property
    def config_path(self) -> Path:
        """Get current configuration path"""
        return self._config_path

    def set_config_path(self, path: str) -> None:
        """
        Set configuration path (e.g., to network file server)

        Args:
            path: Path to configuration directory

        Raises:
            ValueError: If path doesn't exist or is not a directory
        """
        new_path = Path(path)

        if not new_path.exists():
            raise ValueError(f"Path does not exist: {path}")

        if not new_path.is_dir():
            raise ValueError(f"Path is not a directory: {path}")

        self._config_path = new_path
        # Reload profiles from new location
        self._profiles.clear()
        self._load_all_profiles()

    def _get_profile_file_path(self, client_id: str) -> Path:
        """
        Get file path for a profile

        Args:
            client_id: Client ID

        Returns:
            Path to profile JSON file
        """
        # Sanitize client_id for use as filename
        safe_id = "".join(c for c in client_id if c.isalnum() or c in ('-', '_'))
        return self._config_path / f"{safe_id}.json"

    def _load_all_profiles(self) -> None:
        """Load all profiles from configuration directory"""
        if not self._config_path.exists():
            return

        for json_file in self._config_path.glob('*.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    profile = ClientProfile.from_dict(data)
                    self._profiles[profile.client_id] = profile
            except Exception as e:
                # Log error but continue loading other profiles
                print(f"Warning: Could not load profile from {json_file}: {str(e)}")

    def add_profile(self, profile: ClientProfile, save: bool = True) -> None:
        """
        Add a new profile

        Args:
            profile: ClientProfile to add
            save: Whether to save to disk immediately (default: True)

        Raises:
            ValueError: If profile with same client_id already exists
        """
        if profile.client_id in self._profiles:
            raise ValueError(f"Profile with client_id '{profile.client_id}' already exists")

        self._profiles[profile.client_id] = profile

        if save:
            self._save_profile(profile)

    def update_profile(self, profile: ClientProfile, save: bool = True) -> None:
        """
        Update an existing profile

        Args:
            profile: ClientProfile with updated data
            save: Whether to save to disk immediately (default: True)

        Raises:
            ValueError: If profile doesn't exist
        """
        if profile.client_id not in self._profiles:
            raise ValueError(f"Profile with client_id '{profile.client_id}' not found")

        self._profiles[profile.client_id] = profile

        if save:
            self._save_profile(profile)

    def delete_profile(self, client_id: str) -> None:
        """
        Delete a profile

        Args:
            client_id: Client ID of profile to delete

        Raises:
            ValueError: If profile doesn't exist
        """
        if client_id not in self._profiles:
            raise ValueError(f"Profile with client_id '{client_id}' not found")

        # Remove from memory
        del self._profiles[client_id]

        # Remove from disk
        profile_file = self._get_profile_file_path(client_id)
        if profile_file.exists():
            profile_file.unlink()

    def get_profile(self, client_id: str) -> Optional[ClientProfile]:
        """
        Get a profile by client_id

        Args:
            client_id: Client ID

        Returns:
            ClientProfile or None if not found
        """
        return self._profiles.get(client_id)

    def has_profile(self, client_id: str) -> bool:
        """
        Check if a profile exists

        Args:
            client_id: Client ID

        Returns:
            True if profile exists, False otherwise
        """
        return client_id in self._profiles

    def get_all_profiles(self) -> List[ClientProfile]:
        """
        Get list of all profiles

        Returns:
            List of ClientProfile objects
        """
        return list(self._profiles.values())

    def get_profile_ids(self) -> List[str]:
        """
        Get list of all profile IDs

        Returns:
            List of client IDs
        """
        return list(self._profiles.keys())

    def get_profile_names(self) -> Dict[str, str]:
        """
        Get dictionary mapping client_ids to client_names

        Returns:
            Dictionary {client_id: client_name}
        """
        return {pid: profile.client_name for pid, profile in self._profiles.items()}

    def count(self) -> int:
        """
        Get number of profiles

        Returns:
            Number of profiles loaded
        """
        return len(self._profiles)

    def clear(self) -> None:
        """Clear all profiles from memory (does not delete from disk)"""
        self._profiles.clear()

    def _save_profile(self, profile: ClientProfile) -> None:
        """
        Save a profile to disk

        Args:
            profile: ClientProfile to save

        Raises:
            OSError: If file cannot be written
        """
        profile_file = self._get_profile_file_path(profile.client_id)

        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)

    def save_all(self) -> None:
        """Save all profiles to disk"""
        for profile in self._profiles.values():
            self._save_profile(profile)

    def reload(self) -> None:
        """Reload all profiles from disk"""
        self._profiles.clear()
        self._load_all_profiles()

    def export_profile(self, client_id: str, export_path: str) -> None:
        """
        Export a profile to a specific location

        Args:
            client_id: Client ID of profile to export
            export_path: Path where to export the profile

        Raises:
            ValueError: If profile doesn't exist
            OSError: If file cannot be written
        """
        profile = self.get_profile(client_id)
        if not profile:
            raise ValueError(f"Profile with client_id '{client_id}' not found")

        export_file = Path(export_path)
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)

    def import_profile(self, import_path: str, overwrite: bool = False) -> ClientProfile:
        """
        Import a profile from a file

        Args:
            import_path: Path to profile JSON file
            overwrite: Whether to overwrite if profile already exists

        Returns:
            Imported ClientProfile

        Raises:
            ValueError: If profile exists and overwrite is False
            FileNotFoundError: If import file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        import_file = Path(import_path)

        if not import_file.exists():
            raise FileNotFoundError(f"Import file not found: {import_path}")

        with open(import_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        profile = ClientProfile.from_dict(data)

        if self.has_profile(profile.client_id) and not overwrite:
            raise ValueError(
                f"Profile with client_id '{profile.client_id}' already exists. "
                f"Use overwrite=True to replace it."
            )

        if self.has_profile(profile.client_id):
            self.update_profile(profile)
        else:
            self.add_profile(profile)

        return profile

    def validate_profiles(self) -> Dict[str, List[str]]:
        """
        Validate all profiles and return any issues found

        Returns:
            Dictionary mapping client_id to list of issues (empty list if valid)
        """
        issues = {}

        for client_id, profile in self._profiles.items():
            profile_issues = []

            # Check client_id
            if not profile.client_id or not profile.client_id.strip():
                profile_issues.append("Empty client_id")

            # Check client_name
            if not profile.client_name or not profile.client_name.strip():
                profile_issues.append("Empty client_name")

            # Check output folder if set
            if profile.output_folder and not profile.validate_output_folder():
                profile_issues.append(f"Invalid output folder: {profile.output_folder}")

            issues[client_id] = profile_issues

        return issues
