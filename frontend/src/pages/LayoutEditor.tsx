import { useState, useEffect, useCallback, useMemo } from 'react'
import MapViewer from '../components/MapViewer'
import FileUpload from '../components/FileUpload'
import AssetPlacement from '../components/AssetPlacement'
import RoadNetwork from '../components/RoadNetwork'
import ReportExport from '../components/ReportExport'
import api from '../services/api'
import mapboxgl from 'mapbox-gl'
import './LayoutEditor.css'

interface LayoutData {
  file_id?: string
  properties?: any[]
  exclusion_zones?: any[]
  assets?: Array<{ id: string; type: string; location: [number, number]; dimensions?: any }>
  roads?: Array<{ centerline: number[][]; type: string }>
  terrain_data?: any
}

const LayoutEditor = () => {
  const [mapboxToken, setMapboxToken] = useState<string>('')
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [layoutData, setLayoutData] = useState<LayoutData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedAssets, setSelectedAssets] = useState<Array<{ type: string; count: number }>>([])
  const [entryPoint, setEntryPoint] = useState<[number, number] | null>(null)
  const [mapInstance, setMapInstance] = useState<mapboxgl.Map | null>(null)
  const [optimizedLayout, setOptimizedLayout] = useState<any>(null)

  useEffect(() => {
    const token = import.meta.env.VITE_MAPBOX_TOKEN || ''
    setMapboxToken(token)
  }, [])

  const handleFileUpload = async (file: File) => {
    setLoading(true)
    setError(null)
    
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await api.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      
      console.log('Upload response:', response.data)
      
      setUploadedFile(file)
      
      // Ensure properties and exclusion_zones are arrays
      const properties = Array.isArray(response.data.properties) 
        ? response.data.properties 
        : response.data.properties 
          ? [response.data.properties] 
          : []
      
      const exclusionZones = Array.isArray(response.data.exclusion_zones)
        ? response.data.exclusion_zones
        : response.data.exclusion_zones
          ? [response.data.exclusion_zones]
          : []
      
      // Validate that we have at least one property
      if (properties.length === 0) {
        throw new Error('No property boundaries found in uploaded file')
      }
      
      // Validate property geometry
      const firstProperty = properties[0]
      if (!firstProperty.geometry || !firstProperty.geometry.coordinates) {
        throw new Error('Invalid property geometry in uploaded file')
      }
      
      console.log('Setting layout data:', {
        file_id: response.data.file_id,
        properties: properties.length,
        exclusion_zones: exclusionZones.length,
      })
      
      const newLayoutData = {
        file_id: response.data.file_id,
        properties,
        exclusion_zones: exclusionZones,
      }
      
      setLayoutData(newLayoutData)

      // Center map on property if available
      if (properties.length > 0 && properties[0].geometry) {
        const geom = properties[0].geometry
        if (geom.type === 'Polygon' && geom.coordinates && geom.coordinates[0]) {
          // Calculate center from first polygon
          const coords = geom.coordinates[0]
          const lngs = coords.map((c: number[]) => c[0])
          const lats = coords.map((c: number[]) => c[1])
          const centerLng = (Math.min(...lngs) + Math.max(...lngs)) / 2
          const centerLat = (Math.min(...lats) + Math.max(...lats)) / 2
          
          console.log('Centering map on property:', [centerLng, centerLat])
          
          // Set entry point to property center
          setEntryPoint([centerLng, centerLat])
          
          // Center map if available
          if (mapInstance) {
            mapInstance.flyTo({
              center: [centerLng, centerLat],
              zoom: 14,
            })
          }
        }
      }

      // Auto-analyze terrain
      if (response.data.file_id) {
        await handleAnalyze(response.data.file_id)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error uploading file')
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyze = async (fileId: string) => {
    if (!fileId) {
      console.warn('Cannot analyze: no file ID')
      return
    }
    
    setLoading(true)
    setError(null)
    try {
      const response = await api.post('/analyze', {
        file_id: fileId,
        resolution: 10.0,
      })
      
      setLayoutData(prev => ({
        ...prev,
        terrain_data: response.data,
      }))
    } catch (err: any) {
      console.error('Analysis error:', err)
      const errorMsg = err.response?.data?.detail || err.message || 'Error analyzing terrain'
      setError(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  const handleAssetPlace = (assetType: string, count: number) => {
    setSelectedAssets(prev => {
      const existing = prev.find(a => a.type === assetType)
      if (existing) {
        return prev.map(a => 
          a.type === assetType ? { ...a, count: a.count + count } : a
        )
      }
      return [...prev, { type: assetType, count }]
    })
  }

  const handleOptimize = async () => {
    if (!layoutData || !layoutData.properties || layoutData.properties.length === 0) {
      setError('Please upload a property file first')
      return
    }
    
    if (selectedAssets.length === 0) {
      setError('Please select at least one asset type to place')
      return
    }
    
    // Validate property boundary
    const property = layoutData.properties[0]
    if (!property.geometry || !property.geometry.coordinates || !property.geometry.coordinates[0]) {
      setError('Invalid property boundary data')
      return
    }
    
    const boundary = property.geometry.coordinates[0]
    if (boundary.length < 3) {
      setError('Property boundary must have at least 3 points')
      return
    }

    setLoading(true)
    setError(null)

    try {
      // Get property boundary from first property
      const property = layoutData.properties[0]
      const geometry = property.geometry || property
      
      // Extract coordinates - property_boundary expects List[List[float]] (the outer array of Polygon)
      let boundary: number[][] = []
      if (geometry.type === 'Polygon' && geometry.coordinates && geometry.coordinates[0]) {
        boundary = geometry.coordinates[0] // First ring of polygon
      } else if (Array.isArray(geometry.coordinates)) {
        boundary = geometry.coordinates[0] || geometry.coordinates
      }

      if (boundary.length === 0) {
        setError('Invalid property boundary. Please upload a valid property file.')
        setLoading(false)
        return
      }

      // Convert exclusion zones - each zone is a polygon with coordinates
      const exclusionZones = (layoutData.exclusion_zones || [])
        .map((zone: any) => {
          const zoneGeom = zone.geometry || zone
          if (zoneGeom.type === 'Polygon' && zoneGeom.coordinates && zoneGeom.coordinates[0]) {
            return zoneGeom.coordinates[0] // First ring of polygon
          }
          return null
        })
        .filter((z: any) => z !== null)

      // Get entry point (use first if not set)
      const entry = entryPoint || [-98.5795, 39.8283]

      console.log('Sending optimize request:', {
        property_boundary: boundary.length,
        exclusion_zones: exclusionZones.length,
        asset_requirements: selectedAssets.length,
        entry_point: entry,
      })

      const response = await api.post('/optimize', {
        property_boundary: boundary,
        exclusion_zones: exclusionZones.length > 0 ? exclusionZones : undefined,
        asset_requirements: selectedAssets.map(a => ({
          type: a.type,
          count: a.count,
        })),
        entry_point: entry,
        terrain_data: layoutData.terrain_data,
        fetch_regulatory: true,
      })

      console.log('Optimize response:', response.data)
      console.log('Assets received:', response.data.assets)
      
      setOptimizedLayout(response.data)
      
      // Ensure assets have the correct format
      const assets = (response.data.assets || []).map((asset: any) => {
        // Ensure location is [lng, lat] format
        const location = asset.location || [asset.x, asset.y] || [0, 0]
        if (!Array.isArray(location) || location.length < 2) {
          console.warn('Invalid asset location:', asset)
          return null
        }
        return {
          id: asset.id || `asset-${Math.random()}`,
          type: asset.type || 'unknown',
          location: [location[0], location[1]], // Ensure [lng, lat]
          dimensions: asset.dimensions || {},
        }
      }).filter((a: any) => a !== null)
      
      console.log('Processed assets:', assets)
      console.log('Setting assets in layout data:', assets)
      
      setLayoutData(prev => ({
        ...prev,
        assets: assets,
      }))

      // Auto-generate roads
      if (assets.length > 0) {
        await handleGenerateRoads(assets)
      }
    } catch (err: any) {
      console.error('Optimize error:', err)
      let errorMessage = 'Error optimizing layout'
      
      if (err.response?.data) {
        // Handle FastAPI validation errors
        if (Array.isArray(err.response.data.detail)) {
          // Validation errors come as an array
          errorMessage = err.response.data.detail.map((e: any) => e.msg || e.message || JSON.stringify(e)).join(', ')
        } else if (typeof err.response.data.detail === 'string') {
          errorMessage = err.response.data.detail
        } else if (err.response.data.detail) {
          errorMessage = JSON.stringify(err.response.data.detail)
        }
      }
      
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateRoads = async (assets?: any[], providedEntryPoint?: [number, number] | null) => {
    console.log('handleGenerateRoads called with:', { assets, layoutData: !!layoutData, entryPoint, providedEntryPoint })
    
    if (!layoutData) {
      console.log('Early return: missing layoutData')
      return
    }

    // Use provided entry point, then state entry point, otherwise use property center or default
    const effectiveEntryPoint = providedEntryPoint || entryPoint || (() => {
      // Try to get property center
      const property = layoutData.properties?.[0]
      if (property?.geometry) {
        const coords = property.geometry.coordinates?.[0]
        if (coords && coords.length > 0) {
          // Calculate center of polygon
          const sum = coords.reduce((acc: [number, number], coord: number[]) => 
            [acc[0] + coord[0], acc[1] + coord[1]], [0, 0])
          return [sum[0] / coords.length, sum[1] / coords.length] as [number, number]
        }
      }
      // Default fallback
      return [-98.5795, 39.8283] as [number, number]
    })()
    
    console.log('Using entry point:', effectiveEntryPoint)

    const assetsToUse = assets || layoutData.assets || []
    console.log('Assets to use:', assetsToUse.length, assetsToUse)
    
    if (assetsToUse.length === 0) {
      console.log('Early return: no assets to use')
      return
    }

    setLoading(true)
    try {
      const property = layoutData.properties?.[0]
      const geometry = property?.geometry || property
      console.log('Property geometry:', geometry)
      
      // Extract coordinates - property_boundary expects List[List[float]] (the outer array of Polygon)
      let boundary: number[][] = []
      if (geometry.type === 'Polygon' && geometry.coordinates && geometry.coordinates[0]) {
        boundary = geometry.coordinates[0] // First ring of polygon
      } else if (Array.isArray(geometry.coordinates)) {
        boundary = geometry.coordinates[0] || geometry.coordinates
      }

      console.log('Extracted boundary:', boundary.length, 'points')

      if (boundary.length === 0) {
        console.error('Invalid property boundary for road generation')
        setError('Invalid property boundary for road generation')
        setLoading(false)
        return
      }

      // Convert exclusion zones - each zone is a polygon with coordinates
      const exclusionZones = (layoutData.exclusion_zones || [])
        .map((zone: any) => {
          const zoneGeom = zone.geometry || zone
          if (zoneGeom.type === 'Polygon' && zoneGeom.coordinates && zoneGeom.coordinates[0]) {
            return zoneGeom.coordinates[0] // First ring of polygon
          }
          return null
        })
        .filter((z: any) => z !== null)

      // Convert assets to format expected by backend (x, y instead of location)
      const formattedAssets = assetsToUse.map((asset: any) => {
        const location = asset.location || [asset.x, asset.y] || [0, 0]
        return {
          id: asset.id,
          type: asset.type,
          x: location[0],  // lng
          y: location[1],  // lat
          dimensions: asset.dimensions || {},
        }
      })

      console.log('Generating roads with:', {
        entry_point: effectiveEntryPoint,
        assets: formattedAssets.length,
        property_boundary: boundary.length,
        exclusion_zones: exclusionZones.length,
        formatted_assets: formattedAssets,
      })

      const response = await api.post('/generate-roads', {
        entry_point: effectiveEntryPoint,
        assets: formattedAssets,
        property_boundary: boundary,
        exclusion_zones: exclusionZones.length > 0 ? exclusionZones : undefined,
        terrain_data: layoutData.terrain_data,
      })

      console.log('Road generation response:', response.data)
      console.log('Road network:', response.data.road_network)
      console.log('Roads array:', response.data.road_network?.roads)
      
      const roadsData = response.data.road_network?.roads || []
      console.log('Setting roads in layout data:', roadsData, 'Count:', roadsData.length)
      
      setLayoutData(prev => ({
        ...prev,
        roads: roadsData,
      }))
    } catch (err: any) {
      console.error('Road generation error:', err)
      let errorMessage = 'Error generating roads'
      
      if (err.response?.data) {
        // Handle FastAPI validation errors
        if (Array.isArray(err.response.data.detail)) {
          // Validation errors come as an array
          errorMessage = err.response.data.detail.map((e: any) => e.msg || e.message || JSON.stringify(e)).join(', ')
        } else if (typeof err.response.data.detail === 'string') {
          errorMessage = err.response.data.detail
        } else if (err.response.data.detail) {
          errorMessage = JSON.stringify(err.response.data.detail)
        }
      }
      
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleMapClick = useCallback((lng: number, lat: number) => {
    console.log('Map clicked at:', lng, lat)
    const newEntryPoint: [number, number] = [lng, lat]
    setEntryPoint(newEntryPoint)
    
    // Auto-generate roads if assets are already placed
    // Pass the entry point directly to avoid stale closure issues
    if (layoutData?.assets && layoutData.assets.length > 0) {
      console.log('Entry point set, auto-generating roads for', layoutData.assets.length, 'assets')
      // Pass the entry point directly to handleGenerateRoads to avoid stale state issues
      handleGenerateRoads(layoutData.assets, newEntryPoint)
    } else {
      console.log('No assets to generate roads for')
    }
  }, [layoutData])
  
  const handleMapLoad = useCallback((map: mapboxgl.Map) => {
    setMapInstance(map)
  }, [])

  // Convert data to GeoJSON for map (memoized to prevent re-renders)
  const propertyGeoJSON = useMemo(() => {
    if (!layoutData?.properties?.[0]) {
      console.log('No property data available for map')
      return undefined
    }
    
    const property = layoutData.properties[0]
    const geometry = property.geometry || property
    
    console.log('Creating property GeoJSON from:', property)
    console.log('Geometry:', geometry)
    
    if (!geometry || !geometry.type || !geometry.coordinates) {
      console.warn('Invalid geometry structure:', geometry)
      return undefined
    }
    
    return {
      type: 'FeatureCollection' as const,
      features: [{
        type: 'Feature' as const,
        geometry: geometry,
        properties: property.attributes || {},
      }],
    }
  }, [layoutData?.properties])

  const exclusionZonesGeoJSON = useMemo(() => {
    if (!layoutData?.exclusion_zones || layoutData.exclusion_zones.length === 0) {
      console.log('No exclusion zones available for map')
      return undefined
    }
    
    console.log('Creating exclusion zones GeoJSON from:', layoutData.exclusion_zones)
    
    return {
      type: 'FeatureCollection' as const,
      features: layoutData.exclusion_zones.map((zone: any) => {
        const geometry = zone.geometry || zone
        if (!geometry || !geometry.type || !geometry.coordinates) {
          console.warn('Invalid exclusion zone geometry:', zone)
          return null
        }
        return {
          type: 'Feature' as const,
          geometry: geometry,
          properties: zone.attributes || {},
        }
      }).filter((f: any) => f !== null),
    }
  }, [layoutData?.exclusion_zones])

  // Memoize assets and roads to prevent unnecessary re-renders
  const memoizedAssets = useMemo(() => {
    return layoutData?.assets || []
  }, [layoutData?.assets])

  const memoizedRoads = useMemo(() => {
    const roads = layoutData?.roads || []
    console.log('Memoized roads:', roads, 'Count:', roads.length)
    return roads
  }, [layoutData?.roads ? JSON.stringify(layoutData.roads) : null])

  return (
    <div className="layout-editor">
      <header className="editor-header">
        <h1>Site Layout Editor</h1>
        <p>Pacifico Energy Group - AI-Powered Site Layout Optimization</p>
      </header>
      
      <div className="editor-content">
        <aside className="editor-sidebar">
          <section className="sidebar-section">
            <h2>Upload Property Data</h2>
            <FileUpload onUpload={handleFileUpload} />
            {uploadedFile && (
              <p className="upload-success">✓ {uploadedFile.name} uploaded</p>
            )}
            {layoutData?.file_id && (
              <p className="file-id">File ID: {layoutData.file_id}</p>
            )}
            {layoutData?.file_id && !layoutData?.terrain_data && (
              <button
                className="analyze-button"
                onClick={() => handleAnalyze(layoutData.file_id!)}
                disabled={loading}
                style={{
                  marginTop: '10px',
                  padding: '8px 16px',
                  backgroundColor: '#007bff',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                }}
              >
                {loading ? 'Analyzing...' : 'Analyze Terrain'}
              </button>
            )}
            {layoutData?.terrain_data && (
              <p className="upload-success" style={{ marginTop: '10px' }}>
                ✓ Terrain analyzed
              </p>
            )}
          </section>
          
          <section className="sidebar-section">
            <h2>Asset Placement</h2>
            <AssetPlacement 
              onPlaceAsset={handleAssetPlace}
              selectedAssets={selectedAssets}
            />
          </section>
          
          <section className="sidebar-section">
            <h2>Road Network</h2>
            <RoadNetwork 
              onGenerate={() => {
                console.log('Generate Road Network button clicked')
                handleGenerateRoads()
              }}
              roadData={layoutData?.roads ? {
                totalLength: layoutData.roads.reduce((sum: number, road: any) => sum + (road.length || 0), 0),
                roadCount: layoutData.roads.length,
              } : undefined}
              loading={loading}
              entryPoint={entryPoint}
            />
          </section>
          
          <section className="sidebar-section">
            <h2>Export</h2>
            <ReportExport 
              layoutId={optimizedLayout?.layout_id || layoutData?.file_id}
              layoutData={layoutData}
            />
          </section>
          
          <button 
            className="optimize-button"
            onClick={handleOptimize}
            disabled={!layoutData || loading || selectedAssets.length === 0}
          >
            {loading ? 'Processing...' : 'Optimize Layout'}
          </button>

          {optimizedLayout && (
            <div className="optimization-results">
              <h3>Optimization Results</h3>
              <div className="result-metric">
                <span>Assets Placed:</span>
                <span>{optimizedLayout.optimization_metrics?.assets_placed || 0}</span>
              </div>
              <div className="result-metric">
                <span>Site Utilization:</span>
                <span>{(optimizedLayout.optimization_metrics?.site_utilization || 0 * 100).toFixed(1)}%</span>
              </div>
            </div>
          )}
        </aside>
        
        <main className="editor-main">
          {error && (
            <div className="error-message">
              <span>{String(error)}</span>
              <button onClick={() => setError(null)}>×</button>
            </div>
          )}
          
          {loading && (
            <div className="loading-overlay">
              <div className="spinner"></div>
              <p>Processing...</p>
            </div>
          )}
          
          {mapboxToken ? (
            <>
              <MapViewer 
                accessToken={mapboxToken}
                initialCenter={entryPoint ? entryPoint : [-98.5795, 39.8283]}
                initialZoom={12}
                propertyBoundary={propertyGeoJSON}
                assets={memoizedAssets}
                roads={memoizedRoads}
                exclusionZones={exclusionZonesGeoJSON}
                onMapClick={handleMapClick}
                onMapLoad={handleMapLoad}
              />
              {propertyGeoJSON && (
                <div className="map-info">
                  <p>✓ Property boundary loaded</p>
                  {exclusionZonesGeoJSON && exclusionZonesGeoJSON.features.length > 0 && (
                    <p>✓ {exclusionZonesGeoJSON.features.length} exclusion zone(s) loaded</p>
                  )}
                  {memoizedAssets && memoizedAssets.length > 0 && (
                    <p>✓ {memoizedAssets.length} asset(s) placed</p>
                  )}
                </div>
              )}
            </>
          ) : (
            <div className="map-placeholder">
              <p>Mapbox token required. Set VITE_MAPBOX_TOKEN in .env</p>
              <p className="hint">The map will display property boundaries, assets, roads, and exclusion zones</p>
            </div>
          )}

          {entryPoint && (
            <div className="entry-point-marker">
              Entry Point: {entryPoint[0].toFixed(6)}, {entryPoint[1].toFixed(6)}
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default LayoutEditor
