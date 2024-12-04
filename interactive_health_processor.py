import os
from pathlib import Path
from typing import Optional, List
import pandas as pd
from datetime import datetime

# Import our health data processor
from apple_health_processor import HealthDataProcessor
from health_data_report import HealthDataReport

class InteractiveHealthProcessor:
    """Interactive command-line interface for processing Apple Health data."""

    def __init__(self):
        self.processor: Optional[HealthDataProcessor] = None
        self.output_dir: Optional[Path] = None
        self.report: Optional[HealthDataReport] = None

    def start(self):
        """Start the interactive processing session."""
        print("\n🏥 Welcome to the Apple Health Data Processor!")
        print("Let's analyze your health data export.\n")

        self._setup_processor()
        if self.processor:
            self._setup_output_directory()
            self._process_data()

    def _setup_processor(self):
        """Guide user through setting up the data processor."""
        while True:
            export_path = input("Please enter the path to your export.xml file: ").strip()

            # Handle home directory shorthand
            if export_path.startswith('~'):
                export_path = os.path.expanduser(export_path)

            path = Path(export_path)

            if not path.exists():
                print("\n❌ File not found. Please check the path and try again.")
                continue

            try:
                self.processor = HealthDataProcessor(str(path))
                print("\n✅ Successfully loaded health data export!")
                break
            except Exception as e:
                print(f"\n❌ Error loading file: {e}")
                if not self._should_continue():
                    return

    def _setup_output_directory(self):
        """Guide user through setting up the output directory."""
        while True:
            output_path = input("\nWhere would you like to save the processed data? (Enter path): ").strip()

            # Handle home directory shorthand
            if output_path.startswith('~'):
                output_path = os.path.expanduser(output_path)

            path = Path(output_path)

            try:
                path.mkdir(parents=True, exist_ok=True)
                self.output_dir = path
                print(f"\n✅ Output directory set to: {path}")
                break
            except Exception as e:
                print(f"\n❌ Error creating output directory: {e}")
                if not self._should_continue():
                    return

        if self.output_dir:
            self.report = HealthDataReport(self.output_dir)

    def _process_data(self):
        """Guide user through data processing options."""
        if not self.processor or not self.output_dir:
            return

        print("\n📊 Available health metrics:")
        record_types = self.processor.get_available_record_types()

        # ... (rest of the display logic remains same)

        processed_any = False
        while True:
            print("\nOptions:")
            print("1. Process specific health metric")
            print("2. Process all metrics")
            print("3. Process workouts")
            print("4. Exit")

            choice = input("\nWhat would you like to do? (1-4): ").strip()

            if choice == '1':
                self._process_specific_metric(record_types)
                processed_any = True
            elif choice == '2':
                self._process_all_metrics(record_types)
                # Generate and save the consolidated report
                if self.report:
                    try:
                        report_path = self.report.save_report()
                        print(f"\n📋 Consolidated report saved to: {report_path}")
                    except Exception as e:
                        print(f"\n❌ Error saving report: {e}")
            elif choice == '3':
                self._process_workouts()
                processed_any = True
            elif choice == '4':
                print("\n👋 Thank you for using the Health Data Processor!")
                break
            else:
                print("\n❌ Invalid choice. Please try again.")

    def _process_specific_metric(self, record_types: List[str]):
        """Process a specific health metric chosen by the user."""
        print("\nAvailable metrics:")
        # Create a mapping of index to original metric name for processing
        metric_mapping = {i: metric for i, metric in enumerate(record_types, 1)}

        # Display cleaned metric names
        for i, metric in metric_mapping.items():
            cleaned_name = self.report.clean_metric_name(metric)
            print(f"{i}. {cleaned_name}")

        while True:
            try:
                choice = int(input("\nEnter the number of the metric to process (0 to cancel): "))
                if choice == 0:
                    return
                if 1 <= choice <= len(record_types):
                    # Use the mapping to get the original metric name for processing
                    metric = metric_mapping[choice]
                    self._save_metric_data(metric)
                    break
                else:
                    print("\n❌ Invalid choice. Please try again.")
            except ValueError:
                print("\n❌ Please enter a valid number.")

    def _process_all_metrics(self, record_types: List[str]):
        """Process all available health metrics."""
        for metric in record_types:
            self._save_metric_data(metric)
        print("\n✅ All metrics processed successfully!")

    def _process_workouts(self):
            """Process workout data."""
            try:
                df = self.processor.process_workouts()
                output_path = self.output_dir / "workouts.csv"
                df.to_csv(output_path, index=False)

                # Add to report
                if self.report:
                    self.report.add_dataset_summary("Workouts", df, output_path)

                print(f"\n✅ Workout data saved to: {output_path}")
            except Exception as e:
                print(f"\n❌ Error processing workouts: {e}")

    def _save_metric_data(self, metric: str):
        """Save data for a specific metric to CSV."""
        try:
            df = self.processor.parse_records_by_type(metric)

            # Create a safe filename with cleaned metric name
            clean_name = self.report.clean_metric_name(metric).split(' (')[0]  # Remove type indicator for filename
            safe_filename = f"{clean_name}.csv"
            output_path = self.output_dir / safe_filename

            df.to_csv(output_path, index=False)

            # Add to report
            if self.report:
                self.report.add_dataset_summary(metric, df, output_path)

            print(f"\n✅ Saved {clean_name} data to: {output_path}")
        except Exception as e:
            print(f"\n❌ Error processing {metric}: {e}")

    def _should_continue(self) -> bool:
        """Ask user if they want to try again."""
        response = input("\nWould you like to try again? (y/n): ").strip().lower()
        return response == 'y'

if __name__ == "__main__":
    processor = InteractiveHealthProcessor()
    processor.start()
