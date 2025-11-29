import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Landing from './pages/Landing'
import Verify from './pages/Verify'
import Dashboard from './pages/Dashboard'
import './index.css'

function App() {
  return (
    <Router>
      {/* Background Effects */}
      <div className="bg-gradient"></div>
      <div className="bg-grid"></div>

      {/* Navigation */}
      <Navbar />

      {/* Routes */}
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/verify" element={<Verify />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/blockchain" element={<BlockchainPage />} />
      </Routes>
    </Router>
  )
}

export default App
