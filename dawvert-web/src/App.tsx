import { useState } from 'react'
import './App.css'
import { Button } from "@/components/ui/button"
import './globals.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <h1>h1 tag</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
      </div>
      <div>
        <Button>Click me</Button>
      </div>
    </>
  )
}

export default App
