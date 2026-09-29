import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  getDriverStandings,
  getConstructorStandings
} from '../api/f1Api'

function StandingsPage() {
  const [driverStandings, setDriverStandings] = useState([])
  const [constructorStandings, setConstructorStandings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function loadStandings() {
      try {
        const [driversData, constructorsData] = await Promise.all([
          getDriverStandings(),
          getConstructorStandings()
        ])

        setDriverStandings(driversData.results)
        setConstructorStandings(constructorsData.results)
      } catch (error) {
        setError(error.message)
      } finally {
        setLoading(false)
      }
    }

    loadStandings()
  }, [])

  if (loading) {
    return <p>Loading standings...</p>
  }

  if (error) {
    return <p>Error: {error}</p>
  }

  return (
    <main>
      <h1>Standings</h1>

      <section>
        <h2>Driver Standings</h2>

        {driverStandings.map(standing => (
          <div key={standing.driver_id}>
            <p>
              {standing.position}.{' '}
              <Link to={`/drivers/${standing.number}`}>
                {standing.name}
              </Link>
              {' '}— {standing.points} pts
            </p>
          </div>
        ))}
      </section>

      <section>
        <h2>Constructor Standings</h2>

        {constructorStandings.map(standing => (
          <div key={standing.constructor_id}>
            <p>
              {standing.position}.{' '}
              <Link to={`/constructors/${standing.constructor_id}`}>
                {standing.name}
              </Link>
              {' '}— {standing.points} pts
            </p>
          </div>
        ))}
      </section>
    </main>
  )
}

export default StandingsPage