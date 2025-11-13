import { useEffect, useRef, useState } from 'react'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'

interface MapViewerProps {
  accessToken: string
  initialCenter?: [number, number]
  initialZoom?: number
  propertyBoundary?: GeoJSON.FeatureCollection
  assets?: Array<{ id: string; type: string; location: [number, number]; dimensions?: any }>
  roads?: Array<{ centerline: number[][]; type: string }>
  exclusionZones?: GeoJSON.FeatureCollection
  onMapClick?: (lng: number, lat: number) => void
  onMapLoad?: (map: mapboxgl.Map) => void
}

const MapViewer = ({ 
  accessToken, 
  initialCenter = [-98.5795, 39.8283], 
  initialZoom = 10,
  propertyBoundary,
  assets,
  roads,
  exclusionZones,
  onMapClick,
  onMapLoad
}: MapViewerProps) => {
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<mapboxgl.Map | null>(null)
  const [mapLoaded, setMapLoaded] = useState(false)

  useEffect(() => {
    if (!mapContainer.current || map.current || !accessToken) return

    if (!accessToken || accessToken.trim() === '') {
      console.error('Mapbox access token is missing')
      return
    }

    mapboxgl.accessToken = accessToken

    try {
      map.current = new mapboxgl.Map({
        container: mapContainer.current,
        style: 'mapbox://styles/mapbox/satellite-v9',
        center: initialCenter,
        zoom: initialZoom,
        attributionControl: false,
      })

      map.current.on('error', (e) => {
        console.error('Mapbox error:', e)
        if (e.error?.message) {
          console.error('Error details:', e.error.message)
        }
      })

      map.current.on('load', () => {
        console.log('Map loaded successfully')
        setMapLoaded(true)
        if (onMapLoad && map.current) {
          onMapLoad(map.current)
        }
      })
      
      // Also listen for style load to ensure layers can be added
      map.current.on('style.load', () => {
        console.log('Map style loaded')
      })

      // Handle map clicks
      if (onMapClick) {
        map.current.on('click', (e) => {
          onMapClick(e.lngLat.lng, e.lngLat.lat)
        })
      }
    } catch (error) {
      console.error('Failed to initialize Mapbox:', error)
      return
    }

    return () => {
      if (map.current) {
        map.current.remove()
        map.current = null
      }
    }
  }, [accessToken]) // Only re-initialize if token changes - center/zoom set on initial load only

  // Add property boundary layer
  useEffect(() => {
    if (!map.current || !mapLoaded) {
      console.log('Map not ready for property boundary:', { map: !!map.current, mapLoaded })
      return
    }

    const sourceId = 'property-boundary'
    const layerId = 'property-boundary-layer'

    if (propertyBoundary) {
      console.log('Adding property boundary to map:', propertyBoundary)
      
      try {
        // Update or add source
        if (map.current.getSource(sourceId)) {
          // Update existing source
          console.log('Updating existing property boundary source')
          const source = map.current.getSource(sourceId) as mapboxgl.GeoJSONSource
          source.setData(propertyBoundary as any)
        } else {
          // Add new source and layers
          console.log('Adding new property boundary source and layers')
          map.current.addSource(sourceId, {
            type: 'geojson',
            data: propertyBoundary as any,
          })

          map.current.addLayer({
            id: layerId,
            type: 'fill',
            source: sourceId,
            paint: {
              'fill-color': '#088',
              'fill-opacity': 0.3,
            },
          })

          map.current.addLayer({
            id: `${layerId}-outline`,
            type: 'line',
            source: sourceId,
            paint: {
              'line-color': '#088',
              'line-width': 3,
            },
          })
          
          console.log('Property boundary layers added successfully')
          
          // Fit map to property boundary
          if (propertyBoundary.features && propertyBoundary.features.length > 0) {
            try {
              const bounds = new mapboxgl.LngLatBounds()
              propertyBoundary.features.forEach((feature: any) => {
                if (feature.geometry && feature.geometry.coordinates) {
                  if (feature.geometry.type === 'Polygon') {
                    const coords = feature.geometry.coordinates[0]
                    console.log('Fitting bounds to polygon with', coords.length, 'coordinates')
                    coords.forEach((coord: number[]) => {
                      bounds.extend([coord[0], coord[1]])
                    })
                  }
                }
              })
              
              if (!bounds.isEmpty()) {
                const sw = bounds.getSouthWest()
                const ne = bounds.getNorthEast()
                console.log('Property bounds:', {
                  southwest: [sw.lng, sw.lat],
                  northeast: [ne.lng, ne.lat]
                })
                
                if (map.current) {
                  map.current.fitBounds(bounds, {
                    padding: 50,
                    maxZoom: 16,
                    duration: 1000,
                  })
                  console.log('Map fitted to property boundary')
                }
              } else {
                console.warn('Bounds are empty, cannot fit map')
              }
            } catch (boundsError) {
              console.error('Error fitting bounds:', boundsError)
            }
          }
        }
      } catch (error) {
        console.error('Error adding property boundary to map:', error)
      }
    } else {
      console.log('No property boundary to display')
      // Remove if propertyBoundary is cleared
      if (map.current.getSource(sourceId)) {
        try {
          if (map.current.getLayer(layerId)) map.current.removeLayer(layerId)
          if (map.current.getLayer(`${layerId}-outline`)) map.current.removeLayer(`${layerId}-outline`)
          map.current.removeSource(sourceId)
        } catch (e) {
          console.error('Error removing property boundary:', e)
        }
      }
    }
  }, [mapLoaded, propertyBoundary ? JSON.stringify(propertyBoundary) : null])

  // Add exclusion zones layer
  useEffect(() => {
    if (!map.current || !mapLoaded) {
      console.log('Map not ready for exclusion zones:', { map: !!map.current, mapLoaded })
      return
    }

    const sourceId = 'exclusion-zones'
    const layerId = 'exclusion-zones-layer'

    if (exclusionZones && exclusionZones.features && exclusionZones.features.length > 0) {
      console.log('Adding exclusion zones to map:', exclusionZones)
      
      try {
        if (map.current.getSource(sourceId)) {
          // Update existing source
          console.log('Updating existing exclusion zones source')
          const source = map.current.getSource(sourceId) as mapboxgl.GeoJSONSource
          source.setData(exclusionZones as any)
        } else {
          // Add new source and layer
          map.current.addSource(sourceId, {
            type: 'geojson',
            data: exclusionZones as any,
          })

          map.current.addLayer({
            id: layerId,
            type: 'fill',
            source: sourceId,
            paint: {
              'fill-color': '#f00',
              'fill-opacity': 0.3,
            },
          })
          
          console.log('Exclusion zones layers added successfully')
        }
      } catch (error) {
        console.error('Error adding exclusion zones to map:', error)
      }
    } else {
      console.log('No exclusion zones to display')
      // Remove if exclusionZones is cleared
      if (map.current.getSource(sourceId)) {
        try {
          if (map.current.getLayer(layerId)) map.current.removeLayer(layerId)
          map.current.removeSource(sourceId)
        } catch (e) {
          // Ignore errors
        }
      }
    }
  }, [mapLoaded, exclusionZones ? JSON.stringify(exclusionZones) : null])

  // Add assets layer
  useEffect(() => {
    if (!map.current || !mapLoaded) {
      console.log('Map not ready for assets:', { map: !!map.current, mapLoaded })
      return
    }

    const sourceId = 'assets'
    const layerId = 'assets-layer'

    if (assets && assets.length > 0) {
      console.log('Adding assets to map:', assets)
      
      const assetsGeoJSON: GeoJSON.FeatureCollection = {
        type: 'FeatureCollection',
        features: assets.map(asset => {
          const location = asset.location || [0, 0]
          console.log('Asset:', asset.id, asset.type, 'at', location)
          return {
            type: 'Feature',
            geometry: {
              type: 'Point',
              coordinates: location,
            },
            properties: {
              id: asset.id,
              type: asset.type,
              dimensions: asset.dimensions,
            },
          }
        }),
      }

      console.log('Assets GeoJSON:', assetsGeoJSON)

      try {
        if (map.current.getSource(sourceId)) {
          // Update existing source
          console.log('Updating existing assets source')
          const source = map.current.getSource(sourceId) as mapboxgl.GeoJSONSource
          source.setData(assetsGeoJSON as any)
        } else {
          // Add new source and layers
          console.log('Adding new assets source and layers')
          map.current.addSource(sourceId, {
            type: 'geojson',
            data: assetsGeoJSON as any,
          })

          map.current.addLayer({
          id: layerId,
          type: 'circle',
          source: sourceId,
          paint: {
            'circle-radius': 12,
            'circle-color': '#ff6600',
            'circle-stroke-width': 3,
            'circle-stroke-color': '#fff',
            'circle-opacity': 0.9,
          },
        })

        // Add labels
        map.current.addLayer({
          id: `${layerId}-labels`,
          type: 'symbol',
          source: sourceId,
          layout: {
            'text-field': ['get', 'type'],
            'text-font': ['Open Sans Semibold', 'Arial Unicode MS Bold'],
            'text-offset': [0, 1.25],
            'text-anchor': 'top',
            'text-size': 12,
          },
          paint: {
            'text-color': '#fff',
            'text-halo-color': '#000',
            'text-halo-width': 2,
          },
        })
        
        console.log('Assets layers added successfully')
      }
      } catch (error) {
        console.error('Error adding assets to map:', error)
      }
    } else {
      console.log('No assets to display')
      // Remove if assets array is empty
      if (map.current.getSource(sourceId)) {
        try {
          if (map.current.getLayer(layerId)) map.current.removeLayer(layerId)
          if (map.current.getLayer(`${layerId}-labels`)) map.current.removeLayer(`${layerId}-labels`)
          map.current.removeSource(sourceId)
        } catch (e) {
          // Ignore errors
        }
      }
    }
  }, [mapLoaded, assets ? JSON.stringify(assets) : null])

  // Add roads layer
  useEffect(() => {
    if (!map.current || !mapLoaded) {
      console.log('Map not ready for roads:', { map: !!map.current, mapLoaded })
      return
    }

    const sourceId = 'roads'
    const layerId = 'roads-layer'

    console.log('Roads data received:', roads, 'Length:', roads?.length)

    if (roads && roads.length > 0) {
      console.log('Processing roads for map display:', roads)
      
      const roadsGeoJSON: GeoJSON.FeatureCollection = {
        type: 'FeatureCollection',
        features: roads
          .map((road, idx) => {
            console.log(`Road ${idx}:`, road, 'centerline:', road.centerline)
            
            // Ensure centerline is in correct format [lng, lat][]
            let centerline = road.centerline
            if (!Array.isArray(centerline) || centerline.length === 0) {
              console.warn(`Road ${idx} has invalid centerline:`, centerline)
              return null
            }
            
            // Check if centerline is array of arrays (coordinates)
            if (!Array.isArray(centerline[0])) {
              console.warn(`Road ${idx} centerline is not array of arrays:`, centerline)
              return null
            }
            
            return {
              type: 'Feature' as const,
              geometry: {
                type: 'LineString' as const,
                coordinates: centerline as [number, number][],
              },
              properties: {
                id: `road-${idx}`,
                type: road.type || 'road',
              },
            } as GeoJSON.Feature<GeoJSON.LineString>
          })
          .filter((f): f is GeoJSON.Feature<GeoJSON.LineString> => f !== null),
      }

      console.log('Roads GeoJSON created:', roadsGeoJSON, 'Features:', roadsGeoJSON.features.length)

      try {
        if (map.current.getSource(sourceId)) {
          // Update existing source
          console.log('Updating existing roads source')
          const source = map.current.getSource(sourceId) as mapboxgl.GeoJSONSource
          source.setData(roadsGeoJSON as any)
          
          // Fit map to show all roads after update
          setTimeout(() => {
            try {
              const bounds = new mapboxgl.LngLatBounds()
              let hasCoords = false
              roadsGeoJSON.features.forEach((feature: any) => {
                if (feature.geometry.type === 'LineString' && feature.geometry.coordinates) {
                  feature.geometry.coordinates.forEach((coord: [number, number]) => {
                    bounds.extend(coord)
                    hasCoords = true
                  })
                }
              })
              if (hasCoords && !bounds.isEmpty() && map.current) {
                map.current.fitBounds(bounds, {
                  padding: 100,
                  maxZoom: 18,
                  duration: 1000,
                })
                console.log('Map fitted to roads bounds (update)')
              }
            } catch (e) {
              console.warn('Could not fit bounds to roads:', e)
            }
          }, 500)
        } else {
          // Add new source and layer
          console.log('Adding new roads source and layer')
          map.current.addSource(sourceId, {
            type: 'geojson',
            data: roadsGeoJSON as any,
          })

          // Add roads layer before any labels (so roads are visible)
          const beforeId = map.current.getLayer('assets-layer-labels')?.id || undefined
          
          map.current.addLayer({
            id: layerId,
            type: 'line',
            source: sourceId,
            paint: {
              'line-color': '#ff0000',  // Bright red for maximum visibility
              'line-width': [
                'interpolate',
                ['linear'],
                ['zoom'],
                10, 5,
                15, 10,
                18, 15
              ],
              'line-opacity': 1.0,
            },
            layout: {
              'line-join': 'round',
              'line-cap': 'round',
            },
          }, beforeId)
          
          // Add a click handler to verify roads are clickable
          map.current.on('click', layerId, (e: any) => {
            console.log('Road clicked!', e)
          })
          
          console.log('Roads layer added successfully')
          
          // Verify layer was actually added
          const addedLayer = map.current.getLayer(layerId)
          if (addedLayer) {
            console.log('Roads layer verified on map:', addedLayer)
          } else {
            console.error('ERROR: Roads layer was not added to map!')
          }
          
          // Log first few coordinates to verify format
          if (roadsGeoJSON.features.length > 0) {
            const firstFeature = roadsGeoJSON.features[0]
            if (firstFeature.geometry.type === 'LineString' && 'coordinates' in firstFeature.geometry) {
              const firstCoords = firstFeature.geometry.coordinates.slice(0, 3)
              console.log('First 3 road coordinates:', firstCoords)
            }
          }
          
          // Fit map to show all roads after a short delay to ensure layer is rendered
          setTimeout(() => {
            try {
              const bounds = new mapboxgl.LngLatBounds()
              let hasCoords = false
              roadsGeoJSON.features.forEach((feature: any) => {
                if (feature.geometry.type === 'LineString' && feature.geometry.coordinates) {
                  feature.geometry.coordinates.forEach((coord: [number, number]) => {
                    if (Array.isArray(coord) && coord.length === 2 && 
                        typeof coord[0] === 'number' && typeof coord[1] === 'number') {
                      bounds.extend(coord as [number, number])
                      hasCoords = true
                    }
                  })
                }
              })
              if (hasCoords && !bounds.isEmpty()) {
                const sw = bounds.getSouthWest()
                const ne = bounds.getNorthEast()
                console.log('Roads bounds:', { 
                  southwest: [sw.lng, sw.lat], 
                  northeast: [ne.lng, ne.lat] 
                })
                if (map.current) {
                  map.current.fitBounds(bounds, {
                    padding: 100,
                    maxZoom: 18,
                    duration: 1000,
                  })
                }
                console.log('Map fitted to roads bounds')
              } else {
                console.warn('Could not create bounds from roads - no valid coordinates')
              }
            } catch (e) {
              console.error('Error fitting bounds to roads:', e)
            }
          }, 500)
        }
      } catch (error) {
        console.error('Error adding roads to map:', error)
      }
    } else {
      console.log('No roads to display')
      // Remove if roads array is empty
      if (map.current.getSource(sourceId)) {
        try {
          if (map.current.getLayer(layerId)) map.current.removeLayer(layerId)
          map.current.removeSource(sourceId)
        } catch (e) {
          // Ignore errors
        }
      }
    }
  }, [mapLoaded, roads ? JSON.stringify(roads) : null])

  return <div ref={mapContainer} style={{ width: '100%', height: '100%' }} />
}

export default MapViewer
