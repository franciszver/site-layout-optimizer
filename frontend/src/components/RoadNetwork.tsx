// useState removed - not used
import './RoadNetwork.css'

interface RoadNetworkProps {
  onGenerate?: () => void
  roadData?: {
    totalLength: number
    roadCount: number
  }
  loading?: boolean
  entryPoint?: [number, number] | null
}

const RoadNetwork = ({ onGenerate, roadData, loading, entryPoint }: RoadNetworkProps) => {
  const handleGenerate = () => {
    console.log('RoadNetwork: Generate button clicked, entryPoint:', entryPoint)
    if (onGenerate) {
      onGenerate()
    }
  }

  return (
    <div className="road-network">
      <div className="road-controls">
        <div className="entry-point-section">
          <label>Entry Point</label>
          <p className="hint">Click on map to set entry point</p>
          {entryPoint && (
            <div className="entry-point-display">
              {entryPoint[0].toFixed(6)}, {entryPoint[1].toFixed(6)}
            </div>
          )}
        </div>

        <button
          className="generate-roads-button"
          onClick={handleGenerate}
          disabled={loading || !entryPoint}
        >
          {loading ? 'Generating...' : 'Generate Road Network'}
        </button>
      </div>

      {roadData && (
        <div className="road-stats">
          <div className="stat-item">
            <span className="stat-label">Total Length:</span>
            <span className="stat-value">{(roadData.totalLength / 5280).toFixed(2)} miles</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Road Segments:</span>
            <span className="stat-value">{roadData.roadCount}</span>
          </div>
        </div>
      )}
    </div>
  )
}

export default RoadNetwork
