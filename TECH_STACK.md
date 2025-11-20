# Site Layout Optimizer - Tech Stack Overview

## Executive Summary

This document outlines the complete technology stack for the Site Layout Optimizer application - an AI-powered geospatial site layout optimization platform built with modern, cloud-native technologies.

---

## Technology Highlights

### Why These Choices?

**React + TypeScript**: Industry-standard frontend stack with strong type safety and excellent developer experience.

**FastAPI**: Modern Python framework with automatic API docs, async support, and high performance.

**PostGIS**: Industry-leading geospatial database extension for complex spatial queries and analysis.

**Mapbox GL JS**: High-performance mapping library with 3D capabilities and vector tiles.

**AWS Cloud-Native**: Fully managed services reduce operational overhead and provide scalability.

**Docker**: Consistent environments from development to production.

**AI Integration**: GPT-4o provides intelligent optimization recommendations beyond traditional algorithms.

---

## Frontend Stack

### Core Framework
- **React 18.2** - Modern UI library with hooks and concurrent features
- **TypeScript 5.2** - Type-safe development with strict mode enabled
- **Vite 7.2** - Next-generation build tool and dev server for fast HMR

### Routing & Navigation
- **React Router DOM 6.20** - Client-side routing and navigation

### Geospatial Visualization
- **Mapbox GL JS 3.6** - High-performance vector maps and 3D visualization
- **@mapbox/mapbox-gl-geocoder 5.0** - Location search and geocoding

### HTTP Client
- **Axios 1.6** - Promise-based HTTP client for API communication

### Development Tools
- **ESLint** - Code linting with TypeScript and React plugins
- **@vitejs/plugin-react** - Vite plugin for React support

---

## Backend Stack

### Core Framework
- **Python 3.11** - Modern Python runtime
- **FastAPI 0.104** - High-performance async web framework with automatic API documentation
- **Uvicorn 0.24** - Lightning-fast ASGI server with standard extensions

### Data Validation & Settings
- **Pydantic 2.5** - Data validation using Python type annotations
- **Pydantic Settings 2.1** - Settings management with environment variable support
- **Python-multipart 0.0.6** - File upload handling

### Geospatial Processing
- **GDAL/OGR** - Industry-standard geospatial data processing (system-level)
- **Shapely 2.0+** - Geometric operations and spatial analysis
- **GeoAlchemy2 0.14** - PostGIS integration for SQLAlchemy
- **GeoPandas 0.14** (optional) - Geospatial data manipulation with Pandas
- **Rasterio 1.3** (optional) - Raster I/O operations
- **Fiona 1.9** (optional) - Vector data I/O
- **PyProj 3.6** (optional) - Coordinate system transformations

### Data Science & Machine Learning
- **NumPy 1.26+** - Numerical computing foundation
- **Pandas 2.2+** - Data manipulation and analysis
- **SciPy 1.12+** - Scientific computing and optimization
- **Scikit-learn 1.4+** - Machine learning algorithms

### AI Integration
- **OpenAI 1.3** - GPT-4o integration via OpenRouter API
- **HTTPX 0.25** - Async HTTP client for AI API calls

### Database & ORM
- **PostgreSQL 14.9** - Relational database with PostGIS extension
- **SQLAlchemy 2.0** - Modern Python ORM with async support
- **Psycopg2-binary 2.9+** - PostgreSQL adapter for Python
- **GeoAlchemy2** - PostGIS spatial types integration

### Authentication & Security
- **Python-JOSE 3.3** - JWT token handling with cryptography
- **Passlib 1.7** - Password hashing with bcrypt

### AWS Integration
- **Boto3 1.29** - AWS SDK for Python (S3, RDS, Cognito, etc.)

### Utilities
- **Python-dotenv 1.0** - Environment variable management
- **PyYAML 6.0** - YAML configuration file parsing
- **ReportLab 4.0** - PDF generation for reports
- **Pillow 10.1** - Image processing library

---

## Infrastructure & Cloud Services

### Compute & Deployment
- **AWS App Runner** - Containerized backend deployment
- **AWS Amplify** - Frontend hosting and CI/CD
- **Docker** - Containerization for consistent environments
- **AWS Lambda** - Serverless functions (optional, for specific handlers)

### Database Services
- **AWS RDS PostgreSQL** - Managed PostgreSQL with PostGIS extension
  - Instance: db.t3.medium
  - Engine: PostgreSQL 14.9
  - Storage: GP3, 100GB allocated

