import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

function Donations() {
  const { user } = useAuth();
  const [donations, setDonations] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    donor_name: user?.name || '',
    donation_date: '',
    donation_time: '',
    blood_type: user?.blood_group || '',
    contact_number: user?.mobile || '',
    hospital: '',
    notes: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchDonations();
    // Update form data when user is available
    if (user) {
      setFormData(prev => ({
        ...prev,
        donor_name: user.name,
        blood_type: user.blood_group,
        contact_number: user.mobile
      }));
    }
  }, [user]);

  const fetchDonations = async () => {
    try {
      const response = await axios.get('/api/donations');
      setDonations(response.data.data || []);
    } catch (error) {
      console.error('Error fetching donations:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      await axios.post('/api/donations', formData);
      
      setMessage('Donation scheduled successfully!');
      setShowForm(false);
      setFormData({
        donor_name: user.name,
        donation_date: '',
        donation_time: '',
        blood_type: user.blood_group,
        contact_number: user.mobile,
        hospital: '',
        notes: ''
      });
      
      fetchDonations();
    } catch (error) {
      setMessage(error.response?.data?.message || 'Error scheduling donation');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const bloodGroups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];

  // Filter donations for current user
  const myDonations = donations.filter(don => don.donor_id === user.id);

  // Get today's date for min date validation
  const today = new Date().toISOString().split('T')[0];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Blood Donations</h1>
        <button 
          onClick={() => setShowForm(!showForm)} 
          className="btn btn-success"
        >
          {showForm ? 'Cancel' : 'Schedule Donation'}
        </button>
      </div>

      {message && (
        <div className={`alert ${message.includes('Error') ? 'alert-danger' : 'alert-success'}`}>
          {message}
        </div>
      )}

      {showForm && (
        <div className="card" style={{ marginBottom: '20px' }}>
          <h3>Schedule Blood Donation</h3>
          <form onSubmit={handleSubmit}>
            <div className="row">
              <div className="col-md-6">
                <div className="form-group">
                  <label>Donor Name:</label>
                  <input
                    type="text"
                    name="donor_name"
                    className="form-control"
                    value={formData.donor_name}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>
              <div className="col-md-6">
                <div className="form-group">
                  <label>Contact Number:</label>
                  <input
                    type="tel"
                    name="contact_number"
                    className="form-control"
                    value={formData.contact_number}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>
            </div>

            <div className="row">
              <div className="col-md-6">
                <div className="form-group">
                  <label>Donation Date:</label>
                  <input
                    type="date"
                    name="donation_date"
                    className="form-control"
                    value={formData.donation_date}
                    onChange={handleChange}
                    min={today}
                    required
                  />
                </div>
              </div>
              <div className="col-md-6">
                <div className="form-group">
                  <label>Donation Time:</label>
                  <input
                    type="time"
                    name="donation_time"
                    className="form-control"
                    value={formData.donation_time}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>
            </div>

            <div className="row">
              <div className="col-md-6">
                <div className="form-group">
                  <label>Blood Type:</label>
                  <select
                    name="blood_type"
                    className="form-control"
                    value={formData.blood_type}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Select Blood Type</option>
                    {bloodGroups.map(group => (
                      <option key={group} value={group}>{group}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="col-md-6">
                <div className="form-group">
                  <label>Hospital:</label>
                  <input
                    type="text"
                    name="hospital"
                    className="form-control"
                    value={formData.hospital}
                    onChange={handleChange}
                    placeholder="Enter hospital name"
                    required
                  />
                </div>
              </div>
            </div>

            <div className="form-group">
              <label>Notes (Optional):</label>
              <textarea
                name="notes"
                className="form-control"
                value={formData.notes}
                onChange={handleChange}
                rows="3"
                placeholder="Additional information..."
              />
            </div>

            <button type="submit" className="btn btn-success" disabled={loading}>
              {loading ? 'Scheduling...' : 'Schedule Donation'}
            </button>
          </form>
        </div>
      )}

      <div className="card">
        <h3>My Scheduled Donations</h3>
        {myDonations.length > 0 ? (
          <table className="table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Time</th>
                <th>Hospital</th>
                <th>Blood Type</th>
                <th>Status</th>
                <th>Scheduled On</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {myDonations.map(donation => (
                <tr key={donation.id}>
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
                  <td>{new Date(donation.created_at).toLocaleDateString()}</td>
                  <td>{donation.notes || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No donations scheduled yet. Click "Schedule Donation" to schedule your first donation.</p>
        )}
      </div>
    </div>
  );
}

export default Donations;