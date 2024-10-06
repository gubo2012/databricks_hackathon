import './App.css';
import Header from "./compoents/common/header/header";
import LeftMenu from './compoents/common/left-menu/left-menu';
import { Col, Row } from 'reactstrap';
import { AppRouter } from './router';


// import { useState } from 'react'
// import reactLogo from './assets/react.svg'
// import viteLogo from '/vite.svg'
// import './App.css'

function App() {
  // const [count, setCount] = useState(0)

  return (
    <>
      <Header></Header>
      <Row className="app-body">
        <Col sm="2">
          <LeftMenu />
        </Col>
        <Col sm="10">
          <AppRouter />
        </Col>
      </Row>
      {/* <div>
        <a href="https://vitejs.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.tsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p> */}
    </>
  )
}

export default App
