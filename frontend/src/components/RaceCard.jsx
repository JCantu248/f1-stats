import { Link } from 'react-router-dom'

function RaceCard({ race }) {
  return (
    <div>
        <h2>
            <Link to={`/races/${race.id}`}>
                {race.name}
            </Link>
        </h2>
    </div>
  )
}

export default RaceCard