"""
Configuration loader for YAML config files
"""
import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigLoader:
    """Load and manage configuration files"""
    
    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            config_dir = os.path.join(
                os.path.dirname(__file__),
                '..',
                'config'
            )
        self.config_dir = Path(config_dir)
    
    def load_config(self, filename: str) -> Dict[str, Any]:
        """Load a YAML configuration file"""
        config_path = self.config_dir / filename
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def get_asset_templates(self) -> Dict[str, Any]:
        """Get asset templates configuration"""
        return self.load_config('asset_templates.yaml')
    
    def get_constraints(self) -> Dict[str, Any]:
        """Get constraints configuration"""
        return self.load_config('constraints.yaml')
    
    def get_optimization_rules(self) -> Dict[str, Any]:
        """Get optimization rules configuration"""
        return self.load_config('optimization_rules.yaml')
    
    def get_asset_type(self, asset_name: str) -> Optional[Dict[str, Any]]:
        """Get specific asset type configuration"""
        templates = self.get_asset_templates()
        asset_types = templates.get('asset_types', [])
        
        for asset_type in asset_types:
            if asset_type.get('name') == asset_name:
                return asset_type
        
        return None

