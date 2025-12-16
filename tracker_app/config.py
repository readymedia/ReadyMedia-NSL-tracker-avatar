from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration"""
    
    # Paths
    workspace_dir: Path = Path("D:/tegnspråk/workspace")
    cache_dir: Optional[Path] = None
    tracks_dir: Optional[Path] = None
    exports_dir: Optional[Path] = None
    db_path: Optional[Path] = None
    
    # Video processing
    target_fps: int = 25
    target_height: int = 720
    enable_normalization: bool = False  # Set True if videos vary greatly
    
    # Tracking
    tracking_provider: str = "mediapipe"
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5
    
    # Smoothing
    ema_alpha_wrist: float = 0.35
    ema_alpha_fingers: float = 0.55
    ema_alpha_face: float = 0.40
    velocity_clamp_deg_per_frame: float = 18.0
    
    # Output
    save_parquet: bool = True
    save_jsonl: bool = True  # For debugging
    
    # Quality
    min_quality_score: float = 0.5
    
    # Logging
    log_level: str = "INFO"
    log_dir: Optional[Path] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-derive paths
        if self.cache_dir is None:
            self.cache_dir = self.workspace_dir / "cache"
        if self.tracks_dir is None:
            self.tracks_dir = self.workspace_dir / "tracks"
        if self.exports_dir is None:
            self.exports_dir = self.workspace_dir / "exports"
        if self.db_path is None:
            self.db_path = self.workspace_dir / "tracker.db"
        if self.log_dir is None:
            self.log_dir = self.workspace_dir / "logs"
        
        # Ensure directories exist
        for path in [self.workspace_dir, self.cache_dir, self.tracks_dir, 
                     self.exports_dir, self.log_dir]:
            path.mkdir(parents=True, exist_ok=True)


# Global config instance
_config: Optional[Config] = None

def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config()
    return _config