### Storage Services
- **AWS S3** - Object storage for:
  - Geospatial data (KMZ/KML files)
  - Processed data
  - Export files (PDF, KMZ, GeoJSON)
  - Terrain analysis cache

### Caching
- **AWS ElastiCache Redis 7.0** - In-memory caching for:
  - Session data
  - Frequently accessed calculations
  - Rate limiting

### Authentication
- **AWS Cognito** - User authentication and authorization
  - User pools for identity management
  - JWT token generation

### API Management
- **AWS API Gateway** - RESTful API management and routing

### Infrastructure as Code
- **AWS SAM (Serverless Application Model)** - Serverless infrastructure templates
- **AWS CloudFormation** - Infrastructure provisioning and management

### Networking
- **AWS VPC** - Virtual private cloud for secure networking
- **Private Subnets** - Isolated network segments for databases and cache
- **Security Groups** - Network access control

---

## Development & Build Tools

### Frontend Build
- **Vite** - Build tool with ES modules and HMR
- **TypeScript Compiler** - Type checking and compilation
- **ESLint** - Code quality and consistency

### Backend Development
- **Python Virtual Environment** - Dependency isolation
- **Uvicorn** - Development server with auto-reload

### Containerization
- **Docker** - Multi-stage builds for optimized images
- **Dockerfile** - Python 3.11 slim base with GDAL dependencies

### CI/CD
- **AWS Amplify** - Automated frontend builds and deployments
- **Amplify YAML** - Build configuration and custom headers

---

## Architecture Patterns

### API Design
- **RESTful API** - Standard HTTP methods and status codes
- **OpenAPI/Swagger** - Auto-generated API documentation (FastAPI)
- **CORS Middleware** - Cross-origin resource sharing configuration
- **Rate Limiting** - Request throttling middleware

### Data Flow
- **Client-Side Routing** - React Router for SPA navigation
- **API Proxy** - Vite dev server proxy to backend
- **Async/Await** - Non-blocking I/O throughout the stack

### Geospatial Architecture
- **WGS84 (EPSG:4326)** - Default coordinate reference system
- **PostGIS Spatial Indexing** - Optimized geospatial queries
- **Vector Tiles** - Mapbox GL for efficient map rendering

### Security Architecture
- **JWT Tokens** - Stateless authentication
- **Environment Variables** - Secure credential management
- **HTTPS Only** - Encrypted communication
- **Security Headers** - X-Content-Type-Options, X-Frame-Options, X-XSS-Protection

---

## Key Integrations

### External APIs
- **OpenRouter API** - AI model access (GPT-4o)
- **Mapbox API** - Map tiles and geocoding services

### AWS Services Integration
- **S3** - File storage and retrieval
- **RDS** - Database connections via SQLAlchemy
- **ElastiCache** - Redis caching layer
- **Cognito** - User authentication flows

---

## Performance & Scalability

### Frontend Optimization
- **Code Splitting** - Lazy loading with React Router
- **Tree Shaking** - Dead code elimination via Vite
- **Asset Optimization** - Minification and compression

### Backend Optimization
- **Async Processing** - Non-blocking I/O operations
- **Connection Pooling** - Efficient database connections
- **Caching Strategy** - Redis for frequently accessed data
- **Geospatial Indexing** - PostGIS spatial indexes

### Scalability Features
- **Container Orchestration** - AWS App Runner auto-scaling
- **CDN Distribution** - AWS Amplify global CDN
- **Database Scaling** - RDS vertical and horizontal scaling options
- **Stateless Design** - Horizontal scaling capability

---

## Development Environment

### Local Development
- **Frontend**: `npm run dev` (Vite dev server on port 3001)
- **Backend**: `uvicorn` (FastAPI server on port 8000)
- **Database**: Local PostgreSQL or RDS connection
- **Cache**: Local Redis or ElastiCache connection

### Environment Configuration
- **.env files** - Environment-specific configuration
- **Python-dotenv** - Automatic environment variable loading
- **Pydantic Settings** - Type-safe configuration management

---

## Version Information

- **Node.js**: Compatible with Node 18+
- **Python**: 3.11
- **PostgreSQL**: 14.9
- **Redis**: 7.0
- **React**: 18.2
- **TypeScript**: 5.2
- **FastAPI**: 0.104

---

*Last Updated: Based on current codebase analysis*

