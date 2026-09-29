import { Link } from 'react-router-dom'

function NavBar() {
  return (
    <nav>
      <h2>F1 Stats</h2>

      <Link to="/races"> Races </Link>
      <Link to="/drivers"> Drivers </Link>
      <Link to="/constructors"> Constructors </Link>
      <Link to="/standings">Standings</Link>
    </nav>
  )
}

export default NavBar