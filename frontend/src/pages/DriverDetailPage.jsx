import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getDriver } from '../api/f1Api'

function DriverDetailPage() {
  const { driverNumber } = useParams()

  const [driver, setDriver] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function loadDriver() {
      try {
        const data = await getDriver(driverNumber)
        setDriver(data)
      } catch (error) {
        setError(error.message)
      } finally {
        setLoading(false)
      }
    }

    loadDriver()
  }, [driverNumber])

  if (loading) {
    return <p>Loading driver...</p>
  }

  if (error) {
    return <p>Error: {error}</p>
  }

  return (
    <main>
      <h1>{driver.name}</h1>

      <p>Number: {driver.number}</p>
      <p>Nationality: {driver.nationality}</p>

      <h2>Career Entries</h2>

      {driver.entries.map(entry => (
        <div key={`${entry.season}-${entry.constructor.id}`}>
          <h3>{entry.season}</h3>

          <p>
            Constructor:{' '}
            <Link to={`/constructors/${entry.constructor.id}`}>
              {entry.constructor.name}
            </Link>
          </p>

          <p>Car: {entry.racecar}</p>
        </div>
      ))}
    </main>
  )
}

export default DriverDetailPage