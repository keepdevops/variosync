# How to Run VARIOSYNC

## Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
pip3 install -r requirements.txt
```

Or use the setup script:
```bash
./setup.sh
```

### Step 2: Create Config File (if needed)
```bash
cp config.example.json config.json
```

Edit `config.json` and set `development_mode: true` to bypass authentication:
```json
"Authentication": {
  "development_mode": true,
  "enforce_payment": false
}
```

### Step 3: Run the Application

**Process sample time-series data:**
```bash
python3 main.py --process-file sample_data.json
```

**Process financial data:**
```bash
python3 main.py --process-file financial_sample.json --record-type financial
```

**With authentication (if Supabase is configured):**
```bash
python3 main.py --process-file sample_data.json --license-key "your-uuid-key" --required-hours 0.1
```

## What Happens When You Run It?

1. **Loads configuration** from `config.json` (or uses defaults)
2. **Validates** the data file format
3. **Processes** each record (normalizes timestamps, validates data)
4. **Saves** processed data to `data/` directory (or configured storage)
5. **Logs** all operations to `variosync.log`

## Output Locations

- **Processed data**: `data/` directory (or configured storage backend)
- **Logs**: `variosync.log` (or configured log file)
- **Console**: Real-time status messages

## Troubleshooting

**Missing dependencies:**
```bash
pip3 install requests boto3 supabase
```

**Config file not found:**
- Copy `config.example.json` to `config.json`
- Or the app will use defaults

**Authentication errors:**
- Set `development_mode: true` in config.json to bypass auth
- Or configure valid Supabase credentials

**Check logs:**
```bash
tail -f variosync.log
```

## Example Commands

```bash
# Show help
python3 main.py --help

# Process with custom config
python3 main.py --config my_config.json --process-file data.json

# Process financial data
python3 main.py --process-file stocks.json --record-type financial

# Process with authentication
python3 main.py --process-file data.json --license-key "123e4567-e89b-12d3-a456-426614174000" --required-hours 0.5
```
