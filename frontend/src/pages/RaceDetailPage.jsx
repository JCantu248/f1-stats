import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getRace } from '../api/f1Api'

function RaceDetailPage() {
  const { raceId } = useParams()

  const [race, setRace] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function loadRace() {
      try {
        const data = await getRace(raceId)
        setRace(data)
      } catch (error) {
        setError(error.message)
      } finally {
        setLoading(false)
      }
    }

    loadRace()
  }, [raceId])

  if (loading) {
    return <p>Loading race...</p>
  }

  if (error) {
    return <p>Error: {error}</p>
  }

  return (
    <main>
      <h1>{race.name}</h1>

      <p>Season: {race.season}</p>
      <p>Round: {race.round_number}</p>
      <p>Date: {race.race_date}</p>
      <p>Status: {race.status}</p>

      <h2>Circuit</h2>

      <p>{race.circuit.name}</p>
      <p>
        {race.circuit.city}, {race.circuit.country}
      </p>

      <h2>Qualifying Results</h2>

      {race.qualifying_results.map(result => (
        <div key={result.id}>
          <p>
            P{result.finishing_position} - {result.driver.name}
          </p>
        </div>
      ))}

      <h2>Race Results</h2>

      {race.race_results?.map(result => (
        <div key={result.id}>
          <p>
            P{result.finishing_position} - {result.driver.name}
          </p>
          <p>Constructor: {result.constructor.name}</p>
          <p>Grid: {result.grid_position}</p>
          <p>Laps: {result.laps_completed}</p>
          <p>Points: {result.points}</p>
          <p>Status: {result.status}</p>
        </div>
      ))}
    </main>
  )
}

export default RaceDetailPage