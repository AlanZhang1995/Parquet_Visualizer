"""
Parquet Visualizer - Main Streamlit Application

A web-based application for inspecting and visualizing Parquet files locally.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from src.parquet_service import ParquetService
from src.image_service import ImageService
import traceback


# Page configuration
st.set_page_config(
    page_title="Parquet Visualizer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Increase file upload size limit to 2GB
import streamlit.web.server.server as server
server.MAX_UPLOAD_SIZE_MB = 2048

# Initialize services
@st.cache_resource
def get_services():
    return ParquetService(), ImageService()

parquet_service, image_service = get_services()

# Initialize session state
if 'current_file' not in st.session_state:
    st.session_state.current_file = None
if 'file_metadata' not in st.session_state:
    st.session_state.file_metadata = None
if 'parquet_file' not in st.session_state:
    st.session_state.parquet_file = None
if 'search_term' not in st.session_state:
    st.session_state.search_term = ""
if 'use_sample' not in st.session_state:
    st.session_state.use_sample = False
if 'sample_data' not in st.session_state:
    st.session_state.sample_data = None

def show_custom_table_with_images(df, image_columns):
    """Display a custom table with inline image rendering"""
    
    # Get non-image columns
    non_image_cols = [col for col in df.columns if col not in image_columns]
    
    # Settings
    col1, col2 = st.columns([1, 3])
    with col1:
        thumbnail_size = st.selectbox("Image size", [50, 100, 150, 200], index=1)
    with col2:
        selected_image_col = st.selectbox("Image column to display", image_columns)
    
    st.divider()
    
    # Display each row
    for idx in range(len(df)):
        row = df.iloc[idx]
        
        # Create columns: image + data
        col_img, col_data = st.columns([1, 3])
        
        with col_img:
            # Display image
            try:
                image_data = row[selected_image_col]
                
                # Handle different data formats
                image_bytes = None
                
                if image_data is None:
                    st.info("No image")
                elif isinstance(image_data, dict):
                    # Image is a dictionary with "bytes" key
                    if "bytes" in image_data:
                        image_bytes = image_data["bytes"]
                    else:
                        st.warning(f"⚠️ Dict without 'bytes' key: {list(image_data.keys())}")
                elif isinstance(image_data, str):
                    # If it's a string representation, skip it
                    st.warning("⚠️ Data converted to string")
                elif isinstance(image_data, (bytes, bytearray)):
                    # Direct bytes
                    image_bytes = image_data
                else:
                    st.warning(f"⚠️ Unexpected type: {type(image_data).__name__}")
                
                # Extract and display image if we have bytes
                if image_bytes is not None:
                    if isinstance(image_bytes, (bytes, bytearray)) and len(image_bytes) > 0:
                        image = image_service.extract_image(bytes(image_bytes))
                        if image:
                            st.image(image, width=thumbnail_size, caption=f"Row {idx}")
                        else:
                            st.warning("⚠️ Invalid image")
                    else:
                        st.info("Empty data")
                        
            except Exception as e:
                st.error(f"Error: {str(e)[:50]}")
                import traceback
                with st.expander("Show details"):
                    st.code(traceback.format_exc())
        
        with col_data:
            # Display row data as a compact table
            row_data = {}
            for col in non_image_cols:
                value = row[col]
                # Truncate long values
                if isinstance(value, dict):
                    row_data[col] = f"<dict: {{{', '.join(value.keys())}}}>"
                elif isinstance(value, (bytes, bytearray)):
                    row_data[col] = f"<binary: {len(value)} bytes>"
                elif isinstance(value, str) and len(value) > 50:
                    row_data[col] = value[:47] + "..."
                else:
                    row_data[col] = value
            
            # Display as a small dataframe
            row_df = pd.DataFrame([row_data])
            st.dataframe(row_df, use_container_width=True, hide_index=True)
        
        st.divider()



def main():
    """Main application"""
    
    st.title("📊 Parquet Visualizer")
    st.markdown("Inspect and visualize Parquet files locally")
    
    # Sidebar for file upload and controls
    with st.sidebar:
        st.header("File Selection")
        
        # File selection method
        file_method = st.radio(
            "Select method",
            ["Upload File", "Browse Local File"],
            help="For very large files (>200MB), use 'Browse Local File'"
        )
        
        file_to_load = None
        
        if file_method == "Upload File":
            # File uploader
            uploaded_file = st.file_uploader(
                "Choose a Parquet file",
                type=['parquet'],
                help="Upload a Parquet file to visualize (recommended for files < 200MB)"
            )
            
            if uploaded_file is not None:
                # Save uploaded file temporarily
                temp_path = Path(f"/tmp/{uploaded_file.name}")
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                file_to_load = str(temp_path)
        else:
            # Local file browser
            st.markdown("**Enter file path:**")
            local_path = st.text_input(
                "File path",
                value="./sample_data/catalog.parquet",
                help="Enter the full path to a local Parquet file"
            )
            
            if local_path and st.button("Load File", use_container_width=True):
                if Path(local_path).exists():
                    file_to_load = local_path
                else:
                    st.error(f"File not found: {local_path}")
        
        # Parse the file if selected
        if file_to_load and st.session_state.current_file != file_to_load:
            try:
                with st.spinner("Parsing Parquet file..."):
                    parquet_file, metadata = parquet_service.parse_file(file_to_load)
                    st.session_state.current_file = file_to_load
                    st.session_state.file_metadata = metadata
                    st.session_state.parquet_file = parquet_file
                    # Reset sample data when loading new file
                    st.session_state.sample_data = None
                    st.session_state.use_sample = False
                    st.success("✅ File loaded successfully!")
            except Exception as e:
                st.error(f"❌ Error loading file: {str(e)}")
                st.session_state.current_file = None
                return
        
        # Show file info if loaded
        if st.session_state.file_metadata:
            st.divider()
            st.header("File Information")
            metadata = st.session_state.file_metadata
            
            st.metric("Rows", f"{metadata.row_count:,}")
            st.metric("Columns", metadata.column_count)
            st.metric("File Size", f"{metadata.file_size / 1024 / 1024:.2f} MB")
            st.metric("Compression", metadata.compression)
            
            # Show warning for very large files
            if metadata.row_count > 1_000_000:
                st.warning(f"⚠️ Large file detected ({metadata.row_count:,} rows). Using efficient row group reading for better performance.")
            
            # Add sampling option for very large files
            if metadata.row_count > 100_000:
                st.divider()
                if st.button("📊 Load Random Sample", use_container_width=True):
                    st.session_state.use_sample = True
                    st.rerun()
                if st.button("📋 Load Full Data", use_container_width=True):
                    st.session_state.use_sample = False
                    st.rerun()
    
    # Main content area
    if st.session_state.parquet_file is None:
        st.info("👆 Upload a Parquet file to get started")
        
        # Show example
        st.markdown("### Features")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**📊 Data Browsing**")
            st.markdown("View data in an interactive table with virtual scrolling")
        with col2:
            st.markdown("**🔍 Search & Filter**")
            st.markdown("Search across all columns and apply filters")
        with col3:
            st.markdown("**📈 Statistics**")
            st.markdown("View column statistics and sort data")
        
        return
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Data View", "🖼️ Image Gallery", "📋 Schema", "📈 Statistics"])
    
    with tab1:
        show_data_view()
    
    with tab2:
        show_image_gallery()
    
    with tab3:
        show_schema_view()
    
    with tab4:
        show_statistics_view()


def show_image_gallery():
    """Show image gallery view for image columns"""
    
    st.header("Image Gallery")
    
    # Check for image columns
    image_columns = [col.name for col in st.session_state.file_metadata.schema if col.is_image_column]
    
    if not image_columns:
        st.info("📋 No image columns detected in this file.")
        st.markdown("""
        Image columns are detected when:
        - Column type is `binary` or `large_binary`
        - Column name contains: 'image', 'img', 'picture', 'photo', or 'thumbnail'
        """)
        return
    
    st.success(f"🖼️ Found {len(image_columns)} image column(s): {', '.join(image_columns)}")
    
    # Column selector
    selected_column = st.selectbox(
        "Select image column to display",
        image_columns
    )
    
    # Gallery settings
    col1, col2, col3 = st.columns(3)
    
    with col1:
        images_per_page = st.selectbox("Images per page", [6, 12, 24, 48], index=1)
    
    with col2:
        columns_per_row = st.selectbox("Columns per row", [2, 3, 4, 6], index=1)
    
    # Load data
    try:
        # Use sample if active, otherwise load page
        if st.session_state.use_sample and st.session_state.sample_data is not None:
            df = st.session_state.sample_data
            total_images = len(df)
        else:
            # Load a page of data
            total_rows = st.session_state.file_metadata.row_count
            max_images = min(total_rows, 1000)  # Limit to 1000 images for performance
            
            df = parquet_service.get_rows(
                st.session_state.parquet_file,
                offset=0,
                limit=max_images
            )
            total_images = len(df)
        
        with col3:
            st.metric("Total Images", total_images)
        
        # Pagination
        max_page = max(0, (total_images - 1) // images_per_page)
        page = st.slider("Page", 0, max_page, 0, key="gallery_page")
        
        # Get images for current page
        start_idx = page * images_per_page
        end_idx = min(start_idx + images_per_page, total_images)
        page_df = df.iloc[start_idx:end_idx].reset_index(drop=False)
        
        st.divider()
        
        # Display images in grid
        if len(page_df) > 0:
            # Create grid
            rows = (len(page_df) + columns_per_row - 1) // columns_per_row
            
            for row in range(rows):
                cols = st.columns(columns_per_row)
                
                for col_idx in range(columns_per_row):
                    img_idx = row * columns_per_row + col_idx
                    
                    if img_idx < len(page_df):
                        with cols[col_idx]:
                            try:
                                image_data = page_df.iloc[img_idx][selected_column]
                                original_index = page_df.iloc[img_idx].get('index', start_idx + img_idx)
                                
                                # Handle different data formats
                                image_bytes = None
                                data_size = 0
                                
                                if image_data is None:
                                    st.info("No image")
                                elif isinstance(image_data, dict):
                                    # Image is a dictionary with "bytes" key
                                    if "bytes" in image_data:
                                        image_bytes = image_data["bytes"]
                                        data_size = len(image_bytes) if image_bytes else 0
                                    else:
                                        st.warning(f"⚠️ Dict without 'bytes' key")
                                elif isinstance(image_data, str):
                                    st.warning("⚠️ String data")
                                elif isinstance(image_data, (bytes, bytearray)):
                                    # Direct bytes
                                    image_bytes = image_data
                                    data_size = len(image_bytes)
                                else:
                                    st.warning(f"⚠️ Type: {type(image_data).__name__}")
                                
                                # Extract and display image if we have bytes
                                if image_bytes is not None and isinstance(image_bytes, (bytes, bytearray)) and len(image_bytes) > 0:
                                    image = image_service.extract_image(bytes(image_bytes))
                                    
                                    if image:
                                        st.image(
                                            image,
                                            caption=f"Row {original_index}",
                                            use_container_width=True
                                        )
                                        
                                        # Show image info in expander
                                        with st.expander("ℹ️ Info"):
                                            st.text(f"Format: {image.format or 'Unknown'}")
                                            st.text(f"Size: {image.width} x {image.height}")
                                            st.text(f"Mode: {image.mode}")
                                            st.text(f"Data size: {data_size} bytes")
                                    else:
                                        st.warning("⚠️ Could not decode")
                                    
                            except Exception as e:
                                st.error(f"Error: {str(e)[:50]}")
                                with st.expander("Show details"):
                                    st.code(traceback.format_exc())
        else:
            st.info("No images to display on this page")
            
    except Exception as e:
        st.error(f"Error loading images: {str(e)}")
        st.code(traceback.format_exc())


def show_data_view():
    """Show the main data table view"""
    
    st.header("Data View")
    
    # Show sampling info if active
    if st.session_state.use_sample:
        st.info("📊 **Sampling Mode Active** - Showing a random sample of 10,000 rows for quick inspection. Click 'Load Full Data' in the sidebar to see all rows.")
    
    # Search controls
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_term = st.text_input(
            "🔍 Search",
            value=st.session_state.search_term,
            placeholder="Search across all columns...",
            key="search_input"
        )
        st.session_state.search_term = search_term
    
    with col2:
        if st.button("Clear Search", use_container_width=True):
            st.session_state.search_term = ""
            st.rerun()
    
    # Pagination controls
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        page_size = st.selectbox("Rows per page", [50, 100, 200, 500], index=1)
    
    # Use sample data if sampling is active
    if st.session_state.use_sample:
        # Load sample data if not already loaded
        if st.session_state.sample_data is None:
            with st.spinner("Loading sample data..."):
                st.session_state.sample_data = parquet_service.get_sample_rows(
                    st.session_state.parquet_file,
                    sample_size=10000
                )
        
        total_rows = len(st.session_state.sample_data)
        display_data = st.session_state.sample_data
    else:
        total_rows = st.session_state.file_metadata.row_count
        display_data = None
    
    with col2:
        max_page = max(0, (total_rows - 1) // page_size)
        page = st.slider("Page", 0, max_page, 0)
    
    with col3:
        if st.session_state.use_sample:
            st.metric("Sample Rows", f"{total_rows:,}")
        else:
            st.metric("Total Rows", f"{total_rows:,}")
    
    # Sorting controls
    col1, col2 = st.columns(2)
    with col1:
        sort_column = st.selectbox(
            "Sort by",
            ["None"] + [col.name for col in st.session_state.file_metadata.schema]
        )
    with col2:
        sort_direction = st.radio("Direction", ["Ascending", "Descending"], horizontal=True)
    
    # Load and display data
    try:
        offset = page * page_size
        
        if st.session_state.use_sample:
            # Use pre-loaded sample data
            df = display_data
            
            # Apply sorting if requested
            if sort_column != "None" and sort_column in df.columns:
                df = df.sort_values(by=sort_column, ascending=(sort_direction == "Ascending"))
            
            # Apply search if present
            if st.session_state.search_term:
                search_lower = st.session_state.search_term.lower()
                mask = df.astype(str).apply(
                    lambda col: col.str.lower().str.contains(search_lower, na=False)
                ).any(axis=1)
                df = df[mask]
                st.info(f"🔍 Found {len(df)} matching rows in sample")
            
            # Apply pagination
            df = df.iloc[offset:offset + page_size]
        else:
            # Apply search if present
            if st.session_state.search_term:
                df = parquet_service.search_rows(
                    st.session_state.parquet_file,
                    st.session_state.search_term
                )
                st.info(f"🔍 Found {len(df)} matching rows")
                # Apply pagination to search results
                df = df.iloc[offset:offset + page_size]
            else:
                # Normal pagination with efficient row group reading
                df = parquet_service.get_rows(
                    st.session_state.parquet_file,
                    offset=offset,
                    limit=page_size,
                    sort_column=None if sort_column == "None" else sort_column,
                    sort_ascending=(sort_direction == "Ascending")
                )
        
        # Check for image columns
        image_columns = [col.name for col in st.session_state.file_metadata.schema if col.is_image_column]
        
        # Store original dataframe with bytes intact for image visualization
        df_original = df.copy()
        
        # Create display version with text representation for image columns
        if image_columns:
            df_display = df.copy()
            for col in image_columns:
                if col in df_display.columns:
                    df_display[col] = df_display[col].apply(
                        lambda x: (
                            f"<dict: {{{', '.join(x.keys())}}}>" if isinstance(x, dict) else
                            f"<binary: {len(x)} bytes>" if isinstance(x, (bytes, bytearray)) else
                            x
                        )
                    )
        else:
            df_display = df
        
        # Always show the table first
        if image_columns:
            # Add button to toggle image preview
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"🖼️ Image columns detected: {', '.join(image_columns)}")
            with col2:
                show_images = st.button("🖼️ Preview Images", use_container_width=True)
        else:
            show_images = False
        
        # Display the data table (with text representation for images)
        st.dataframe(
            df_display,
            use_container_width=True,
            height=600,
            hide_index=False
        )
        
        # Show image preview if button was clicked (using original data with bytes)
        if image_columns and show_images:
            st.divider()
            st.subheader("Image Preview")
            show_custom_table_with_images(df_original, image_columns)
            
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.code(traceback.format_exc())


def show_schema_view():
    """Show the schema information"""
    
    st.header("Schema Information")
    
    metadata = st.session_state.file_metadata
    
    # Create schema dataframe
    schema_data = []
    for col in metadata.schema:
        schema_data.append({
            "Column Name": col.name,
            "Data Type": col.type,
            "Nullable": "✓" if col.nullable else "✗",
            "Image Column": "🖼️" if col.is_image_column else ""
        })
    
    schema_df = pd.DataFrame(schema_data)
    
    st.dataframe(
        schema_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Show metadata if available
    if metadata.metadata:
        st.subheader("File Metadata")
        for key, value in metadata.metadata.items():
            st.text(f"{key}: {value}")


def show_statistics_view():
    """Show column statistics"""
    
    st.header("Column Statistics")
    
    # Column selector
    column_name = st.selectbox(
        "Select column",
        [col.name for col in st.session_state.file_metadata.schema]
    )
    
    if column_name:
        try:
            stats = parquet_service.get_column_stats(
                st.session_state.parquet_file,
                column_name
            )
            
            # Display statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Count", f"{stats['count']:,}")
            with col2:
                st.metric("Null Count", f"{stats['null_count']:,}")
            with col3:
                st.metric("Unique Values", f"{stats['unique_count']:,}")
            with col4:
                null_pct = (stats['null_count'] / stats['count'] * 100) if stats['count'] > 0 else 0
                st.metric("Null %", f"{null_pct:.1f}%")
            
            # Numeric statistics if available
            if 'min' in stats:
                st.divider()
                st.subheader("Numeric Statistics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Min", f"{stats['min']:.2f}" if isinstance(stats['min'], float) else stats['min'])
                with col2:
                    st.metric("Max", f"{stats['max']:.2f}" if isinstance(stats['max'], float) else stats['max'])
                with col3:
                    st.metric("Mean", f"{stats['mean']:.2f}")
                with col4:
                    st.metric("Median", f"{stats['median']:.2f}")
            
        except Exception as e:
            st.error(f"Error calculating statistics: {str(e)}")


if __name__ == "__main__":
    main()
