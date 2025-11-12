"""
File upload handler
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from services.geospatial_processor import GeospatialProcessor
from config.settings import settings
import boto3

router = APIRouter()

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region
)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and process KMZ/KML file
    
    Returns:
        File ID and metadata
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    valid_extensions = ['.kmz', '.kml', '.geojson']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in valid_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported: {', '.join(valid_extensions)}"
        )
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        # Process file
        processor = GeospatialProcessor(
            s3_client=s3_client,
            bucket_name=settings.s3_bucket_geospatial
        )
        
        result = processor.process_upload(tmp_file_path, file.filename)
        
        return JSONResponse(content={
            'file_id': str(result.get('s3_key', '')),
            'file_name': result.get('file_name', ''),
            's3_key': result.get('s3_key', ''),
            'properties': result.get('properties', []),
            'exclusion_zones': result.get('exclusion_zones', []),
            'contours': result.get('contours', []),
            'message': 'File uploaded and processed successfully'
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)

