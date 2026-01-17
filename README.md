# apple-health

Apple Health data processor and analyzer with Streamlit interface.

## Overview

A Python-based tool for processing, analyzing, and visualizing Apple Health export data. Features interactive dashboards and automated reporting capabilities.

## Features

- **Apple Health Data Processing**: Parse and process Apple Health XML exports
- **Interactive Dashboard**: Streamlit-based web interface for data exploration
- **Automated Reporting**: Generate health data reports and summaries
- **Data Visualization**: Charts and graphs for health metrics
- **Multiple Interfaces**: CLI, interactive, and web-based options

## Project Structure

```
apple-health/
├── apple_health_processor.py        # Core data processing
├── streamlit_health_processor.py    # Web dashboard
├── interactive_health_processor.py  # Interactive CLI
├── health_data_report.py           # Report generation
├── requirements.txt                # Python dependencies
└── .streamlit/                     # Streamlit configuration
```

## Installation

```bash
# Clone repository
git clone https://github.com/mitchens84/apple-health.git
cd apple-health

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Streamlit Dashboard (Recommended)

```bash
streamlit run streamlit_health_processor.py
```

### Interactive CLI

```bash
python interactive_health_processor.py
```

### Generate Report

```bash
python health_data_report.py
```

### Core Processor

```bash
python apple_health_processor.py
```

## Exporting Your Apple Health Data

1. Open the Health app on your iPhone
2. Tap your profile picture
3. Scroll down and tap "Export All Health Data"
4. Save and transfer the export.zip to your computer
5. Extract the XML file and use it with this tool

## Requirements

- Python 3.7+
- See requirements.txt for package dependencies

## License

MIT License - see [LICENSE](LICENSE) for details.

---

*Health data processing and visualization toolkit*
