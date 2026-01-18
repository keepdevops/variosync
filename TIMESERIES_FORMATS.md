# Time-Series Data Formats Support

Comprehensive guide to time-series data formats that can be supported in VARIOSYNC.

## Currently Supported Formats

### ✅ Implemented (10 formats)

1. **JSON** (.json) - Human-readable, good for APIs
2. **CSV** (.csv) - Spreadsheet compatible, universal
3. **TXT** (.txt) - Tab-delimited text file
4. **Parquet** (.parquet, .pq) - Efficient columnar format
5. **Feather** (.feather) - Fast binary format
6. **DuckDB** (.duckdb) - Embedded database format
7. **Excel XLSX** (.xlsx) - Microsoft Excel format
8. **Excel XLS** (.xls) - Legacy Excel format
9. **HDF5** (.h5) - Scientific data format
10. **Apache Arrow** (.arrow) - Columnar in-memory format

---

## Additional Formats That Can Be Supported

### High Priority (Commonly Used)

#### 1. **JSONL / NDJSON** (.jsonl, .ndjson)
- **Description**: JSON Lines - one JSON object per line
- **Use Case**: Streaming data, large datasets, log files
- **Pros**: Streaming-friendly, easy to parse line-by-line, good for large files
- **Cons**: Less efficient than binary formats
- **Library**: Native Python (json module)
- **Difficulty**: Easy ⭐

#### 2. **Apache Avro** (.avro)
- **Description**: Schema-based binary format with schema evolution
- **Use Case**: Kafka streams, schema evolution, data pipelines
- **Pros**: Schema evolution, good compression, efficient serialization
- **Cons**: Requires schema definition, less human-readable
- **Library**: `fastavro` or `avro-python3`
- **Difficulty**: Medium ⭐⭐

#### 3. **Apache ORC** (.orc)
- **Description**: Optimized Row Columnar format (Hadoop ecosystem)
- **Use Case**: Big data analytics, Hive/Spark integratio
- **Pros**: Excellent compression, predicate pushdown, good for analytics
- **Cons**: Less common than Parquet, Hadoop ecosystem dependency
- **Library**: `pyarrow` (supports ORC)
- **Difficulty**: Medium ⭐⭐

#### 4. **Protocol Buffers** (.pb, .protobuf)
- **Description**: Google's binary serialization format
- **Use Case**: Remote write endpoints, efficient network transport, gRPC
- **Pros**: Very compact, fast, schema-based
- **Cons**: Requires .proto schema files, less flexible
- **Library**: `protobuf`
- **Difficulty**: Medium ⭐⭐

#### 5. **MessagePack** (.msgpack, .mp)
- **Description**: Binary JSON-like format
- **Use Case**: Efficient JSON alternative, network protocols
- **Pros**: Smaller than JSON, faster parsing, JSON-compatible
- **Cons**: Less human-readable than JSON
- **Library**: `msgpack`
- **Difficulty**: Easy ⭐

---

### TSDB-Specific Formats

#### 6. **InfluxDB Line Protocol** (.line, .lp)
- **Description**: Text-based format for InfluxDB ingestion
- **Format**: `measurement,tag1=value1 field1=value1,field2=value2 timestamp`
- **Use Case**: Direct InfluxDB integration, time-series ingestion
- **Pros**: Human-readable, efficient for time-series, widely supported
- **Cons**: Text-based (larger than binary), InfluxDB-specific
- **Library**: Native Python or `influxdb-client`
- **Difficulty**: Easy ⭐

#### 7. **OpenTSDB Format** (.tsdb)
- **Description**: Text-based format for OpenTSDB
- **Format**: `metric timestamp value tag1=value1 tag2=value2`
- **Use Case**: OpenTSDB integration, monitoring data
- **Pros**: Simple, human-readable
- **Cons**: Less efficient, OpenTSDB-specific
- **Library**: Native Python
- **Difficulty**: Easy ⭐

#### 8. **Prometheus Remote Write Format** (.prom)
- **Description**: Protocol Buffers format for Prometheus remote write
- **Use Case**: Prometheus integration, monitoring data export
- **Pros**: Efficient, standard Prometheus format
- **Cons**: Requires Prometheus protobuf definitions
- **Library**: `prometheus-client` or protobuf
- **Difficulty**: Medium ⭐⭐

---

### Scientific & Specialized Formats

#### 9. **NetCDF** (.nc, .netcdf, .cdf)
- **Description**: Network Common Data Form - scientific data format
- **Use Case**: Climate data, oceanography, atmospheric sciences
- **Pros**: Self-describing, supports metadata, multi-dimensional arrays
- **Cons**: Scientific focus, less common in general time-series
- **Library**: `netCDF4` or `xarray`
- **Difficulty**: Medium ⭐⭐

#### 10. **Zarr** (.zarr)
- **Description**: Chunked, compressed N-dimensional arrays
- **Use Case**: Large scientific datasets, cloud storage, parallel access
- **Pros**: Cloud-friendly, parallel I/O, good compression
- **Cons**: Less common for simple time-series
- **Library**: `zarr`
- **Difficulty**: Medium ⭐⭐

