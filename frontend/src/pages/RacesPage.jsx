import { useEffect, useState } from 'react'
import { getRaces } from '../api/f1Api'
import RaceCard from '../components/RaceCard'

function RacesPage() {
  const [races, setRaces] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function loadRaces() {
      try {
        const data = await getRaces()
        setRaces(data.results)
      } catch (error) {
        setError(error.message)
      } finally {
        setLoading(false)
      }
    }

    loadRaces()
  }, [])

  if (loading) {
    return <p>Loading races...</p>
  }

  if (error) {
    return <p>Error: {error}</p>
  }

  return (
    <main>
      <h1>Races</h1>

      {races.map(race => (
        <RaceCard
          key={race.id}
          race={race}
        />
      ))}
    </main>
  )
}

export default RacesPage