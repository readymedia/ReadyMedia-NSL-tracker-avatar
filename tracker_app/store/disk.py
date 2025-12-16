import gzip
import orjson
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from loguru import logger


def save_tracking_parquet(
    output_path: Path,
    tracking_data: List[Dict[str, Any]]
) -> None:
    """Save tracking data as Parquet (efficient, columnar)"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df = pd.DataFrame(tracking_data)
    df.to_parquet(
        output_path,
        engine='pyarrow',
        compression='snappy',
        index=False
    )
    
    logger.debug(f"Saved Parquet: {output_path} ({output_path.stat().st_size / 1024:.1f} KB)")


def save_tracking_jsonl(
    output_path: Path,
    tracking_data: List[Dict[str, Any]]
) -> None:
    """Save tracking data as JSONL.gz (human-readable, for debugging)"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with gzip.open(output_path, 'wt', encoding='utf-8') as f:
        for record in tracking_data:
            json_str = orjson.dumps(record, option=orjson.OPT_SERIALIZE_NUMPY).decode('utf-8')
            f.write(json_str + '\n')
    
    logger.debug(f"Saved JSONL: {output_path} ({output_path.stat().st_size / 1024:.1f} KB)")


def save_metadata(
    output_path: Path,
    metadata: Dict[str, Any]
) -> None:
    """Save metadata JSON"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'wb') as f:
        f.write(orjson.dumps(metadata, option=orjson.OPT_INDENT_2 | orjson.OPT_SERIALIZE_NUMPY))
    
    logger.debug(f"Saved metadata: {output_path}")


def load_tracking_parquet(filepath: Path) -> pd.DataFrame:
    """Load tracking data from Parquet"""
    return pd.read_parquet(filepath, engine='pyarrow')
