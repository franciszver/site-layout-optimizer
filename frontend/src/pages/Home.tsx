import { Link } from 'react-router-dom'
import './Home.css'

const Home = () => {
  return (
    <div className="home">
      <header className="home-header">
        <h1>Pacifico Energy Group</h1>
        <h2>Site Layout Optimizer</h2>
        <p>AI-Powered geospatial site layout optimization for resources</p>
      </header>
      <nav className="home-nav">
        <Link to="/editor" className="nav-button primary">
          Create New Layout
        </Link>
      </nav>
    </div>
  )
}

export default Home

