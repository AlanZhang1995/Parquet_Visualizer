"""
ImageService - Service for handling image data in Parquet files

This service extracts and processes image data from Parquet columns,
supporting both embedded binary images and file path references.
"""

import io
from typing import Optional, Tuple
from PIL import Image
import base64


class ImageService:
    """Service for handling image operations"""
    
    def extract_image(self, image_data: bytes) -> Optional[Image.Image]:
        """
        Extract image from binary data
        
        Args:
            image_data: Binary image data
            
        Returns:
            PIL Image object or None if extraction fails
        """
        try:
            return Image.open(io.BytesIO(image_data))
        except Exception as e:
            print(f"Error extracting image: {e}")
            return None
    
    def detect_image_format(self, image_data: bytes) -> str:
        """
        Detect image format from binary data
        
        Args:
            image_data: Binary image data
            
        Returns:
            Image format string (PNG, JPEG, WEBP, etc.) or UNKNOWN
        """
        try:
            img = Image.open(io.BytesIO(image_data))
            return img.format or "UNKNOWN"
        except:
            return "UNKNOWN"
    
    def load_image_from_path(self, image_path: str) -> Optional[Image.Image]:
        """
        Load image from file path
        
        Args:
            image_path: Path to image file
            
        Returns:
            PIL Image object or None if loading fails
        """
        try:
            return Image.open(image_path)
        except Exception as e:
            print(f"Error loading image from path: {e}")
            return None
    
    def image_to_base64(self, image: Image.Image) -> str:
        """
        Convert PIL Image to base64 string
        
        Args:
            image: PIL Image object
            
        Returns:
            Base64 encoded string
        """
        buffer = io.BytesIO()
        image.save(buffer, format=image.format or 'PNG')
        return base64.b64encode(buffer.getvalue()).decode()
    
    def create_thumbnail(
        self,
        image: Image.Image,
        size: Tuple[int, int] = (100, 100)
    ) -> Image.Image:
        """
        Create a thumbnail of the image
        
        Args:
            image: PIL Image object
            size: Thumbnail size (width, height)
            
        Returns:
            Thumbnail image
        """
        thumbnail = image.copy()
        thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
        return thumbnail
