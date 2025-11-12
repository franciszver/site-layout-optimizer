import { useState } from 'react'
import api from '../services/api'
import './ReportExport.css'

interface ReportExportProps {
  layoutId?: string
  layoutData?: any
  onExport?: (format: string) => void
}

const ReportExport = ({ layoutId, layoutData, onExport }: ReportExportProps) => {
  const [exporting, setExporting] = useState(false)
  const [exportFormat, setExportFormat] = useState<string>('pdf')

  const handleExport = async () => {
    if (!layoutId) {
      alert('No layout to export. Please complete the layout workflow first.')
      return
    }
    
    if (!layoutData) {
      alert('No layout data available. Please upload a property and optimize the layout first.')
      return
    }

    setExporting(true)
    try {
      const response = await api.post(
        '/export',
        {
          layout_id: layoutId,
          format: exportFormat,
          layout_data: layoutData,  // Send full layout data
          include_statistics: true,
        },
        {
          responseType: exportFormat === 'geojson' ? 'json' : 'blob',  // Binary for PDF/KMZ, JSON for GeoJSON
        }
      )

      if (exportFormat === 'geojson') {
        // Handle JSON response
        const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `layout_${layoutId}.geojson`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
      } else {
        // Handle binary file download (PDF, KMZ)
        const blob = new Blob([response.data], { 
          type: exportFormat === 'pdf' ? 'application/pdf' : 'application/vnd.google-earth.kmz'
        })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `layout_${layoutId}.${exportFormat}`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
      }

      if (onExport) {
        onExport(exportFormat)
      }
    } catch (error: any) {
      console.error('Export error:', error)
      alert('Error exporting layout: ' + (error.response?.data?.detail || error.message))
    } finally {
      setExporting(false)
    }
  }

  return (
    <div className="report-export">
      <div className="export-options">
        <label>Export Format:</label>
        <select
          value={exportFormat}
          onChange={(e) => setExportFormat(e.target.value)}
          disabled={exporting}
        >
          <option value="pdf">PDF Report</option>
          <option value="kmz">KMZ (Google Earth)</option>
          <option value="geojson">GeoJSON</option>
        </select>
      </div>

      <button
        className="export-button"
        onClick={handleExport}
        disabled={exporting || !layoutId}
      >
        {exporting ? 'Exporting...' : 'Export Layout'}
      </button>

      {layoutId && (
        <div className="export-info">
          <p>Layout ID: {layoutId}</p>
        </div>
      )}
    </div>
  )
}

export default ReportExport
