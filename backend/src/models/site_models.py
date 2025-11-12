"""
Database models for site layout optimizer
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from datetime import datetime
import uuid

Base = declarative_base()


class Property(Base):
    """Property boundaries and metadata"""
    __tablename__ = 'properties'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    boundary = Column(Geometry('POLYGON', srid=4326), nullable=False)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ExclusionZone(Base):
    """Exclusion zones and constraints"""
    __tablename__ = 'exclusion_zones'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey('properties.id'), nullable=False)
    zone_type = Column(String(100))  # environmental, regulatory, user_defined
    geometry = Column(Geometry('POLYGON', srid=4326), nullable=False)
    buffer_distance = Column(Float, default=100.0)
    attributes = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class Asset(Base):
    """Placed assets"""
    __tablename__ = 'assets'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    layout_id = Column(UUID(as_uuid=True), ForeignKey('layouts.id'), nullable=False)
    asset_type = Column(String(100), nullable=False)
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    dimensions = Column(JSON)
    attributes = Column(JSON)
    placement_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Road(Base):
    """Road network segments"""
    __tablename__ = 'roads'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    layout_id = Column(UUID(as_uuid=True), ForeignKey('layouts.id'), nullable=False)
    road_type = Column(String(50))  # access, secondary
    centerline = Column(Geometry('LINESTRING', srid=4326), nullable=False)
    right_of_way = Column(Geometry('POLYGON', srid=4326))
    width = Column(Float)
    length = Column(Float)
    attributes = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class TerrainData(Base):
    """Cached terrain analysis data"""
    __tablename__ = 'terrain'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey('properties.id'), nullable=False)
    dem_data = Column(JSON)  # Store DEM as JSON
    slope_data = Column(JSON)
    aspect_data = Column(JSON)
    elevation_stats = Column(JSON)
    bounds = Column(JSON)
    resolution = Column(Float)
    s3_key = Column(String(500))  # Reference to cached file in S3
    created_at = Column(DateTime, default=datetime.utcnow)


class Layout(Base):
    """Site layouts"""
    __tablename__ = 'layouts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey('properties.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    entry_point = Column(Geometry('POINT', srid=4326))
    layout_data = Column(JSON)  # Full layout configuration
    optimization_metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))


class LayoutVersion(Base):
    """Layout version history"""
    __tablename__ = 'layout_versions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    layout_id = Column(UUID(as_uuid=True), ForeignKey('layouts.id'), nullable=False)
    version_number = Column(Integer, nullable=False)
    layout_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(255))


class RegulatoryData(Base):
    """Fetched regulatory constraint data"""
    __tablename__ = 'regulatory_data'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey('properties.id'), nullable=False)
    data_type = Column(String(50))  # flood_zone, wetland, zoning
    geometry = Column(Geometry('GEOMETRY', srid=4326))
    attributes = Column(JSON)
    source = Column(String(100))
    fetched_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # For cache expiration


class CutFillData(Base):
    """Cut/fill volume calculations"""
    __tablename__ = 'cutfill_data'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    layout_id = Column(UUID(as_uuid=True), ForeignKey('layouts.id'), nullable=False)
    cut_volume_yd3 = Column(Float)
    fill_volume_yd3 = Column(Float)
    net_volume_yd3 = Column(Float)
    volume_data = Column(JSON)  # Detailed breakdown
    visualization_map = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

