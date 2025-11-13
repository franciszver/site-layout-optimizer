import { useState, ReactNode } from 'react'
import './StepSection.css'

interface StepSectionProps {
  stepNumber: number
  title: string
  isCompleted: boolean
  isActive: boolean
  children: ReactNode
  onNext?: () => void
  onPrevious?: () => void
  canProceed?: boolean
}

const StepSection = ({
  stepNumber,
  title,
  isCompleted,
  isActive,
  children,
  onNext,
  onPrevious,
  canProceed = false
}: StepSectionProps) => {
  const [isExpanded, setIsExpanded] = useState(isActive || isCompleted)

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded)
  }

  return (
    <div className={`step-section ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}>
      <div className="step-header" onClick={toggleExpanded}>
        <div className="step-number">{stepNumber}</div>
        <div className="step-title">
          <span>{title}</span>
          {isCompleted && <span className="step-check">✓</span>}
        </div>
        <div className="step-toggle">
          {isExpanded ? '▼' : '▶'}
        </div>
      </div>
      {isExpanded && (
        <div className="step-content">
          {children}
          {isActive && (
            <div className="step-navigation">
              {onPrevious && stepNumber > 1 && (
                <button className="step-nav-button prev" onClick={onPrevious}>
                  ← Previous
                </button>
              )}
              {onNext && canProceed && (
                <button className="step-nav-button next" onClick={onNext}>
                  Next →
                </button>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default StepSection

