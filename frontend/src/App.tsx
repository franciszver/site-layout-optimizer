import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import LayoutEditor from './pages/LayoutEditor'
import LayoutLibrary from './pages/LayoutLibrary'
import './App.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/editor" element={<LayoutEditor />} />
        <Route path="/library" element={<LayoutLibrary />} />
      </Routes>
    </Router>
  )
}

export default App

