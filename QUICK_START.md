# Parquet Visualizer - Quick Start Guide

## 🚀 Get Started in 30 Seconds

### Step 1: Start the Application
```bash
./start.sh
```

That's it! The application will:
- ✅ Create a virtual environment
- ✅ Install all dependencies
- ✅ Start the web server
- ✅ Open your browser automatically

### Step 2: Upload a File

1. Click the **"Choose a Parquet file"** button in the sidebar
2. Select a Parquet file from your computer
3. Or use one of the sample files in `sample_data/`

### Step 3: Explore Your Data

**📊 Data View Tab**
- Browse your data in an interactive table
- Use the search box to find specific values
- Sort by clicking column names
- Navigate pages with the slider

**📋 Schema Tab**
- View all column names and types
- Check nullability information
- See file metadata and compression

**📈 Statistics Tab**
- Select any column
- View count, unique values, null count
- See min, max, mean, median for numeric columns

## 📁 Sample Data

Try the included sample files:

```bash
# Generate sample data
source venv/bin/activate
python create_sample_data.py
```

This creates 4 sample files in `sample_data/`:
- `sample1_simple.parquet` - Simple dataset (100 rows)
- `sample2_with_nulls.parquet` - Dataset with nulls (50 rows)
- `sample3_large.parquet` - Larger dataset (1000 rows)
- `sample4_mixed_types.parquet` - Mixed data types (50 rows)

## 🧪 Run Tests

```bash
source venv/bin/activate
pytest
```

Expected output:
```
✅ 13 unit tests passed
✅ 5 property-based tests passed
✅ 93% code coverage
```

## 🎯 Key Features

### Search
Type in the search box to find rows containing your search term in any column.

### Filter
Use the filter controls to narrow down your data:
- **Equals**: Exact match
- **Contains**: Partial match
- **Greater than / Less than**: Numeric comparisons

### Sort
Click on any column name to sort:
- First click: Ascending
- Second click: Descending
- Third click: No sort

### Pagination
- Choose rows per page: 50, 100, 200, or 500
- Use the slider to navigate pages
- See total row count at the top

### Statistics
Select a column in the Statistics tab to see:
- Total count
- Null count
- Unique values
- Min, max, mean, median (for numeric columns)

## 🛠️ Troubleshooting

### Application won't start
```bash
# Check Python version (need 3.9+)
python3 --version

# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

### File upload fails
- Ensure the file is a valid Parquet file
- Check file permissions
- Try a smaller file first

### Tests fail
```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run tests with verbose output
pytest -v
```

## 📚 More Information

- **README.md** - Full documentation
- **SETUP.md** - Detailed setup guide
- **IMPLEMENTATION_SUMMARY.md** - Technical details
- **COMPLETION_REPORT.md** - Project summary

## 💡 Tips

1. **Large Files**: Use pagination and filtering for files > 100MB
2. **Search**: Search is case-insensitive and searches all columns
3. **Sorting**: Sorting works across all pages, not just the current page
4. **Statistics**: Statistics are calculated on the entire dataset
5. **Keyboard**: Use Ctrl+C in terminal to stop the server

## 🎉 That's It!

You're ready to explore your Parquet files. Enjoy! 🚀

---

**Need help?** Check the documentation files or run `pytest` to verify your installation.
