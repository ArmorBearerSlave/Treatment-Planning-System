import { DicomViewer } from './components/DicomViewer'

function App() {
  return (
    <main style={{ padding: '1rem', fontFamily: 'sans-serif' }}>
      <h1>NL-TPS Cornerstone3D Prototype</h1>
      <p>Independent prototype, not yet traced to the NL-TPS requirements suite.</p>
      <DicomViewer />
    </main>
  )
}

export default App

