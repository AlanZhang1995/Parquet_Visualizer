"""
ParquetService - Service for parsing and reading Parquet files

This service uses pyarrow to parse Parquet files and extract schema,
metadata, and data. It supports various compression formats including
SNAPPY, GZIP, and LZ4.
"""

import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import pyarrow.parquet as pq
import pandas as pd


@dataclass
class ColumnSchema:
    """Schema information for a single column"""
    name: str
    type: str
    nullable: bool
    is_image_column: bool


@dataclass
class FileMetadata:
    """Metadata for a Parquet file"""
    file_name: str
    file_size: int
    row_count: int
    column_count: int
    schema: List[ColumnSchema]
    compression: str
    metadata: Dict[str, str]


class ParquetService:
    """Service for handling Parquet file operations"""
    
    def __init__(self):
        self._file_cache: Dict[str, pq.ParquetFile] = {}
    
    def parse_file(self, file_path: str) -> Tuple[pq.ParquetFile, FileMetadata]:
        """
        Parse a Parquet file and return file handle and metadata
        
        Args:
            file_path: Path to the Parquet file
            
        Returns:
            Tuple of (ParquetFile, FileMetadata)
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not a valid Parquet file
        """
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # Open Parquet file
            parquet_file = pq.ParquetFile(file_path)
            
            # Extract schema
            schema = self._extract_schema(parquet_file)
            
            # Extract metadata
            metadata = self._extract_metadata(parquet_file)
            
            # Get file info
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            row_count = parquet_file.metadata.num_rows
            column_count = len(schema)
            
            # Get compression codec
            compression = self._get_compression(parquet_file)
            
            # Create metadata object
            file_metadata = FileMetadata(
                file_name=file_name,
                file_size=file_size,
                row_count=row_count,
                column_count=column_count,
                schema=schema,
                compression=compression,
                metadata=metadata
            )
            
            # Cache the file
            self._file_cache[file_path] = parquet_file
            
            return parquet_file, file_metadata
            
        except Exception as e:
            if "Parquet magic bytes" in str(e) or "Invalid" in str(e):
                raise ValueError(f"Invalid Parquet file format: {e}")
            raise ValueError(f"Error parsing Parquet file: {e}")
    
    def get_rows(
        self,
        parquet_file: pq.ParquetFile,
        offset: int = 0,
        limit: int = 100,
        sort_column: Optional[str] = None,
        sort_ascending: bool = True,
        sample_large_files: bool = True,
        large_file_threshold: int = 1000000  # 1 million rows
    ) -> pd.DataFrame:
        """
        Get rows from Parquet file with pagination and optional sorting
        
        For large files (> threshold rows), uses efficient row group reading
        to avoid loading entire file into memory.
        
        Args:
            parquet_file: ParquetFile object
            offset: Starting row index
            limit: Maximum number of rows to return
            sort_column: Column name to sort by (optional)
            sort_ascending: Sort direction (default: ascending)
            sample_large_files: Use sampling for very large files
            large_file_threshold: Row count threshold for sampling
            
        Returns:
            DataFrame with requested rows
        """
        total_rows = parquet_file.metadata.num_rows
        
        # For very large files, use efficient row group reading
        if total_rows > large_file_threshold and sample_large_files:
            # Read only the row groups we need
            df = self._read_row_groups_efficiently(
                parquet_file, offset, limit
            )
        else:
            # For smaller files, read entire table
            table = parquet_file.read()
            df = table.to_pandas()
            
            # Apply pagination
            end = min(offset + limit, len(df))
            df = df.iloc[offset:end]
        
        # Apply sorting if requested
        if sort_column and sort_column in df.columns:
            df = df.sort_values(by=sort_column, ascending=sort_ascending)
        
        return df
    
    def _read_row_groups_efficiently(
        self,
        parquet_file: pq.ParquetFile,
        offset: int,
        limit: int
    ) -> pd.DataFrame:
        """
        Efficiently read specific rows from large Parquet files using row groups
        
        Args:
            parquet_file: ParquetFile object
            offset: Starting row index
            limit: Maximum number of rows to return
            
        Returns:
            DataFrame with requested rows
        """
        # Find which row groups contain our target rows
        row_groups_to_read = []
        current_row = 0
        
        for i in range(parquet_file.metadata.num_row_groups):
            rg_metadata = parquet_file.metadata.row_group(i)
            rg_num_rows = rg_metadata.num_rows
            
            # Check if this row group contains rows we need
            if current_row + rg_num_rows > offset and current_row < offset + limit:
                row_groups_to_read.append(i)
            
            current_row += rg_num_rows
            
            # Stop if we've passed our target range
            if current_row >= offset + limit:
                break
        
        # Read only the necessary row groups
        if not row_groups_to_read:
            # Return empty DataFrame with correct schema
            return pd.DataFrame(columns=[field.name for field in parquet_file.schema_arrow])
        
        # Read the row groups
        tables = []
        for rg_idx in row_groups_to_read:
            table = parquet_file.read_row_group(rg_idx)
            tables.append(table)
        
        # Combine tables
        if len(tables) == 1:
            combined_table = tables[0]
        else:
            import pyarrow as pa
            combined_table = pa.concat_tables(tables)
        
        df = combined_table.to_pandas()
        
        # Calculate the offset within the combined data
        rows_before_first_group = 0
        for i in range(row_groups_to_read[0]):
            rows_before_first_group += parquet_file.metadata.row_group(i).num_rows
        
        local_offset = offset - rows_before_first_group
        local_end = local_offset + limit
        
        return df.iloc[local_offset:local_end]
    
    def get_sample_rows(
        self,
        parquet_file: pq.ParquetFile,
        sample_size: int = 10000,
        random_seed: Optional[int] = 42
    ) -> pd.DataFrame:
        """
        Get a random sample of rows from a large Parquet file
        
        This is useful for quick data inspection of very large files
        without loading everything into memory.
        
        Args:
            parquet_file: ParquetFile object
            sample_size: Number of rows to sample
            random_seed: Random seed for reproducibility
            
        Returns:
            DataFrame with sampled rows
        """
        total_rows = parquet_file.metadata.num_rows
        
        if total_rows <= sample_size:
            # File is small enough, return all rows
            return parquet_file.read().to_pandas()
        
        # Calculate sampling ratio
        sample_ratio = sample_size / total_rows
        
        # Read row groups and sample
        import numpy as np
        if random_seed is not None:
            np.random.seed(random_seed)
        
        sampled_dfs = []
        for i in range(parquet_file.metadata.num_row_groups):
            rg_metadata = parquet_file.metadata.row_group(i)
            rg_num_rows = rg_metadata.num_rows
            
            # Calculate how many rows to sample from this row group
            rg_sample_size = int(rg_num_rows * sample_ratio)
            
            if rg_sample_size > 0:
                # Read the row group
                table = parquet_file.read_row_group(i)
                df = table.to_pandas()
                
                # Sample rows
                if len(df) > rg_sample_size:
                    sampled_df = df.sample(n=rg_sample_size, random_state=random_seed)
                else:
                    sampled_df = df
                
                sampled_dfs.append(sampled_df)
        
        # Combine all sampled data
        if sampled_dfs:
            result = pd.concat(sampled_dfs, ignore_index=True)
            # Ensure we don't exceed sample_size
            if len(result) > sample_size:
                result = result.sample(n=sample_size, random_state=random_seed)
            return result
        else:
            # Return empty DataFrame with correct schema
            return pd.DataFrame(columns=[field.name for field in parquet_file.schema_arrow])
    
    def search_rows(
        self,
        parquet_file: pq.ParquetFile,
        search_term: str
    ) -> pd.DataFrame:
        """
        Search for rows containing the search term in any column
        
        Args:
            parquet_file: ParquetFile object
            search_term: Term to search for
            
        Returns:
            DataFrame with matching rows
        """
        table = parquet_file.read()
        df = table.to_pandas()
        
        # Convert search term to string and lowercase
        search_term = str(search_term).lower()
        
        # Search across all columns
        mask = df.astype(str).apply(
            lambda col: col.str.lower().str.contains(search_term, na=False)
        ).any(axis=1)
        
        return df[mask]
    
    def filter_rows(
        self,
        parquet_file: pq.ParquetFile,
        filters: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """
        Filter rows based on column conditions
        
        Args:
            parquet_file: ParquetFile object
            filters: List of filter conditions
                Each filter: {"column": str, "operator": str, "value": Any}
                Operators: "equals", "contains", "gt", "lt", "gte", "lte"
                
        Returns:
            DataFrame with filtered rows
        """
        table = parquet_file.read()
        df = table.to_pandas()
        
        # Apply each filter
        for filter_spec in filters:
            column = filter_spec["column"]
            operator = filter_spec["operator"]
            value = filter_spec["value"]
            
            if column not in df.columns:
                continue
            
            if operator == "equals":
                df = df[df[column] == value]
            elif operator == "contains":
                df = df[df[column].astype(str).str.contains(str(value), na=False)]
            elif operator == "gt":
                df = df[df[column] > value]
            elif operator == "lt":
                df = df[df[column] < value]
            elif operator == "gte":
                df = df[df[column] >= value]
            elif operator == "lte":
                df = df[df[column] <= value]
        
        return df
    
    def get_column_stats(
        self,
        parquet_file: pq.ParquetFile,
        column_name: str
    ) -> Dict[str, Any]:
        """
        Get statistics for a specific column
        
        Args:
            parquet_file: ParquetFile object
            column_name: Name of the column
            
        Returns:
            Dictionary with column statistics
        """
        table = parquet_file.read()
        df = table.to_pandas()
        
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found")
        
        col = df[column_name]
        stats = {
            "count": len(col),
            "null_count": col.isna().sum(),
            "unique_count": col.nunique(),
        }
        
        # Add numeric statistics if applicable
        if pd.api.types.is_numeric_dtype(col):
            stats.update({
                "min": col.min(),
                "max": col.max(),
                "mean": col.mean(),
                "median": col.median(),
            })
        
        return stats
    
    def _extract_schema(self, parquet_file: pq.ParquetFile) -> List[ColumnSchema]:
        """Extract schema information from Parquet file"""
        schema = parquet_file.schema_arrow
        columns = []
        
        for i in range(len(schema)):
            field = schema.field(i)
            field_type = str(field.type)
            
            # Determine if this is an image column
            # Check for binary types or columns with 'image', 'img', 'picture', 'photo' in name
            is_image = (
                field_type in ['binary', 'large_binary'] or
                any(keyword in field.name.lower() for keyword in ['image', 'img', 'picture', 'photo', 'thumbnail'])
            )
            
            columns.append(ColumnSchema(
                name=field.name,
                type=field_type,
                nullable=field.nullable,
                is_image_column=is_image
            ))
        
        return columns
    
    def _extract_metadata(self, parquet_file: pq.ParquetFile) -> Dict[str, str]:
        """Extract metadata from Parquet file"""
        metadata = {}
        
        # Get schema metadata
        if parquet_file.schema_arrow.metadata:
            for key, value in parquet_file.schema_arrow.metadata.items():
                metadata[key.decode('utf-8')] = value.decode('utf-8')
        
        return metadata
    
    def _get_compression(self, parquet_file: pq.ParquetFile) -> str:
        """Get compression codec from Parquet file"""
        try:
            # Get compression from first row group
            if parquet_file.metadata.num_row_groups > 0:
                row_group = parquet_file.metadata.row_group(0)
                if row_group.num_columns > 0:
                    column = row_group.column(0)
                    return column.compression
            return "UNCOMPRESSED"
        except:
            return "UNKNOWN"
    
    def close_file(self, file_path: str):
        """Close and remove file from cache"""
        if file_path in self._file_cache:
            del self._file_cache[file_path]
