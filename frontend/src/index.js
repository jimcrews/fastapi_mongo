import React from 'react';
import ReactDOM from 'react-dom/client';

import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";



import Car from './pages/Car'
import Cars from './pages/Cars'
import NewCar from './pages/NewCar'



import './index.css';
import App from './App';


const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  
  <React.StrictMode>
      <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="cars" element={<Cars />} />
        <Route path="new" element={<NewCar />} />
        <Route path="cars/:id" element={<Car />} />
        <Route path="*" element={
        <main style={{ padding: "1rem" }}>
          <p>There's nothing here!</p>
        </main>
      }
    />
      </Routes>
    </BrowserRouter>
    </React.StrictMode>

);
