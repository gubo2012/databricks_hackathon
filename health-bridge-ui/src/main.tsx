import ReactDOM from "react-dom/client";
import App from './App.tsx'
import "bootstrap/dist/css/bootstrap.min.css"
import './index.css'
import { RecoilRoot } from "recoil";

import { HashRouter } from "react-router-dom";

// import { StrictMode } from 'react'
// import { createRoot } from 'react-dom/client'


// createRoot(document.getElementById('root')!).render(
//   <StrictMode>
//     <App />
//   </StrictMode>,
// )

ReactDOM.createRoot(document.getElementById("root")!).render(
  <RecoilRoot>
    <HashRouter>
      <App />
    </HashRouter>
  </RecoilRoot>
);
