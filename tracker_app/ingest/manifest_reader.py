from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
import pandas as pd
import csv

@dataclass
class ManifestRecord:
    word: str
    filename: str
    local_path: str
    remote_url: Optional[str] = None

def read_manifest(csv_path: Path) -> List[ManifestRecord]:
    """
    Read manifest CSV, handling æøå and different delimiters.
    Auto-detects ; vs , delimiter.
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"Manifest not found: {csv_path}")
    
    # Sniff delimiter
    with open(csv_path, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        delimiter = ';' if ';' in first_line else ','
        f.seek(0)
        
        reader = csv.DictReader(f, delimiter=delimiter)
        records = []
        
        for row in reader:
            # Strip whitespace from keys and values
            row = {k.strip(): v.strip() for k, v in row.items()}
            
            # Helper to safely get fields
            def get_field(names):
                for name in names:
                    if name in row and row[name]:
                        return row[name]
                return None
            
            word = get_field(['word', 'gloss', 'tegn'])
            filename = get_field(['filename', 'file', 'video'])
            path = get_field(['local_path', 'path', 'location'])
            url = get_field(['remote_url', 'url', 'link'])
            
            if word and filename:
                # Basic validation
                records.append(ManifestRecord(
                    word=word,
                    filename=filename,
                    local_path=path or str(Path(csv_path).parent / filename),
                    remote_url=url
                ))
    
    return records
