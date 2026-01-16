# VARIOSYNC Quick Start Guide

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Create configuration file:**
```bash
cp config.example.json config.json
```

3. **Edit config.json** (optional - defaults work for local testing):
   - Set `development_mode: true` in Authentication section to bypass auth
   - Or configure Supabase credentials if you have them

## Running the Application

### Basic Usage (No Authentication)

1. **Process a time-series data file:**
```bash
python main.py --process-file sample_data.json --record-type time_series
```

2. **Process a financial data file:**
```bash
python main.py --process-file financial_data.json --record-type financial
```

### With Authentication

```bash
python main.py --process-file sample_data.json --license-key "your-uuid-key" --required-hours 0.1
```

### Help

```bash
python main.py --help
```

## Example Data Files

See `sample_data.json` and `financial_sample.json` for example formats.

## Output

- Processed data is saved to the `data/` directory (or configured storage backend)
- Logs are written to `variosync.log` (or configured log file)

## Development Mode

To run without authentication/payment checks, set in `config.json`:
```json
"Authentication": {
  "development_mode": true,
  "enforce_payment": false
}
```
