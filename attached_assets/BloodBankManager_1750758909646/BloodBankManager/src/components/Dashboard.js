import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    myRequests: 0,
    myDonations: 0,
    pendingRequests: 0
  });
  const [recentRequests, setRecentRequests] = useState([]);
  const [recentDonations, setRecentDonations] = useState([]);
  const [loading, setLoading] = useState(true);

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
      const myRequests = requests.filter(req => req.user_id === user.id);
      const myDonations = donations.filter(don => don.donor_id === user.id);
      const pendingRequests = myRequests.filter(req => req.status === 'pending');

      setStats({
        myRequests: myRequests.length,
        myDonations: myDonations.length,
        pendingRequests: pendingRequests.length
      });

      // Set recent data (last 3 items)
      setRecentRequests(myRequests.slice(-3).reverse());
      setRecentDonations(myDonations.slice(-3).reverse());

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Loading dashboard...</div>;
  }

  return (
    <div>
      <h1>Welcome, {user.name}!</h1>
      <p>Blood Group: <strong>{user.blood_group}</strong></p>

      {/* Statistics Cards */}
      <div className="row" style={{ marginBottom: '30px' }}>
        <div className="col-md-4">
          <div className="card" style={{ textAlign: 'center', backgroundColor: '#e3f2fd' }}>
            <h3>{stats.myRequests}</h3>
            <p>Total Blood Requests</p>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card" style={{ textAlign: 'center', backgroundColor: '#e8f5e8' }}>
            <h3>{stats.myDonations}</h3>
            <p>Total Donations</p>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card" style={{ textAlign: 'center', backgroundColor: '#fff3e0' }}>
            <h3>{stats.pendingRequests}</h3>
            <p>Pending Requests</p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h3>Quick Actions</h3>
        <div style={{ display: 'flex', gap: '10px' }}>
          <a href="/blood-requests" className="btn btn-primary">
            Make Blood Request
          </a>
          <a href="/donations" className="btn btn-success">
            Schedule Donation
          </a>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="row">
        <div className="col-md-6">
          <div className="card">
            <h3>Recent Blood Requests</h3>
            {recentRequests.length > 0 ? (
              <table className="table">
                <thead>
                  <tr>
                    <th>Blood Type</th>
                    <th>Units</th>
                    <th>Status</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {recentRequests.map(request => (
                    <tr key={request.id}>
                      <td>{request.blood_type}</td>
                      <td>{request.units}</td>
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
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p>No blood requests yet.</p>
            )}
          </div>
        </div>

        <div className="col-md-6">
          <div className="card">
            <h3>Recent Donations</h3>
            {recentDonations.length > 0 ? (
              <table className="table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Hospital</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {recentDonations.map(donation => (
                    <tr key={donation.id}>
                      <td>{donation.donation_date}</td>
                      <td>{donation.donation_time}</td>
                      <td>{donation.hospital}</td>
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
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p>No donations scheduled yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;