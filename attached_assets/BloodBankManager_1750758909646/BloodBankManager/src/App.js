import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import AdminDashboard from './components/AdminDashboard';
import BloodRequests from './components/BloodRequests';
import Donations from './components/Donations';
import Inventory from './components/Inventory';
import { AuthProvider, useAuth } from './context/AuthContext';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Navbar />
          <div className="container">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="/admin" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
              <Route path="/blood-requests" element={<ProtectedRoute><BloodRequests /></ProtectedRoute>} />
              <Route path="/donations" element={<ProtectedRoute><Donations /></ProtectedRoute>} />
              <Route path="/inventory" element={<AdminRoute><Inventory /></AdminRoute>} />
              <Route path="/" element={<Home />} />
            </Routes>
          </div>
        </div>
      </Router>
    </AuthProvider>
  );
}

function Home() {
  const { user } = useAuth();
  
  if (user) {
    return user.role === 'admin' ? <Navigate to="/admin" /> : <Navigate to="/dashboard" />;
  }
  
  return (
    <div className="card">
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <h1 style={{ color: '#dc3545', marginBottom: '20px' }}>
          🩸 Blood Bank Management System
        </h1>
        <p style={{ fontSize: '18px', marginBottom: '30px' }}>
          Connecting donors with those in need. Save lives through blood donation.
        </p>
        <div>
          <a href="/login" className="btn btn-primary" style={{ marginRight: '10px' }}>
            Login
          </a>
          <a href="/register" className="btn btn-success">
            Register
          </a>
        </div>
      </div>
    </div>
  );
}

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return user ? children : <Navigate to="/login" />;
}

function AdminRoute({ children }) {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return user && user.role === 'admin' ? children : <Navigate to="/dashboard" />;
}

export default App;