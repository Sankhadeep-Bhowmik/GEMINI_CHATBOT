import { useState } from 'react'

import './App.css'
import ChatBot from './components/ChatBot'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div>
      <ChatBot/>
    </div>
  )
}

export default App
