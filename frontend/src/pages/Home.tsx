import { Link } from 'react-router-dom'
import './Home.css'

const Home = () => {
  return (
    <div className="home">
      <header className="home-header">
        <h1>Pacifico Energy Group</h1>
        <h2>Site Layout Optimizer</h2>
        <p>AI-powered geospatial site layout optimization for real estate due diligence</p>
      </header>
      <nav className="home-nav">
        <Link to="/editor" className="nav-button primary">
          Create New Layout
        </Link>
        <Link to="/library" className="nav-button secondary">
          View Layout Library
        </Link>
      </nav>
    </div>
  )
}

export default Home

