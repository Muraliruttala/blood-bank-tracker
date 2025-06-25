import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

function BloodRequests() {
  const { user } = useAuth();
  const [requests, setRequests] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    hospital: '',
    blood_type: '',
    units: '',
    urgency: 'normal',
    notes: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchRequests();
  }, []);

  const fetchRequests = async () => {
    try {
      const response = await axios.get('/api/blood-requests');
      setRequests(response.data.data || []);
    } catch (error) {
      console.error('Error fetching requests:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const requestData = {
        ...formData,
        units: parseInt(formData.units)
      };

      await axios.post('/api/blood-requests', requestData);
      
      setMessage('Blood request submitted successfully!');
      setShowForm(false);
      setFormData({
        hospital: '',
        blood_type: '',
        units: '',
        urgency: 'normal',
        notes: ''
      });
      
      fetchRequests();
    } catch (error) {
      setMessage(error.response?.data?.message || 'Error submitting request');
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

  // Filter requests for current user
  const myRequests = requests.filter(req => req.user_id === user.id);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Blood Requests</h1>
        <button 
          onClick={() => setShowForm(!showForm)} 
          className="btn btn-primary"
        >
          {showForm ? 'Cancel' : 'New Request'}
        </button>
      </div>

      {message && (
        <div className={`alert ${message.includes('Error') ? 'alert-danger' : 'alert-success'}`}>
          {message}
        </div>
      )}

      {showForm && (
        <div className="card" style={{ marginBottom: '20px' }}>
          <h3>Submit Blood Request</h3>
          <form onSubmit={handleSubmit}>
            <div className="row">
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
            </div>

            <div className="row">
              <div className="col-md-6">
                <div className="form-group">
                  <label>Units Required:</label>
                  <input
                    type="number"
                    name="units"
                    className="form-control"
                    value={formData.units}
                    onChange={handleChange}
                    min="1"
                    max="10"
                    required
                  />
                </div>
              </div>
              <div className="col-md-6">
                <div className="form-group">
                  <label>Urgency:</label>
                  <select
                    name="urgency"
                    className="form-control"
                    value={formData.urgency}
                    onChange={handleChange}
                  >
                    <option value="normal">Normal</option>
                    <option value="urgent">Urgent</option>
                  </select>
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

            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Submitting...' : 'Submit Request'}
            </button>
          </form>
        </div>
      )}

      <div className="card">
        <h3>My Blood Requests</h3>
        {myRequests.length > 0 ? (
          <table className="table">
            <thead>
              <tr>
                <th>Hospital</th>
                <th>Blood Type</th>
                <th>Units</th>
                <th>Urgency</th>
                <th>Status</th>
                <th>Date</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {myRequests.map(request => (
                <tr key={request.id}>
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
                  <td>{request.notes || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No blood requests found. Click "New Request" to submit your first request.</p>
        )}
      </div>
    </div>
  );
}

export default BloodRequests;