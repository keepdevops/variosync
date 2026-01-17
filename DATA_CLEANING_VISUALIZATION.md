# Data Cleaning, Editing, and Visualization Guide

VARIOSYNC now includes comprehensive data cleaning, editing, and visualization capabilities.

## Features Overview

### 1. Data Cleaning & Editing

Access the data editor from the Storage Browser by clicking the **✏️ Edit** button on any file.

#### Available Cleaning Operations

1. **Drop NA** - Remove rows with missing values
   - Options: Subset columns, drop if 'any' or 'all' columns are NA

2. **Fill NA** - Fill missing values
   - Methods: Forward fill, backward fill, mean, median, mode, or custom value
   - Can target specific columns or all columns

3. **Remove Duplicates** - Remove duplicate rows
   - Options: Keep first, last, or remove all duplicates
   - Can specify subset of columns to check

4. **Remove Outliers** - Remove statistical outliers
   - Methods: IQR (Interquartile Range) or Z-score
   - Configurable threshold for Z-score method

5. **Normalize Timestamps** - Standardize timestamp formats
   - Automatically converts to datetime and sorts chronologically

6. **Filter Rows** - Filter data based on conditions
   - Example: `column > 100` or `column == 'value'`

7. **Rename Columns** - Rename column names
   - JSON mapping format: `{"old_name": "new_name"}`

8. **Drop Columns** - Remove unwanted columns
   - List columns one per line

9. **Add Column** - Add new calculated columns
   - Supports expressions like `col1 + col2` or constant values

10. **Convert Type** - Change column data types
    - Types: float, int, datetime, string

11. **Resample** - Resample time-series data
    - Frequencies: 1H, 1D, 1W, etc.
    - Aggregation methods: mean, sum, max, min, first, last

12. **Interpolate** - Fill missing values using interpolation
    - Methods: linear, polynomial, spline

13. **Clip Values** - Limit values to a range
    - Set min and max bounds

14. **Round Values** - Round numeric values
    - Specify decimal places and target columns

#### Workflow

1. **View Data Summary** - Expand the "Data Summary" section to see:
   - Total rows and columns
   - Missing values per column
   - Data types
   - Duplicate count

2. **Add Operations** - Click "➕ Add Operation" to add cleaning steps
   - Configure each operation's parameters
   - Operations are applied in sequence

3. **Preview Changes** - Click "🔍 Preview" to see results
   - Shows before/after row counts
   - Displays preview table with first 20 rows

4. **Save Cleaned Data** - Click "💾 Save Cleaned Data" to save
   - Creates a new file with `_cleaned` suffix
   - Original file remains unchanged

### 2. Data Visualization

Access the visualizer from the Storage Browser by clicking the **📊 Visualize** button on any file.

#### Chart Types

1. **Line Chart** - Time-series line plots
   - Multiple series support
   - Markers and lines

2. **Scatter Plot** - Scatter point visualization
   - Good for correlation analysis

3. **Bar Chart** - Categorical comparisons
   - Vertical bars for each category

4. **Area Chart** - Filled area under line
   - Shows cumulative values

5. **Heatmap** - Correlation matrix visualization
   - Requires multiple numeric columns
   - Color-coded correlation values

6. **Histogram** - Distribution visualization
   - Shows frequency distribution

7. **Box Plot** - Statistical distribution
   - Shows quartiles, median, outliers

8. **Violin Plot** - Enhanced distribution view
   - Combines box plot with density

9. **Candlestick** - Financial OHLC charts
   - Requires: open, high, low, close columns

#### Visualization Options

- **X Axis** - Select column for X-axis (typically timestamp)
- **Y Axis** - Select one or more columns for Y-axis
- **Chart Title** - Customize chart title
- **Dimensions** - Set width and height
- **Legend** - Show/hide legend
- **Grid** - Show/hide grid lines

#### Workflow

1. **Select Chart Type** - Choose from 9 chart types
2. **Configure Axes** - Select X and Y axis columns
3. **Customize Options** - Set title, size, legend, grid
4. **Update Plot** - Click "🔄 Update Plot" to refresh
5. **Interactive Exploration** - Use Plotly's built-in zoom, pan, hover

### 3. Data Summary & Statistics

The data editor automatically provides:

- **Row/Column Counts** - Total dimensions
- **Missing Values** - Count and percentage per column
- **Data Types** - Type information for each column
- **Duplicate Detection** - Number of duplicate rows
- **Numeric Statistics** - Mean, median, std, min, max, quartiles
- **Datetime Statistics** - Range and span for date columns

## Usage Examples

### Example 1: Clean Financial Data

1. Load financial data file
2. Click **✏️ Edit**
3. Add operations:
   - Remove duplicates
   - Fill NA with forward fill
   - Remove outliers (IQR method)
   - Round values to 2 decimals
4. Preview and save

### Example 2: Visualize Time-Series

1. Load time-series data
2. Click **📊 Visualize**
3. Select:
   - Chart Type: Line
   - X Axis: timestamp
   - Y Axis: temperature, humidity (multiple)
4. Customize title and options
5. Update plot

### Example 3: Resample Data

1. Load high-frequency data
2. Click **✏️ Edit**
3. Add operation:
   - Resample: 1H frequency, mean aggregation
4. Preview and save

## Technical Details

### Data Cleaning Module (`data_cleaner.py`)

- **DataCleaner Class** - Main cleaning operations
- **clean_dataframe()** - Apply operations to DataFrame
- **get_data_summary()** - Generate statistics

### Supported Data Formats

All operations work with any format that can be loaded by FileLoader:
- JSON, JSONL, CSV, TXT
- Parquet, Feather, DuckDB
- XLSX, XLS, HDF5
- Arrow, Avro, ORC, MessagePack, SQLite

### Performance Considerations

- **Large Files** - Operations process data in-memory
- **Preview** - Shows first 20 rows for quick review
- **Save** - Creates new file, preserves original
- **Memory** - Consider file size when applying multiple operations

## Best Practices

1. **Always Preview** - Review changes before saving
2. **Keep Originals** - Cleaned files are saved with new names
3. **Operation Order** - Order matters (e.g., fill NA before removing outliers)
4. **Data Types** - Ensure correct types before operations
5. **Backup** - Export originals before major cleaning

## Integration with Other Features

- **Download** - Export cleaned data in any supported format
- **API Download** - Clean data downloaded from APIs
- **Storage Browser** - All files accessible for editing/visualization
- **File Upload** - Clean uploaded files before processing

## Future Enhancements

- Undo/redo for operations
- Operation templates/presets
- Batch processing multiple files
- Advanced statistical operations
- Custom Python expressions
- Export cleaning scripts
- Real-time preview updates
- Operation history tracking
