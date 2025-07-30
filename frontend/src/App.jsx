import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import AdminPage from './pages/Admin/AdminPage';
import ShopPage from './pages/Shop/ShopPage';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<ShopPage />} />
        <Route path="/admin" element={<AdminPage />} />
      </Routes>
    </Router>
  );
};

export default App;
