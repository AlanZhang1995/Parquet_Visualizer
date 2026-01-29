# Parquet Visualizer 📊

A Python-based web application for local inspection and visualization of Parquet files on macOS.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Tests](https://img.shields.io/badge/tests-18%20passed-brightgreen.svg)
![Coverage](https://img.shields.io/badge/coverage-93%25-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

- 📊 **Interactive Data Browsing** - Browse Parquet data in a responsive table with virtual scrolling
- 🔍 **Search & Filter** - Full-text search across all columns with advanced filtering
- 📈 **Column Statistics** - View detailed statistics including min, max, mean, median
- 🎯 **Quick Inspection** - Fast loading and navigation for files of any size
- 📋 **Schema Display** - Complete schema information with types and nullability
- 🖼️ **Inline Image Display** - View images directly alongside data (like HuggingFace Dataset Viewer)
- 💾 **Compression Support** - Handle SNAPPY, GZIP, LZ4, and uncompressed files
- ⚡ **High Performance** - Built on pyarrow for maximum speed
- 🚀 **Large File Support** - Handle files up to 2GB with efficient row group reading
- 📊 **Smart Sampling** - Instantly inspect large files with 10K row samples

## 🚀 Quick Start

### One-Command Installation

```bash
./start.sh
```

This script will:
1. Create a virtual environment
2. Install all dependencies
3. Start the application
4. Open your browser automatically

### Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

The application will open at http://localhost:8501

## 📖 Usage

### 1. Upload a Parquet File

- Click the file uploader in the sidebar
- Or drag and drop a Parquet file (up to 2GB)
- Try the sample files in `sample_data/`

### 2. Explore Your Data

**Data View Tab:**
- Browse data with pagination (50, 100, 200, 500 rows per page)
- **NEW: Inline Image Display** - Toggle "Table with Images" mode to see images alongside data
- Choose image column and thumbnail size (50-200px)
- Search across all columns
- Sort by any column (ascending/descending)
- Navigate pages with the slider

**Schema Tab:**
- View complete column schema
- See data types and nullability
- Check file metadata and compression

**Statistics Tab:**
- Select any column
- View count, unique values, null count
- See numeric statistics (min, max, mean, median)

### 3. Create Sample Data

```bash
source venv/bin/activate
python create_sample_data.py
```

This creates 4 sample Parquet files:
- `sample1_simple.parquet` - Simple dataset (100 rows)
- `sample2_with_nulls.parquet` - Dataset with nulls (50 rows)
- `sample3_large.parquet` - Larger dataset (1000 rows)
- `sample4_mixed_types.parquet` - Mixed data types (50 rows)

### 4. Working with Large Files

For files with **> 100,000 rows**, you'll see sampling options:
- **📊 Load Random Sample** - Instantly load 10,000 random rows
- **📋 Load Full Data** - Use efficient pagination for all rows

For files with **> 1 million rows**, the app automatically uses efficient row group reading to avoid loading the entire file into memory.

See [LARGE_FILES_GUIDE.md](LARGE_FILES_GUIDE.md) for detailed information.

## 🧪 Testing

### Run All Tests

```bash
source venv/bin/activate
pytest
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
```

### Run Specific Tests

```bash
# Unit tests only
pytest tests/test_parquet_service.py -v

# Property-based tests only
pytest tests/property_tests.py -v

# Specific test
pytest tests/test_parquet_service.py::TestParquetService::test_parse_file_success
```

### Test Results

```
✅ 19 unit tests - PASSED (including 6 large file tests)
✅ 5 property-based tests - PASSED (400+ iterations)
✅ 69% code coverage on ParquetService (with large file handling)
```

## 📁 Project Structure

```
parquet-visualizer/
├── app.py                      # Main Streamlit application
├── src/
│   ├── __init__.py
│   ├── parquet_service.py      # Parquet file parsing service
│   └── image_service.py        # Image extraction service
├── tests/
│   ├── __init__.py
│   ├── test_parquet_service.py # Unit tests (13 tests)
│   └── property_tests.py       # Property-based tests (5 tests)
├── sample_data/                # Sample Parquet files
│   ├── sample1_simple.parquet
│   ├── sample2_with_nulls.parquet
│   ├── sample3_large.parquet
│   └── sample4_mixed_types.parquet
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Pytest configuration
├── start.sh                    # Startup script
├── create_sample_data.py       # Generate sample files
├── README.md                   # This file
├── SETUP.md                    # Detailed setup guide
├── IMPLEMENTATION_SUMMARY.md   # Implementation details
└── .gitignore                  # Git ignore rules
```

## 🛠️ Technology Stack

### Core Libraries
- **pyarrow** (21.0.0) - High-performance Parquet file reading
- **pandas** (2.3.3) - Data manipulation and analysis
- **streamlit** (1.50.0) - Interactive web UI framework

### Image Processing
- **Pillow** (11.3.0) - Image handling and processing

### Testing
- **pytest** (8.4.2) - Testing framework
- **pytest-cov** (7.0.0) - Coverage reporting
- **hypothesis** (6.141.1) - Property-based testing

### Development
- **black** (25.11.0) - Code formatting
- **flake8** (7.3.0) - Linting
- **mypy** (1.19.1) - Type checking

## 📋 Requirements Satisfied

All 10 requirements from the specification:

✅ **File Loading and Parsing** - Parse Parquet files with error handling  
✅ **Table View Display** - Interactive table with pagination  
✅ **Image Visualization** - Detect and display images  
✅ **Schema Information** - Complete schema display  
✅ **Data Filtering and Search** - Full-text search and filters  
✅ **Column Operations** - Statistics, sorting, visibility  
✅ **Web Application** - Runs locally in browser  
✅ **Performance** - Fast loading and responsive UI  
✅ **Error Handling** - Clear error messages  
✅ **User Interface** - Clean, intuitive design  

## 🎯 Property-Based Tests

5 comprehensive property-based tests validate correctness:

1. **Parquet File Parsing Completeness** (100 iterations)
2. **Paginated Data Retrieval** (100 iterations)
3. **Search Result Accuracy** (50 iterations)
4. **Column Statistics Accuracy** (50 iterations)
5. **Sort Order Correctness** (50 iterations)

## 🚀 Performance

- **Startup**: < 2 seconds
- **File Loading**: Instant for files < 100MB
- **Search**: Fast full-text search
- **Pagination**: Smooth scrolling
- **Memory**: Efficient with pyarrow

## 📚 Documentation

- **README.md** - This file (quick start and overview)
- **CHANGELOG.md** - Version history and changes
- **SETUP.md** - Detailed setup and configuration
- **QUICK_START.md** - 30-second start guide
- **docs/guides/** - User guides:
  - `LARGE_FILES_GUIDE.md` - Handling large Parquet files
  - `IMAGE_VISUALIZATION_GUIDE.md` - Image features
  - `CATALOG_QUICKSTART.md` - Guide for catalog.parquet
- **docs/archive/** - Historical documentation
- **.kiro/specs/parquet-visualizer/** - Original specification

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Apache Arrow](https://arrow.apache.org/)
- Tested with [Hypothesis](https://hypothesis.readthedocs.io/)

## 📞 Support

For issues or questions:
- Check the [SETUP.md](SETUP.md) guide
- Review [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- Check test files for usage examples

---

**Made with ❤️ for data engineers and scientists**
