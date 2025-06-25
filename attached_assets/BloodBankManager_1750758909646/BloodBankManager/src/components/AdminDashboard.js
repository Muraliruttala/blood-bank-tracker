import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

function AdminDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalRequests: 0,
    pendingRequests: 0,
    totalDonations: 0,
    totalUsers: 0
  });
  const [recentRequests, setRecentRequests] = useState([]);
  const [recentDonations, setRecentDonations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [requestsRes, donationsRes] = await Promise.all([
        axios.get('/api/blood-requests'),
        axios.get('/api/donations')
      ]);

      const requests = requestsRes.data.data || [];
      const donations = donationsRes.data.data || [];

      // Calculate stats
      const pendingRequests = requests.filter(req => req.status === 'pending');

      setStats({
        totalRequests: requests.length,
        pendingRequests: pendingRequests.length,
        totalDonations: donations.length,
        totalUsers: new Set([...requests.map(r => r.user_id), ...donations.map(d => d.donor_id)]).size
      });

      // Set recent data (last 5 items)
      setRecentRequests(requests.slice(-5).reverse());
      setRecentDonations(donations.slice(-5).reverse());

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateRequestStatus = async (requestId, status) => {
    try {
      await axios.put(`/api/blood-requests/${requestId}/status`, { status });
      setMessage(`Request ${status} successfully!`);
      fetchDashboardData(); // Refresh data
    } catch (error) {
      setMessage(error.response?.data?.message || 'Error updating request status');
    }
  };

  const updateDonationStatus = async (donationId, status) => {
    try {
      await axios.put(`/api/donations/${donationId}/status`, { status });
      setMessage(`Donation ${status} successfully!`);
      fetchDashboardData(); // Refresh data
    } catch (error) {
      setMessage(error.response?.data?.message || 'Error updating donation status');
    }
  };

  if (loading) {
    return <div>Loading admin dashboard...</div>;
  }

  return (
    <div>
      <h1>Admin Dashboard</h1>
      <p>Welcome, {user.name} - {user.hospital}</p>

      {message && (
        <div className={`alert ${message.includes('Error') ? 'alert-danger' : 'alert-success'}`}>
          {message}
        </div>
      )}

      {/* Statistics Cards */}
      <div className="row" style={{ marginBottom: '30px' }}>
        <div className="col-md-3">
          <div className="card" style={{ textAlign: 'center', backgroundColor: '#e3f2fd' }}>
            <h3>{stats.totalRequests}</h3>
            <p>Total Requests</p>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card" style={{ textAlign: 'center', backgroundColor: '#fff3e0' }}>
            <h3>{stats.pendingRequests}</h3>
            <p>Pending Requests</p>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card" style={{ textAlign: 'center', backgroundColor: '#e8f5e8' }}>
            <h3>{stats.totalDonations}</h3>
            <p>Total Donations</p>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card" style={{ textAlign: 'center', backgroundColor: '#f3e5f5' }}>
            <h3>{stats.totalUsers}</h3>
            <p>Active Users</p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <h3>Quick Actions</h3>
        <div style={{ display: 'flex', gap: '10px' }}>
          <a href="/inventory" className="btn btn-primary">
            Manage Inventory
          </a>
          <a href="/blood-requests" className="btn btn-success">
            View All Requests
          </a>
          <a href="/donations" className="btn btn-danger">
            View All Donations
          </a>
        </div>
      </div>

      {/* Recent Blood Requests */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <h3>Recent Blood Requests</h3>
        {recentRequests.length > 0 ? (
          <table className="table">
            <thead>
              <tr>
                <th>Requester</th>
                <th>Hospital</th>
                <th>Blood Type</th>
                <th>Units</th>
                <th>Urgency</th>
                <th>Status</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {recentRequests.map(request => (
                <tr key={request.id}>
                  <td>{request.requester_name}</td>
                  <td>{request.hospital}</td>
                  <td>{request.blood_type}</td>
                  <td>{request.units}</td>
                  <td>
                    <span style={{
                      padding: '4px 8px',
                      borderRadius: '4px',
                      backgroundColor: request.urgency === 'urgent' ? '#f8d7da' : '#d4edda',
                      color: request.urgency === 'urgent' ? '#721c24' : '#155724'
                    }}>
                      {request.urgency}
                    </span>
                  </td>
                  <td>
                    <span style={{
                      padding: '4px 8px',
                      borderRadius: '4px',
                      backgroundColor: request.status === 'pending' ? '#fff3cd' : 
                                      request.status === 'successful' ? '#d4edda' : '#f8d7da',
                      color: request.status === 'pending' ? '#856404' : 
                             request.status === 'successful' ? '#155724' : '#721c24'
                    }}>
                      {request.status}
                    </span>
                  </td>
                  <td>{new Date(request.created_at).toLocaleDateString()}</td>
                  <td>
                    {request.status === 'pending' && (
                      <div style={{ display: 'flex', gap: '5px' }}>
                        <button
                          onClick={() => updateRequestStatus(request.id, 'successful')}
                          className="btn btn-success"
                          style={{ fontSize: '12px', padding: '4px 8px' }}
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => updateRequestStatus(request.id, 'rejected')}
                          className="btn btn-danger"
                          style={{ fontSize: '12px', padding: '4px 8px' }}
                        >
                          Reject
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No blood requests found.</p>
        )}
      </div>

      {/* Recent Donations */}
      <div className="card">
        <h3>Recent Donations</h3>
        {recentDonations.length > 0 ? (
          <table className="table">
            <thead>
              <tr>
                <th>Donor</th>
                <th>Date</th>
                <th>Time</th>
                <th>Hospital</th>
                <th>Blood Type</th>
                <th>Status</th>
                <th>Contact</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {recentDonations.map(donation => (
                <tr key={donation.id}>
                  <td>{donation.donor_name}</td>
                  <td>{donation.donation_date}</td>
                  <td>{donation.donation_time}</td>
                  <td>{donation.hospital}</td>
                  <td>{donation.blood_type}</td>
                  <td>
                    <span style={{
                      padding: '4px 8px',
                      borderRadius: '4px',
                      backgroundColor: donation.status === 'scheduled' ? '#fff3cd' : 
                                      donation.status === 'completed' ? '#d4edda' : '#f8d7da',
                      color: donation.status === 'scheduled' ? '#856404' : 
                             donation.status === 'completed' ? '#155724' : '#721c24'
                    }}>
                      {donation.status}
                    </span>
                  </td>
                  <td>{donation.contact_number}</td>
                  <td>
                    {donation.status === 'scheduled' && (
                      <div style={{ display: 'flex', gap: '5px' }}>
                        <button
                          onClick={() => updateDonationStatus(donation.id, 'completed')}
                          className="btn btn-success"
                          style={{ fontSize: '12px', padding: '4px 8px' }}
                        >
                          Complete
                        </button>
                        <button
                          onClick={() => updateDonationStatus(donation.id, 'cancelled')}
                          className="btn btn-danger"
                          style={{ fontSize: '12px', padding: '4px 8px' }}
                        >
                          Cancel
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No donations scheduled.</p>
        )}
      </div>
    </div>
  );
}

export default AdminDashboard;