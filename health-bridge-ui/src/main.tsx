import ReactDOM from "react-dom/client";
import App from './App.tsx'
import './index.css'
import { RecoilRoot } from "recoil";

// import { StrictMode } from 'react'
// import { createRoot } from 'react-dom/client'


// createRoot(document.getElementById('root')!).render(
//   <StrictMode>
//     <App />
//   </StrictMode>,
// )

ReactDOM.createRoot(document.getElementById("root")!).render(
  <RecoilRoot>
    <App />
  </RecoilRoot>
);
