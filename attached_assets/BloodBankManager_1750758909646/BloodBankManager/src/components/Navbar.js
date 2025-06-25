import React from 'react';
import { useAuth } from '../context/AuthContext';

function Navbar() {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    window.location.href = '/';
  };

  return (
    <nav className="navbar">
      <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <a href="/" className="navbar-brand">
          🩸 Blood Bank System
        </a>
        
        {user && (
          <ul className="navbar-nav" style={{ display: 'flex', alignItems: 'center' }}>
            <li>
              <a href="/dashboard" className="nav-link">Dashboard</a>
            </li>
            <li>
              <a href="/blood-requests" className="nav-link">Blood Requests</a>
            </li>
            <li>
              <a href="/donations" className="nav-link">Donations</a>
            </li>
            {user.role === 'admin' && (
              <>
                <li>
                  <a href="/inventory" className="nav-link">Inventory</a>
                </li>
                <li>
                  <a href="/admin" className="nav-link">Admin Panel</a>
                </li>
              </>
            )}
            <li>
              <span className="nav-link" style={{ color: '#fff', opacity: 0.8 }}>
                Welcome, {user.name}
              </span>
            </li>
            <li>
              <button onClick={handleLogout} className="btn btn-danger" style={{ fontSize: '14px' }}>
                Logout
              </button>
            </li>
          </ul>
        )}
      </div>
    </nav>
  );
}

export default Navbar;