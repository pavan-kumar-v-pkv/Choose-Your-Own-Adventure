import './App.css'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import StoryGenerator from './components/StoryGenerator.jsx';
import StoryLoader from './components/StoryLoader.jsx';
import StoryGame from './components/StoryGame.jsx';

function App() {

  return (
    <Router>
      <div className="app-container">
        <header>
          <h1>Interactive Story Generator</h1>
        </header>
        <main>
        <Routes>
          <Route path="/" element={<StoryGenerator />} />
          <Route path="/stories/:id" element={<StoryLoader />} />
          <Route path="/play/:id" element={<StoryGame />} />
        </Routes>

        </main>
      </div>
    </Router>
  )
}

export default App
