import streamlit as st
import pandas as pd
from pathlib import Path
import tempfile
import os
from apple_health_processor import HealthDataProcessor
from health_data_report import HealthDataReport

class StreamlitHealthApp:
    def __init__(self):
        st.set_page_config(
            page_title="Apple Health Data Processor",
            page_icon="🏥",
            layout="wide"
        )
        self.setup_session_state()

    def setup_session_state(self):
        """Initialize session state variables"""
        if 'processor' not in st.session_state:
            st.session_state.processor = None
        if 'report' not in st.session_state:
            st.session_state.report = None
        if 'available_metrics' not in st.session_state:
            st.session_state.available_metrics = []

    def render(self):
        """Render the main app interface"""
        st.title("🏥 Apple Health Data Processor")
        st.write("Upload and process your Apple Health export data")

        # File upload section
        self.render_upload_section()

        # Only show processing options if data is loaded
        if st.session_state.processor:
            self.render_processing_section()

    def render_upload_section(self):
        """Render the file upload section"""
        with st.expander("📤 Upload Health Data", expanded=True):
            uploaded_file = st.file_uploader(
                "Upload your export.xml file",
                type=['xml'],
                help="Select the export.xml file from your Apple Health data export"
            )

            if uploaded_file:
                self.process_uploaded_file(uploaded_file)

    def process_uploaded_file(self, uploaded_file):
        """Process the uploaded health data file"""
        try:
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name

            # Initialize processor and get available metrics
            st.session_state.processor = HealthDataProcessor(tmp_path)
            st.session_state.available_metrics = st.session_state.processor.get_available_record_types()

            # Setup temporary output directory
            output_dir = Path(tempfile.mkdtemp())
            st.session_state.report = HealthDataReport(output_dir)

            st.success("✅ Health data loaded successfully!")

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

    def render_processing_section(self):
        """Render the data processing options"""
        st.header("Process Health Data")

        # Processing tabs
        tab1, tab2, tab3 = st.tabs([
            "Single Metric Processing",
            "Batch Processing",
            "Workout Data"
        ])

        # Single Metric Processing Tab
        with tab1:
            self.render_single_metric_processor()

        # Batch Processing Tab
        with tab2:
            self.render_batch_processor()

        # Workout Data Tab
        with tab3:
            self.render_workout_processor()

    def render_single_metric_processor(self):
        """Render interface for processing single metrics"""
        st.subheader("Process Individual Metrics")

        # Group metrics by category for better organization
        categories = {
            "Activity": ["StepCount", "DistanceWalkingRunning", "FlightsClimbed"],
            "Vitals": ["HeartRate", "BloodPressure", "OxygenSaturation"],
            "Body": ["BodyMass", "Height", "BodyFatPercentage"]
        }

        # Create metric selector
        selected_metric = st.selectbox(
            "Select health metric to process",
            options=st.session_state.available_metrics,
            format_func=lambda x: st.session_state.report.clean_metric_name(x)
        )

        if st.button("Process Selected Metric"):
            self.process_single_metric(selected_metric)

    def render_batch_processor(self):
        """Render interface for batch processing"""
        st.subheader("Process All Metrics")

        if st.button("Process All Health Metrics"):
            self.process_all_metrics()

    def render_workout_processor(self):
        """Render interface for processing workout data"""
        st.subheader("Process Workout Data")

        if st.button("Process Workout Records"):
            self.process_workouts()

    def process_single_metric(self, metric):
        """Process a single selected metric"""
        try:
            with st.spinner(f"Processing {st.session_state.report.clean_metric_name(metric)}..."):
                df = st.session_state.processor.parse_records_by_type(metric)

                # Create downloadable CSV
                csv = df.to_csv(index=False)
                clean_name = st.session_state.report.clean_metric_name(metric).split(' (')[0]

                st.download_button(
                    label=f"Download {clean_name} Data",
                    data=csv,
                    file_name=f"{clean_name}.csv",
                    mime="text/csv"
                )

                # Show preview
                st.write("Data Preview:")
                st.dataframe(df.head())

        except Exception as e:
            st.error(f"Error processing metric: {str(e)}")

    def process_all_metrics(self):
        """Process all available metrics"""
        try:
            with st.spinner("Processing all metrics..."):
                # Process each metric
                all_dfs = {}
                for metric in st.session_state.available_metrics:
                    df = st.session_state.processor.parse_records_by_type(metric)
                    clean_name = st.session_state.report.clean_metric_name(metric)
                    all_dfs[clean_name] = df

                # Create schedule report
                report_df = st.session_state.report.create_report()

                # Create a ZIP file containing all CSVs
                import io
                import zipfile

                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                    # Add individual metric CSVs
                    for name, df in all_dfs.items():
                        csv_buffer = io.StringIO()
                        df.to_csv(csv_buffer, index=False)
                        zip_file.writestr(f"{name.split(' (')[0]}.csv", csv_buffer.getvalue())

                    # Add schedule report
                    report_buffer = io.StringIO()
                    report_df.to_csv(report_buffer, index=False)
                    zip_file.writestr("_APPLE_HEALTH_SCHEDULE.csv", report_buffer.getvalue())

                # Provide download button for ZIP file
                st.download_button(
                    label="Download All Processed Data",
                    data=zip_buffer.getvalue(),
                    file_name="apple_health_data.zip",
                    mime="application/zip"
                )

                # Show schedule preview
                st.write("Health Data Schedule:")
                st.dataframe(report_df)

        except Exception as e:
            st.error(f"Error processing metrics: {str(e)}")

    def process_workouts(self):
        """Process workout data"""
        try:
            with st.spinner("Processing workout data..."):
                df = st.session_state.processor.process_workouts()

                # Create downloadable CSV
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download Workout Data",
                    data=csv,
                    file_name="workouts.csv",
                    mime="text/csv"
                )

                # Show preview
                st.write("Workout Data Preview:")
                st.dataframe(df.head())

        except Exception as e:
            st.error(f"Error processing workouts: {str(e)}")

if __name__ == "__main__":
    app = StreamlitHealthApp()
    app.render()
