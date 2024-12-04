from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import pandas as pd
from typing import Dict, List, Optional

@dataclass
class DatasetSummary:
    name: str
    record_count: int
    date_range: tuple
    file_path: Path
    columns: List[str]
    file_size: int
    data_types: Dict
    sample_stats: Optional[Dict] = None

class HealthDataReport:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.datasets: Dict[str, DatasetSummary] = {}
        self.processing_time = datetime.now()

    def clean_metric_name(self, name: str) -> str:
        """Clean up metric names and add type indicator."""
        type_indicators = {
            'HKQuantityTypeIdentifier': '(Quantity)',
            'HKCategoryTypeIdentifier': '(Category)',
            'HKDataTypeIdentifier': '(Data)'
        }

        cleaned_name = name
        type_indicator = ''

        # Find which type indicator to use
        for prefix, indicator in type_indicators.items():
            if prefix in name:
                cleaned_name = cleaned_name.replace(prefix, '')
                type_indicator = f" {indicator}"
                break

        return f"{cleaned_name}{type_indicator}"

    def add_dataset_summary(self, name: str, df: pd.DataFrame, file_path: Path):
        """Add summary information for a processed dataset."""
        cleaned_name = self.clean_metric_name(name)
        date_range = (None, None)
        if 'startDate' in df.columns:
            date_range = (df['startDate'].min(), df['startDate'].max())

        sample_stats = None
        if 'value' in df.columns:
            try:
                sample_stats = {
                    'mean': df['value'].mean(),
                    'median': df['value'].median(),
                    'std': df['value'].std(),
                    'min': df['value'].min(),
                    'max': df['value'].max()
                }
            except Exception as e:
                print(f"Warning: Could not calculate statistics for {cleaned_name}: {e}")

        summary = DatasetSummary(
            name=cleaned_name,
            record_count=len(df),
            date_range=date_range,
            file_path=file_path,
            columns=df.columns.tolist(),
            file_size=file_path.stat().st_size,
            data_types=df.dtypes.to_dict(),
            sample_stats=sample_stats
        )

        self.datasets[cleaned_name] = summary
        print(f"Added summary for: {cleaned_name}")  # Debug line

    def create_report(self) -> pd.DataFrame:
        """Generate a DataFrame report of all processed datasets."""
        if not self.datasets:
            return pd.DataFrame()

        rows = []
        for name, summary in self.datasets.items():
            row = {
                'Dataset': name,
                'Records': summary.record_count,
                'Start Date': summary.date_range[0],
                'End Date': summary.date_range[1],
                'File': str(summary.file_path),
                'Size (KB)': summary.file_size/1024,
                'Columns': '; '.join(summary.columns)
            }

            if summary.sample_stats:
                for stat, value in summary.sample_stats.items():
                    row[f'Value {stat}'] = value

            rows.append(row)

        return pd.DataFrame(rows)

    def save_report(self) -> Path:
        """Save the consolidated report as CSV."""
        try:
            df = self.create_report()
            report_filename = "_APPLE_HEALTH_SCHEDULE.csv"
            report_path = self.output_dir / report_filename
            df.to_csv(report_path, index=False)
            return report_path
        except Exception as e:
            print(f"Error saving report: {e}")
            raise
