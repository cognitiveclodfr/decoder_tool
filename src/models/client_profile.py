"""Client Profile - represents a client configuration with column mapping"""
from dataclasses import dataclass, field, asdict
from typing import Dict, Optional
import json
from pathlib import Path


@dataclass
class ClientProfile:
    """
    Represents a client profile with custom configuration

    Attributes:
        client_id: Unique identifier for the client
        client_name: Full name of the client
        column_mapping: Dictionary mapping client's column names to standard names
        output_folder: Path to folder where exports for this client should be saved
        platform: E-commerce platform (e.g., 'Shopify', 'WooCommerce')
    """
    client_id: str
    client_name: str
    column_mapping: Dict[str, str] = field(default_factory=dict)
    output_folder: Optional[str] = None
    platform: str = "Shopify"

    # Standard column names that the application expects
    STANDARD_COLUMNS = {
        'Name': 'Order ID',
        'Created at': 'Order date',
        'Lineitem quantity': 'Quantity',
        'Lineitem name': 'Product name',
        'Lineitem sku': 'Product SKU',
        'Lineitem price': 'Price',
        'Lineitem discount': 'Discount',
        'Shipping Name': 'Shipping name',
        'Shipping Method': 'Shipping method',
    }

    def __post_init__(self):
        """Validate profile after initialization"""
        if not self.client_id or not self.client_id.strip():
            raise ValueError("client_id cannot be empty")
        if not self.client_name or not self.client_name.strip():
            raise ValueError("client_name cannot be empty")

    def to_dict(self) -> dict:
        """
        Convert profile to dictionary for JSON serialization

        Returns:
            Dictionary representation of the profile
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'ClientProfile':
        """
        Create ClientProfile from dictionary

        Args:
            data: Dictionary with profile data

        Returns:
            ClientProfile instance
        """
        return cls(**data)

    def to_json(self) -> str:
        """
        Convert profile to JSON string

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'ClientProfile':
        """
        Create ClientProfile from JSON string

        Args:
            json_str: JSON string with profile data

        Returns:
            ClientProfile instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def get_mapped_column(self, client_column: str) -> str:
        """
        Get standard column name for a client's column

        Args:
            client_column: Column name from client's export

        Returns:
            Standard column name (or original if no mapping exists)
        """
        return self.column_mapping.get(client_column, client_column)

    def has_column_mapping(self) -> bool:
        """
        Check if profile has any column mappings defined

        Returns:
            True if mappings exist, False otherwise
        """
        return bool(self.column_mapping)

    def validate_output_folder(self) -> bool:
        """
        Check if output folder exists and is accessible

        Returns:
            True if folder is valid, False otherwise
        """
        if not self.output_folder:
            return False

        folder = Path(self.output_folder)
        return folder.exists() and folder.is_dir()

    def ensure_output_folder(self) -> Path:
        """
        Ensure output folder exists, create if needed

        Returns:
            Path to output folder

        Raises:
            ValueError: If output_folder is not set
            OSError: If folder cannot be created
        """
        if not self.output_folder:
            raise ValueError("output_folder is not set")

        folder = Path(self.output_folder)
        folder.mkdir(parents=True, exist_ok=True)
        return folder


# Predefined platform templates for common e-commerce platforms
PLATFORM_TEMPLATES = {
    'Shopify': ClientProfile(
        client_id='template_shopify',
        client_name='Shopify Template',
        column_mapping={},  # No mapping needed - Shopify is the standard
        platform='Shopify'
    ),
    'WooCommerce': ClientProfile(
        client_id='template_woocommerce',
        client_name='WooCommerce Template',
        column_mapping={
            'Order ID': 'Name',  # WooCommerce 'Order ID' → Standard 'Name'
            'Ordered at': 'Created at',  # WooCommerce 'Ordered at' → Standard 'Created at'
        },
        platform='WooCommerce'
    ),
}


def create_default_profile(client_id: str, client_name: str, platform: str = 'Shopify') -> ClientProfile:
    """
    Create a default profile for a client based on platform

    Args:
        client_id: Unique client identifier
        client_name: Full name of the client
        platform: E-commerce platform (default: 'Shopify')

    Returns:
        ClientProfile with platform-specific defaults
    """
    template = PLATFORM_TEMPLATES.get(platform, PLATFORM_TEMPLATES['Shopify'])

    return ClientProfile(
        client_id=client_id,
        client_name=client_name,
        column_mapping=template.column_mapping.copy(),
        platform=platform
    )
