import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import NavBar from './components/NavBar'
import RacesPage from './pages/RacesPage'
import DriversPage from './pages/DriversPage'
import ConstructorsPage from './pages/ConstructorsPage'
import DriverDetailPage from './pages/DriverDetailPage'
import RaceDetailPage from './pages/RaceDetailPage'
import ConstructorDetailPage from './pages/ConstructorDetailPage'
import StandingsPage from './pages/StandingsPage'

function App() {
  return (
    <BrowserRouter>
      <NavBar />

      <Routes>
        <Route path="/" element={<Navigate to="/races" replace />} />
        <Route path="/races" element={<RacesPage />} />
        <Route path="/drivers" element={<DriversPage />} />
        <Route path="/constructors" element={<ConstructorsPage />} />
        <Route
          path="/drivers/:driverNumber"
          element={<DriverDetailPage />}
        />
        <Route path="/races/:raceId" element={<RaceDetailPage />} />
        <Route
          path="/constructors/:constructorId"
          element={<ConstructorDetailPage />}
        />
        <Route path="/standings" element={<StandingsPage /> } />
      </Routes>
    </BrowserRouter>
  )
}

export default App