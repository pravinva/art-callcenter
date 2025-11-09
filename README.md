# ART Call Center - Zerobus + GenAI Agent Framework

Real-time call center agent assistance system using Databricks Zerobus and GenAI Agent Framework.

## Overview

This project implements a complete end-to-end solution for providing AI-powered assistance to call center agents during live customer calls:

1. **Zerobus Ingestion** - Real-time streaming of call transcripts
2. **DLT Pipeline** - Enrichment with sentiment, intent, and compliance detection
3. **GenAI Agent Framework** - Intelligent agent with UC Functions as tools
4. **Streamlit Dashboard** - Live agent-facing interface

## Architecture

```
Genesys Cloud → Zerobus SDK → Delta Table → DLT Pipeline → Online Tables
                                                              ↓
                                    Streamlit App ← Model Serving ← GenAI Agent
```

## Setup

### Prerequisites

- Python 3.9+
- Databricks CLI configured (`~/.databrickscfg`)
- Access to Databricks workspace

### Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

The project uses Databricks CLI credentials from `~/.databrickscfg`:

```ini
[DEFAULT]
host = https://your-workspace.cloud.databricks.com/
token = your-token
```

## Project Structure

```
art-callcenter/
├── notebooks/          # Databricks notebooks for each phase
├── app/                # Streamlit dashboard application
├── scripts/            # Standalone Python scripts
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Implementation Phases

### Phase 1: Data Foundation
- Setup Zerobus infrastructure
- Mock data generator with 100+ call scenarios
- Zerobus ingestion pipeline

### Phase 2: Data Processing
- DLT pipeline for enrichment
- Online Tables setup

### Phase 3: AI Components
- UC Functions (agent tools)
- GenAI Agent development
- Model Serving deployment

### Phase 4: User Interface
- Streamlit dashboard
- Databricks App deployment

## Usage

See individual notebook files for detailed usage instructions.

## License

MIT

