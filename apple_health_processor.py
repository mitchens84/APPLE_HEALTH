import xml.etree.ElementTree as ET
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
import logging
from datetime import datetime

class HealthDataProcessor:
    """Process Apple Health Data export into structured datasets."""
    
    def __init__(self, export_path: str):
        """
        Initialize the processor with path to export.xml file.
        
        Args:
            export_path: Path to the Apple Health export.xml file
        """
        self.export_path = Path(export_path)
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging for the data processing."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def parse_records_by_type(self, record_type: str) -> pd.DataFrame:
        """
        Parse health records of a specific type into a DataFrame.
        
        Args:
            record_type: The type of health record to extract
            
        Returns:
            DataFrame containing the parsed records
        """
        self.logger.info(f"Parsing records for type: {record_type}")
        
        # Use iterparse to handle large XML files efficiently
        records = []
        context = ET.iterparse(self.export_path, events=("end",))
        
        try:
            for event, elem in context:
                if elem.tag == 'Record' and elem.get('type') == record_type:
                    # Extract record attributes
                    record_data = {
                        'startDate': elem.get('startDate'),
                        'endDate': elem.get('endDate'),
                        'value': elem.get('value'),
                        'unit': elem.get('unit'),
                        'device': elem.get('device'),
                        'sourceName': elem.get('sourceName')
                    }
                    records.append(record_data)
                    
                # Clear element to free memory
                elem.clear()
                
            # Create DataFrame from records
            df = pd.DataFrame(records)
            
            # Convert dates to datetime
            for date_col in ['startDate', 'endDate']:
                if date_col in df.columns:
                    df[date_col] = pd.to_datetime(df[date_col])
                    
            # Convert value to numeric where possible
            try:
                df['value'] = pd.to_numeric(df['value'])
            except Exception as e:
                self.logger.warning(f"Could not convert values to numeric: {e}")
                
            return df
            
        except Exception as e:
            self.logger.error(f"Error parsing {record_type} records: {e}")
            raise
            
    def get_available_record_types(self) -> List[str]:
        """
        Scan the export file to identify all available record types.
        
        Returns:
            List of unique record types found in the export
        """
        record_types = set()
        context = ET.iterparse(self.export_path, events=("end",))
        
        try:
            for event, elem in context:
                if elem.tag == 'Record':
                    record_type = elem.get('type')
                    if record_type:
                        record_types.add(record_type)
                elem.clear()
                
            return sorted(list(record_types))
            
        except Exception as e:
            self.logger.error(f"Error getting record types: {e}")
            raise
            
    def process_workouts(self) -> pd.DataFrame:
        """
        Parse workout records into a DataFrame.
        
        Returns:
            DataFrame containing workout records
        """
        self.logger.info("Processing workout records")
        workouts = []
        context = ET.iterparse(self.export_path, events=("end",))
        
        try:
            for event, elem in context:
                if elem.tag == 'Workout':
                    workout_data = {
                        'workoutActivityType': elem.get('workoutActivityType'),
                        'duration': elem.get('duration'),
                        'startDate': elem.get('startDate'),
                        'endDate': elem.get('endDate'),
                        'totalDistance': elem.get('totalDistance'),
                        'totalEnergyBurned': elem.get('totalEnergyBurned'),
                        'sourceName': elem.get('sourceName')
                    }
                    workouts.append(workout_data)
                elem.clear()
                
            df = pd.DataFrame(workouts)
            
            # Convert dates and numeric values
            for date_col in ['startDate', 'endDate']:
                if date_col in df.columns:
                    df[date_col] = pd.to_datetime(df[date_col])
                    
            numeric_cols = ['duration', 'totalDistance', 'totalEnergyBurned']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    
            return df
            
        except Exception as e:
            self.logger.error(f"Error processing workouts: {e}")
            raise

# Example usage:
if __name__ == "__main__":
    processor = HealthDataProcessor("export.xml")
    
    # Get available record types
    record_types = processor.get_available_record_types()
    print("Available record types:", record_types)
    
    # Process specific health metrics
    steps_df = processor.parse_records_by_type("HKQuantityTypeIdentifierStepCount")
    heart_rate_df = processor.parse_records_by_type("HKQuantityTypeIdentifierHeartRate")
    workouts_df = processor.process_workouts()