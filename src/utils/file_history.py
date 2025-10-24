"""File history and favorites management"""
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime


class FileHistory:
    """Manages recent files and favorites"""

    def __init__(self, config_dir: Path = None):
        """
        Initialize file history

        Args:
            config_dir: Directory to store config files
        """
        if config_dir is None:
            config_dir = Path.home() / '.decoder_tool'

        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)

        self.history_file = self.config_dir / 'history.json'
        self.favorites_file = self.config_dir / 'favorites.json'

        self.recent_files = self._load_history()
        self.favorites = self._load_favorites()

    def _load_history(self) -> List[Dict]:
        """Load recent files history"""
        if not self.history_file.exists():
            return []

        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def _save_history(self):
        """Save recent files history"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.recent_files, f, indent=2)
        except Exception:
            pass  # Silently fail

    def _load_favorites(self) -> List[Dict]:
        """Load favorite files"""
        if not self.favorites_file.exists():
            return []

        try:
            with open(self.favorites_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def _save_favorites(self):
        """Save favorite files"""
        try:
            with open(self.favorites_file, 'w', encoding='utf-8') as f:
                json.dump(self.favorites, f, indent=2)
        except Exception:
            pass  # Silently fail

    def add_recent(self, file_path: str, file_type: str = 'master'):
        """
        Add file to recent history

        Args:
            file_path: Path to file
            file_type: Type of file ('master' or 'orders')
        """
        file_path = str(Path(file_path).resolve())

        # Remove if already exists
        self.recent_files = [f for f in self.recent_files if f['path'] != file_path]

        # Add to beginning
        self.recent_files.insert(0, {
            'path': file_path,
            'type': file_type,
            'timestamp': datetime.now().isoformat(),
            'name': Path(file_path).name
        })

        # Keep only last 10
        self.recent_files = self.recent_files[:10]

        self._save_history()

    def get_recent(self, file_type: str = None, limit: int = 10) -> List[Dict]:
        """
        Get recent files

        Args:
            file_type: Filter by file type (None for all)
            limit: Maximum number to return

        Returns:
            List of recent file dictionaries
        """
        files = self.recent_files

        if file_type:
            files = [f for f in files if f.get('type') == file_type]

        # Filter out non-existent files
        files = [f for f in files if Path(f['path']).exists()]

        return files[:limit]

    def clear_recent(self):
        """Clear all recent files"""
        self.recent_files = []
        self._save_history()

    def remove_recent(self, file_path: str):
        """Remove specific file from recent history"""
        file_path = str(Path(file_path).resolve())
        self.recent_files = [f for f in self.recent_files if f['path'] != file_path]
        self._save_history()

    def add_favorite(self, file_path: str, file_type: str = 'master', nickname: str = None):
        """
        Add file to favorites

        Args:
            file_path: Path to file
            file_type: Type of file ('master' or 'orders')
            nickname: Optional nickname for the file
        """
        file_path = str(Path(file_path).resolve())

        # Remove if already exists
        self.favorites = [f for f in self.favorites if f['path'] != file_path]

        # Add favorite
        self.favorites.append({
            'path': file_path,
            'type': file_type,
            'nickname': nickname or Path(file_path).stem,
            'name': Path(file_path).name,
            'pinned_at': datetime.now().isoformat()
        })

        self._save_favorites()

    def remove_favorite(self, file_path: str):
        """Remove file from favorites"""
        file_path = str(Path(file_path).resolve())
        self.favorites = [f for f in self.favorites if f['path'] != file_path]
        self._save_favorites()

    def is_favorite(self, file_path: str) -> bool:
        """Check if file is in favorites"""
        file_path = str(Path(file_path).resolve())
        return any(f['path'] == file_path for f in self.favorites)

    def get_favorites(self, file_type: str = None) -> List[Dict]:
        """
        Get favorite files

        Args:
            file_type: Filter by file type (None for all)

        Returns:
            List of favorite file dictionaries
        """
        files = self.favorites

        if file_type:
            files = [f for f in files if f.get('type') == file_type]

        # Filter out non-existent files
        files = [f for f in files if Path(f['path']).exists()]

        return files

    def clear_favorites(self):
        """Clear all favorites"""
        self.favorites = []
        self._save_favorites()