#### 11. **FITS** (.fits, .fit)
- **Description**: Flexible Image Transport System - astronomy format
- **Use Case**: Astronomical time-series data, scientific observations
- **Pros**: Rich metadata, astronomy standard
- **Cons**: Very specialized, astronomy-focused
- **Library**: `astropy` or `fitsio`
- **Difficulty**: Medium ⭐⭐

---

### Database & Storage Formats

#### 12. **SQLite** (.sqlite, .db)
- **Description**: Embedded SQL database
- **Use Case**: Local time-series storage, portable databases
- **Pros**: SQL queries, ACID transactions, portable
- **Cons**: Less optimized for time-series than specialized formats
- **Library**: `sqlite3` (built-in) or `sqlalchemy`
- **Difficulty**: Easy ⭐

#### 13. **TimescaleDB Format** (.tsdb)
- **Description**: PostgreSQL extension format (can export to CSV/JSON)
- **Use Case**: TimescaleDB integration, PostgreSQL-based time-series
- **Pros**: SQL interface, PostgreSQL ecosystem
- **Cons**: Requires PostgreSQL/TimescaleDB
- **Library**: `psycopg2` or `sqlalchemy`
- **Difficulty**: Medium ⭐⭐

#### 14. **QuestDB Format** (.qdb)
- **Description**: QuestDB's native format
- **Use Case**: QuestDB integration, high-performance time-series
- **Pros**: Fast ingestion, good compression
- **Cons**: QuestDB-specific, proprietary format
- **Library**: `questdb` Python client
- **Difficulty**: Medium ⭐⭐

---

### Compression & Archive Formats

#### 15. **Gzip** (.gz)
- **Description**: Compressed text files (CSV, JSON, TXT)
- **Use Case**: Compressed data storage, network transfer
- **Pros**: Good compression, widely supported
- **Cons**: Requires decompression before reading
- **Library**: `gzip` (built-in)
- **Difficulty**: Easy ⭐

#### 16. **Bzip2** (.bz2)
- **Description**: Better compression than gzip
- **Use Case**: Maximum compression for text files
- **Pros**: Better compression ratio than gzip
- **Cons**: Slower than gzip
- **Library**: `bz2` (built-in)
- **Difficulty**: Easy ⭐

#### 17. **Zstandard** (.zst, .zstd)
- **Description**: Modern compression algorithm
- **Use Case**: Fast compression with good ratios
- **Pros**: Fast, good compression, modern
- **Cons**: Less universal than gzip
- **Library**: `zstandard`
- **Difficulty**: Easy ⭐

---

### Specialized Time-Series Formats

#### 18. **TsFile** (.tsfile)
- **Description**: Apache IoTDB's native time-series file format
- **Use Case**: IoT data, high-frequency sensor data
- **Pros**: Optimized for time-series, good compression, schema support
- **Cons**: IoTDB-specific, less common
- **Library**: `iotdb` Python client or `tsfile`
- **Difficulty**: Hard ⭐⭐⭐

#### 19. **TDengine Format** (.td)
- **Description**: TDengine's native format
- **Use Case**: TDengine integration, IoT time-series
- **Pros**: Optimized for time-series, high performance
- **Cons**: TDengine-specific
- **Library**: `taos` Python connector
- **Difficulty**: Medium ⭐⭐

#### 20. **VictoriaMetrics Format** (.vm)
- **Description**: VictoriaMetrics storage format
- **Use Case**: VictoriaMetrics integration, Prometheus-compatible
- **Pros**: Efficient, Prometheus-compatible
- **Cons**: VictoriaMetrics-specific
- **Library**: VictoriaMetrics API client
- **Difficulty**: Medium ⭐⭐

---

## Format Comparison Matrix

| Format | Type | Compression | Human-Readable | Schema | Best For | Difficulty |
|--------|------|-------------|----------------|--------|----------|------------|
| **JSON** | Text | None | ✅ Yes | No | APIs, small datasets | ⭐ Easy |
| **JSONL** | Text | None | ✅ Yes | No | Streaming, logs | ⭐ Easy |
| **CSV** | Text | None | ✅ Yes | No | Spreadsheets, universal | ⭐ Easy |
| **Parquet** | Binary | ✅ Excellent | ❌ No | Yes | Analytics, storage | ⭐⭐ Medium |
| **Avro** | Binary | ✅ Good | ❌ No | ✅ Yes | Schema evolution | ⭐⭐ Medium |
| **ORC** | Binary | ✅ Excellent | ❌ No | Yes | Big data, Hive | ⭐⭐ Medium |
| **Arrow** | Binary | ✅ Good | ❌ No | Yes | In-memory, fast | ⭐⭐ Medium |
| **Feather** | Binary | ✅ Good | ❌ No | Yes | Fast I/O | ⭐⭐ Medium |
| **HDF5** | Binary | ✅ Good | ❌ No | Yes | Scientific data | ⭐⭐ Medium |
| **MessagePack** | Binary | ✅ Good | ❌ No | No | Efficient JSON | ⭐ Easy |
| **Protobuf** | Binary | ✅ Excellent | ❌ No | ✅ Yes | Network, gRPC | ⭐⭐ Medium |
| **InfluxDB LP** | Text | None | ✅ Yes | No | InfluxDB ingestion | ⭐ Easy |
| **NetCDF** | Binary | ✅ Good | ❌ No | ✅ Yes | Scientific, climate | ⭐⭐ Medium |
| **Zarr** | Binary | ✅ Excellent | ❌ No | Yes | Cloud, parallel I/O | ⭐⭐ Medium |
| **SQLite** | Binary | ✅ Good | ❌ No | ✅ Yes | Portable database | ⭐ Easy |

