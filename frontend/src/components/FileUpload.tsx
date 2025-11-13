import { useState } from 'react'
import './FileUpload.css'

interface FileUploadProps {
  onUpload: (file: File) => void
  acceptedTypes?: string[]
}

const FileUpload = ({ onUpload, acceptedTypes = ['.kmz', '.kml', '.geojson'] }: FileUploadProps) => {
  const [dragging, setDragging] = useState(false)
  const [fileInput, setFileInput] = useState<HTMLInputElement | null>(null)

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    console.log('FileUpload: handleDrop called')
    const file = e.dataTransfer.files[0]
    console.log('FileUpload: dropped file:', file?.name, file?.size)
    if (file) {
      console.log('FileUpload: calling onUpload with file')
      onUpload(file)
    } else {
      console.warn('FileUpload: No file in drop event')
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log('FileUpload: handleFileSelect called')
    const file = e.target.files?.[0]
    console.log('FileUpload: selected file:', file?.name, file?.size)
    if (file) {
      console.log('FileUpload: calling onUpload with file')
      onUpload(file)
    } else {
      console.warn('FileUpload: No file selected')
    }
  }

  const handleClick = () => {
    fileInput?.click()
  }

  return (
    <div
      className={`file-upload ${dragging ? 'dragging' : ''}`}
      onDragOver={(e) => {
        e.preventDefault()
        setDragging(true)
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={handleClick}
    >
      <input
        ref={(el) => setFileInput(el)}
        type="file"
        accept={acceptedTypes.join(',')}
        onChange={handleFileSelect}
        style={{ display: 'none' }}
        id="file-upload-input"
      />
      <div className="upload-content">
        <svg className="upload-icon" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="17 8 12 3 7 8"></polyline>
          <line x1="12" y1="3" x2="12" y2="15"></line>
        </svg>
        <p className="upload-text">Drag and drop files here</p>
        <p className="upload-text-secondary">or click to browse</p>
        <p className="upload-hint">Accepted formats: {acceptedTypes.join(', ')}</p>
      </div>
    </div>
  )
}

export default FileUpload
