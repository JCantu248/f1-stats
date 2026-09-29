import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getConstructors } from '../api/f1Api'

function ConstructorsPage() {
  const [constructors, setConstructors] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

    useEffect(() => {
        async function loadConstructors() {
            try {
            const data = await getConstructors()
            setConstructors(data.results)
            } catch (error) {
            setError(error.message)
            } finally {
            setLoading(false)
            }
        }

        loadConstructors()
    }, [])

  if (loading) {
    return <p>Loading constructors...</p>
  }

  if (error) {
    return <p>Error: {error}</p>
  }

  return (
    <main>
      <h1>Constructors</h1>

      {constructors.map(constructor => (
        <div key={constructor.id}>
          <h2>
            <Link to={`/constructors/${constructor.id}`}>
              {constructor.name}
            </Link>
          </h2>
        </div>
      ))}
    </main>
  )
}

export default ConstructorsPage