import { useState } from 'react'
import './AssetPlacement.css'

interface AssetType {
  name: string
  category: string
  dimensions: {
    length: number
    width: number
    height: number
  }
}

interface AssetPlacementProps {
  onAssetSelect?: (assetType: string) => void
  onPlaceAsset?: (assetType: string, count: number) => void
  selectedAssets?: Array<{ type: string; count: number }>
}

const AssetPlacement = ({ onAssetSelect, onPlaceAsset, selectedAssets = [] }: AssetPlacementProps) => {
  const [assetTypes] = useState<AssetType[]>([
    { name: 'Warehouse', category: 'infrastructure', dimensions: { length: 100, width: 50, height: 30 } },
    { name: 'Office Building', category: 'infrastructure', dimensions: { length: 80, width: 60, height: 40 } },
    { name: 'Storage Facility', category: 'infrastructure', dimensions: { length: 150, width: 100, height: 25 } },
    { name: 'Solar Array', category: 'energy', dimensions: { length: 200, width: 200, height: 10 } },
    { name: 'Wind Turbine', category: 'energy', dimensions: { length: 30, width: 30, height: 300 } },
    { name: 'Battery Storage', category: 'energy', dimensions: { length: 50, width: 50, height: 15 } },
  ])
  
  const [selectedType, setSelectedType] = useState<string>('')
  const [count, setCount] = useState<number>(1)

  const handleSelect = (assetName: string) => {
    setSelectedType(assetName)
    if (onAssetSelect) {
      onAssetSelect(assetName)
    }
  }

  const handlePlace = () => {
    if (selectedType && count > 0 && onPlaceAsset) {
      onPlaceAsset(selectedType, count)
      setSelectedType('')
      setCount(1)
    }
  }

  const getAssetCount = (assetType: string) => {
    const asset = selectedAssets.find(a => a.type === assetType)
    return asset ? asset.count : 0
  }

  return (
    <div className="asset-placement">
      <div className="asset-list">
        {assetTypes.map((asset) => (
          <div
            key={asset.name}
            className={`asset-item ${selectedType === asset.name ? 'selected' : ''}`}
            onClick={() => handleSelect(asset.name)}
          >
            <div className="asset-header">
              <span className="asset-name">{asset.name}</span>
              <span className="asset-category">{asset.category}</span>
            </div>
            <div className="asset-details">
              <span>{asset.dimensions.length}ft × {asset.dimensions.width}ft</span>
              {getAssetCount(asset.name) > 0 && (
                <span className="asset-count">×{getAssetCount(asset.name)}</span>
              )}
            </div>
          </div>
        ))}
      </div>

      {selectedType && (
        <div className="asset-controls">
          <div className="count-control">
            <label>Count:</label>
            <input
              type="number"
              min="1"
              value={count}
              onChange={(e) => setCount(parseInt(e.target.value) || 1)}
            />
          </div>
          <button className="place-button" onClick={handlePlace}>
            Add to Layout
          </button>
        </div>
      )}

      {selectedAssets.length > 0 && (
        <div className="selected-assets">
          <h3>Placed Assets</h3>
          <ul>
            {selectedAssets.map((asset, idx) => (
              <li key={idx}>
                {asset.type} × {asset.count}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default AssetPlacement
