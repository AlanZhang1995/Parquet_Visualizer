# Project Structure

Clean and organized structure of the Parquet Visualizer project.

## Directory Tree

```
parquet-visualizer/
├── README.md                   # Project overview and quick start
├── CHANGELOG.md                # Version history
├── SETUP.md                    # Detailed setup instructions
├── QUICK_START.md              # 30-second start guide
├── PROJECT_STRUCTURE.md        # This file
├── LICENSE                     # MIT License
│
├── app.py                      # Main Streamlit application
├── start.sh                    # Startup script
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Test configuration
│
├── .streamlit/                 # Streamlit configuration
│   └── config.toml            # Upload limits, etc.
│
├── src/                        # Source code
│   ├── __init__.py
│   ├── parquet_service.py     # Parquet file operations
│   └── image_service.py       # Image handling
│
├── tests/                      # Test files
│   ├── __init__.py
│   ├── test_parquet_service.py    # Unit tests (13 tests)
│   ├── test_image_service.py      # Image tests (9 tests)
│   ├── test_large_files.py        # Large file tests (6 tests)
│   ├── property_tests.py          # Property-based tests (5 tests)
│   ├── test_catalog.py            # Catalog file test
│   ├── test_dict_image_format.py  # Dictionary format test
│   ├── test_image_display_fix.py  # Display fix test
│   └── test_image_viewer_fix.py   # Viewer fix test
│
├── sample_data/                # Sample Parquet files
│   ├── sample1_simple.parquet
│   ├── sample2_with_nulls.parquet
│   ├── sample3_large.parquet
│   ├── sample4_mixed_types.parquet
│   ├── sample_with_images.parquet
│   └── catalog.parquet         # 13GB, 213M rows
│
├── docs/                       # Documentation
│   ├── README.md              # Documentation index
│   ├── guides/                # User guides
│   │   ├── LARGE_FILES_GUIDE.md
│   │   ├── IMAGE_VISUALIZATION_GUIDE.md
│   │   └── CATALOG_QUICKSTART.md
│   └── archive/               # Historical documentation
│       ├── COMPLETE_CHANGELOG.md
│       ├── COMPLETION_REPORT.md
│       ├── IMPLEMENTATION_SUMMARY.md
│       └── ... (various fix docs)
│
├── .kiro/                      # Kiro spec files
│   └── specs/parquet-visualizer/
│       ├── requirements.md
│       ├── design.md
│       └── tasks.md
│
├── create_sample_data.py       # Generate sample files
├── create_image_sample.py      # Generate image samples
│
└── venv/                       # Virtual environment (gitignored)
```

## File Descriptions

### Root Files

| File | Purpose |
|------|---------|
| `README.md` | Project overview, features, quick start |
| `CHANGELOG.md` | Version history and changes |
| `SETUP.md` | Detailed setup and configuration |
| `QUICK_START.md` | 30-second start guide |
| `PROJECT_STRUCTURE.md` | This file - project organization |
| `app.py` | Main Streamlit application (~600 lines) |
| `start.sh` | One-command startup script |
| `requirements.txt` | Python dependencies |
| `pytest.ini` | Test configuration |

### Source Code (`src/`)

| File | Purpose | Lines |
|------|---------|-------|
| `parquet_service.py` | Parquet file operations | ~450 |
| `image_service.py` | Image extraction and handling | ~80 |

### Tests (`tests/`)

| File | Tests | Coverage |
|------|-------|----------|
| `test_parquet_service.py` | 13 | Core functionality |
| `test_image_service.py` | 9 | Image operations |
| `test_large_files.py` | 6 | Large file handling |
| `property_tests.py` | 5 | Property-based (400+ iterations) |
| **Total** | **28** | **90%** |

### Documentation (`docs/`)

#### Guides (`docs/guides/`)
- `LARGE_FILES_GUIDE.md` - Handling files > 100K rows
- `IMAGE_VISUALIZATION_GUIDE.md` - Image features
- `CATALOG_QUICKSTART.md` - Using the 13GB sample

#### Archive (`docs/archive/`)
- Historical documentation from development
- Fix details and implementation notes
- Kept for reference, not needed for normal use

### Sample Data (`sample_data/`)

| File | Rows | Size | Purpose |
|------|------|------|---------|
| `sample1_simple.parquet` | 100 | ~5 KB | Basic testing |
| `sample2_with_nulls.parquet` | 50 | ~3 KB | Null handling |
| `sample3_large.parquet` | 1,000 | ~50 KB | Pagination |
| `sample4_mixed_types.parquet` | 50 | ~4 KB | Type handling |
| `sample_with_images.parquet` | 20 | ~7 KB | Image testing |
| `catalog.parquet` | 213M | 13 GB | Large file testing |

## Key Features by File

### `app.py`
- File upload and local file browser
- Data table with pagination
- Image gallery and preview
- Search functionality
- Schema display
- Statistics view

### `parquet_service.py`
- Parse Parquet files
- Efficient row group reading
- Smart sampling (10K rows)
- Search and filter
- Column statistics
- Sorting

### `image_service.py`
- Extract images from bytes
- Detect image format
- Create thumbnails
- Handle dictionary format

## Configuration

### `.streamlit/config.toml`
```toml
[server]
maxUploadSize = 20000  # 20GB
maxMessageSize = 2000

[browser]
gatherUsageStats = false
```

### `pytest.ini`
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

## Ignored Files (`.gitignore`)

- `venv/` - Virtual environment
- `__pycache__/` - Python cache
- `.pytest_cache/` - Test cache
- `.hypothesis/` - Hypothesis cache
- `htmlcov/` - Coverage reports
- `*.pyc` - Compiled Python
- `.DS_Store` - macOS files
- Test scripts in root

## Quick Navigation

### For Users
1. Start here: `README.md`
2. Setup: `SETUP.md` or `QUICK_START.md`
3. Guides: `docs/guides/`
4. Changes: `CHANGELOG.md`

### For Developers
1. Code: `src/` and `app.py`
2. Tests: `tests/`
3. Specs: `.kiro/specs/`
4. History: `docs/archive/`

### For Contributors
1. Read: `README.md` and `SETUP.md`
2. Check: `CHANGELOG.md`
3. Test: `pytest`
4. Document: Add to `docs/guides/`

## Statistics

- **Total Lines of Code**: ~1,200
- **Test Coverage**: 90%
- **Documentation Files**: 15+
- **Sample Files**: 6
- **Supported File Size**: Up to 20GB (upload) or unlimited (local)
- **Tested with**: 213M rows, 13GB file

## Clean and Organized! ✨

All documentation is now properly organized:
- Essential docs in root
- User guides in `docs/guides/`
- Historical docs in `docs/archive/`
- Tests in `tests/`
- Source in `src/`

Easy to navigate and maintain!
