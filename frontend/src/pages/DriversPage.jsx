import { useEffect, useState } from 'react'
import { getDrivers } from '../api/f1Api'
import { Link } from 'react-router-dom'

function DriversPage() {
  const [drivers, setDrivers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function loadDrivers() {
      try {
        const data = await getDrivers()
        setDrivers(data.results)
      } catch (error) {
        setError(error.message)
      } finally {
        setLoading(false)
      }
    }

    loadDrivers()
  }, [])

  if (loading) {
    return <p>Loading drivers...</p>
  }

  if (error) {
    return <p>Error: {error}</p>
  }

  return (
    <div>
      <h1>Drivers</h1>

      {drivers.map(driver => (
        <div key={driver.id}>
            <h2>
            <Link to={`/drivers/${driver.number}`}>
                {driver.name}
            </Link>
            </h2>

            <p>Number: {driver.number}</p>
        </div>
        ))}
    </div>
  )
}

export default DriversPage