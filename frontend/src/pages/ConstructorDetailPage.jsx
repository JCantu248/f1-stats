import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getConstructor } from '../api/f1Api'

function ConstructorDetailPage() {
  const { constructorId } = useParams()

  const [constructor, setConstructor] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function loadConstructor() {
        try {
        const data = await getConstructor(constructorId)
        setConstructor(data)
        } catch (error) {
        setError(error.message)
        } finally {
        setLoading(false)
        }
    }

    loadConstructor()
   }, [constructorId])

  if (loading) {
    return <p>Loading constructor...</p>
  }

  if (error) {
    return <p>Error: {error}</p>
  }

  return (
    <main>
      <h1>{constructor.name}</h1>

      <p>Nation: {constructor.nation}</p>

      <h2>Drivers</h2>

      {constructor.entries.map(entry => (
        <div key={`${entry.season}-${entry.driver.id}`}>
          <h3>{entry.season}</h3>

          <p>
            Driver:{' '}
            <Link to={`/drivers/${entry.driver.number}`}>
              {entry.driver.name}
            </Link>
          </p>

          <p>Car: {entry.racecar}</p>
        </div>
      ))}
    </main>
  )
}

export default ConstructorDetailPage