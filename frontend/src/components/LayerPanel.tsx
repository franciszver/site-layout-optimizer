import { useState } from 'react'
import './LayerPanel.css'

interface LayerPanelProps {
  propertyBoundary?: GeoJSON.FeatureCollection
  exclusionZones?: GeoJSON.FeatureCollection
  assets?: Array<{ id: string; type: string; location: [number, number]; dimensions?: any }>
  roads?: Array<{ centerline: number[][]; type: string }>
  onLayerToggle?: (layerId: string, visible: boolean) => void
}

const LayerPanel = ({
  propertyBoundary,
  exclusionZones,
  assets,
  roads,
  onLayerToggle
}: LayerPanelProps) => {
  const [layers, setLayers] = useState<Record<string, boolean>>({
    'property-boundary': true,
    'exclusion-zones': true,
    'assets': true,
    'roads': true,
  })

  const handleToggle = (layerId: string) => {
    const newVisibility = !layers[layerId]
    setLayers(prev => ({
      ...prev,
      [layerId]: newVisibility
    }))
    if (onLayerToggle) {
      onLayerToggle(layerId, newVisibility)
    }
  }

  const getLayerIcon = (layerId: string) => {
    switch (layerId) {
      case 'property-boundary':
        return '📐'
      case 'exclusion-zones':
        return '🚫'
      case 'assets':
        return '🏗️'
      case 'roads':
        return '🛣️'
      default:
        return '📍'
    }
  }

  return (
    <div className="layer-panel">
      <div className="layer-panel-header">
        <h3>Map Contents</h3>
      </div>
      <div className="layer-list">
        {/* Property Boundary */}
        {propertyBoundary && propertyBoundary.features.length > 0 && (
          <div className="layer-item">
            <label className="layer-checkbox">
              <input
                type="checkbox"
                checked={layers['property-boundary']}
                onChange={() => handleToggle('property-boundary')}
              />
              <span className="layer-icon">{getLayerIcon('property-boundary')}</span>
              <span className="layer-name">Property Boundary</span>
            </label>
          </div>
        )}

        {/* Exclusion Zones */}
        {exclusionZones && exclusionZones.features.length > 0 && (
          <>
            {exclusionZones.features.map((zone, index) => {
              const zoneId = `exclusion-zone-${index}`
              const zoneName = zone.properties?.name || `Exclusion Zone ${index + 1}`
              return (
                <div key={zoneId} className="layer-item">
                  <label className="layer-checkbox">
                    <input
                      type="checkbox"
                      checked={layers['exclusion-zones']}
                      onChange={() => handleToggle('exclusion-zones')}
                    />
                    <span className="layer-icon">{getLayerIcon('exclusion-zones')}</span>
                    <span className="layer-name">{zoneName}</span>
                  </label>
                </div>
              )
            })}
          </>
        )}

        {/* Assets */}
        {assets && assets.length > 0 && (
          <>
            {assets.map((asset) => {
              const assetId = `asset-${asset.id}`
              return (
                <div key={assetId} className="layer-item layer-item-indented">
                  <label className="layer-checkbox">
                    <input
                      type="checkbox"
                      checked={layers['assets']}
                      onChange={() => handleToggle('assets')}
                    />
                    <span className="layer-icon">📍</span>
                    <span className="layer-name">{asset.type} - {asset.id}</span>
                  </label>
                </div>
              )
            })}
          </>
        )}

        {/* Roads */}
        {roads && roads.length > 0 && (
          <>
            {roads.map((road, index) => {
              const roadId = `road-${index}`
              const roadName = road.type || `Road ${index + 1} - access`
              return (
                <div key={roadId} className="layer-item layer-item-indented">
                  <label className="layer-checkbox">
                    <input
                      type="checkbox"
                      checked={layers['roads']}
                      onChange={() => handleToggle('roads')}
                    />
                    <span className="layer-icon">{getLayerIcon('roads')}</span>
                    <span className="layer-name">{roadName}</span>
                  </label>
                </div>
              )
            })}
          </>
        )}

        {/* Empty state */}
        {(!propertyBoundary || propertyBoundary.features.length === 0) &&
         (!exclusionZones || exclusionZones.features.length === 0) &&
         (!assets || assets.length === 0) &&
         (!roads || roads.length === 0) && (
          <div className="layer-empty">
            <p>No layers available. Upload a property file to begin.</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default LayerPanel