---

## Recommended Next Formats to Add

### Priority 1: Easy & High Value
1. **JSONL/NDJSON** - Simple, streaming-friendly, widely used
2. **MessagePack** - Efficient JSON alternative
3. **InfluxDB Line Protocol** - Direct TSDB integration
4. **Gzip compression** - Add compression support to existing formats

### Priority 2: Medium Value
5. **Apache Avro** - Schema evolution, Kafka integration
6. **Apache ORC** - Big data ecosystem
7. **Protocol Buffers** - Efficient network transport
8. **SQLite** - Portable database format

### Priority 3: Specialized Use Cases
9. **NetCDF** - Scientific data community
10. **Zarr** - Cloud-native, parallel I/O
11. **TsFile** - IoTDB ecosystem

---

## Implementation Notes

### Adding New Formats

1. **Add to `file_exporter.py`**:
   - Add format to `SUPPORTED_FORMATS` dict
   - Implement `export_to_<format>()` method
   - Add to `export()` method dispatcher

2. **Add to `file_loader.py`** (if reading support needed):
   - Add extension mapping in `detect_format()`
   - Implement loader in `file_formats.py`

3. **Update UI**:
   - Add format to download dialog selector
   - Add format description

### Format-Specific Considerations

- **Compression**: Some formats support compression (gzip, snappy, zstd)
- **Schema**: Schema-based formats (Avro, Protobuf) require schema definition
- **Streaming**: Line-based formats (JSONL, InfluxDB LP) support streaming
- **Metadata**: Some formats support rich metadata (NetCDF, HDF5)

---

## Format Selection Guide

### For Small Datasets (< 1GB)
- **JSON** - Human-readable, easy to debug
- **CSV** - Universal compatibility
- **JSONL** - Streaming-friendly

### For Medium Datasets (1GB - 100GB)
- **Parquet** - Best compression, analytics-friendly
- **Feather** - Fast I/O
- **Arrow** - In-memory operations

### For Large Datasets (> 100GB)
- **Parquet** - Excellent compression
- **ORC** - Hadoop ecosystem
- **Zarr** - Cloud storage, parallel I/O

### For Real-Time Streaming
- **JSONL** - Line-by-line processing
- **MessagePack** - Efficient binary
- **InfluxDB LP** - Direct TSDB ingestion

### For Scientific Data
- **NetCDF** - Climate, oceanography
- **HDF5** - General scientific
- **Zarr** - Cloud-native scientific

### For Database Integration
- **SQLite** - Portable, embedded
- **DuckDB** - Analytics-focused
- **Parquet** - Universal analytics format

---

## Dependencies Required

| Format | Required Libraries | Install Command |
|--------|-------------------|-----------------|
| JSONL | None (built-in) | - |
| Avro | `fastavro` | `pip install fastavro` |
| ORC | `pyarrow` | `pip install pyarrow` |
| Protobuf | `protobuf` | `pip install protobuf` |
| MessagePack | `msgpack` | `pip install msgpack` |
| InfluxDB LP | None (built-in) | - |
| NetCDF | `netCDF4` | `pip install netCDF4` |
| Zarr | `zarr` | `pip install zarr` |
| SQLite | None (built-in) | - |
| Gzip | None (built-in) | - |
| Bzip2 | None (built-in) | - |
| Zstandard | `zstandard` | `pip install zstandard` |

---

## Future Considerations

- **Cloud Storage Formats**: Direct integration with S3, GCS, Azure Blob
- **Streaming Formats**: Real-time format support (Kafka, Pulsar)
- **Time-Series Specific**: Native support for TSDB formats (InfluxDB, TimescaleDB)
- **Compression**: Automatic compression for all formats
- **Schema Registry**: Integration with schema registries (Confluent, etc.)

---

## References

- [Apache Parquet](https://parquet.apache.org/)
- [Apache Arrow](https://arrow.apache.org/)
- [InfluxDB Line Protocol](https://docs.influxdata.com/influxdb/v2/reference/syntax/line-protocol/)
- [NetCDF](https://www.unidata.ucar.edu/software/netcdf/)
- [Zarr Specification](https://zarr.readthedocs.io/)
- [Apache Avro](https://avro.apache.org/)
