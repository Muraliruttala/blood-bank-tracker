import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Inventory() {
  const [inventory, setInventory] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    hospital: '',
    blood_type: '',
    units_available: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchInventory();
  }, []);

  const fetchInventory = async () => {
    try {
      const response = await axios.get('/api/inventory');
      setInventory(response.data.data || []);
    } catch (error) {
      console.error('Error fetching inventory:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const inventoryData = {
        ...formData,
        units_available: parseInt(formData.units_available)
      };

      await axios.put('/api/inventory', inventoryData);
      
      setMessage('Inventory updated successfully!');
      setShowForm(false);
      setFormData({
        hospital: '',
        blood_type: '',
        units_available: ''
      });
      
      fetchInventory();
    } catch (error) {
      setMessage(error.response?.data?.message || 'Error updating inventory');
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

  // Group inventory by hospital
  const inventoryByHospital = inventory.reduce((acc, item) => {
    if (!acc[item.hospital]) {
      acc[item.hospital] = [];
    }
    acc[item.hospital].push(item);
    return acc;
  }, {});

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Blood Inventory Management</h1>
        <button 
          onClick={() => setShowForm(!showForm)} 
          className="btn btn-primary"
        >
          {showForm ? 'Cancel' : 'Update Inventory'}
        </button>
      </div>

      {message && (
        <div className={`alert ${message.includes('Error') ? 'alert-danger' : 'alert-success'}`}>
          {message}
        </div>
      )}

      {showForm && (
        <div className="card" style={{ marginBottom: '20px' }}>
          <h3>Update Blood Inventory</h3>
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

            <div className="form-group">
              <label>Units Available:</label>
              <input
                type="number"
                name="units_available"
                className="form-control"
                value={formData.units_available}
                onChange={handleChange}
                min="0"
                placeholder="Enter number of units"
                required
              />
            </div>

            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Updating...' : 'Update Inventory'}
            </button>
          </form>
        </div>
      )}

      {/* Inventory Summary */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <h3>Inventory Summary</h3>
        <div className="row">
          {bloodGroups.map(bloodType => {
            const totalUnits = inventory
              .filter(item => item.blood_type === bloodType)
              .reduce((sum, item) => sum + parseInt(item.units_available || 0), 0);
            
            return (
              <div key={bloodType} className="col-md-3" style={{ marginBottom: '10px' }}>
                <div style={{
                  textAlign: 'center',
                  padding: '10px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  backgroundColor: totalUnits > 0 ? '#d4edda' : '#f8d7da'
                }}>
                  <strong>{bloodType}</strong><br/>
                  {totalUnits} units
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Detailed Inventory by Hospital */}
      {Object.keys(inventoryByHospital).length > 0 ? (
        Object.entries(inventoryByHospital).map(([hospital, items]) => (
          <div key={hospital} className="card" style={{ marginBottom: '20px' }}>
            <h3>{hospital}</h3>
            <table className="table">
              <thead>
                <tr>
                  <th>Blood Type</th>
                  <th>Units Available</th>
                  <th>Last Updated</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {items.map(item => {
                  const units = parseInt(item.units_available || 0);
                  return (
                    <tr key={item.id}>
                      <td>{item.blood_type}</td>
                      <td>{units}</td>
                      <td>{new Date(item.updated_at).toLocaleDateString()}</td>
                      <td>
                        <span style={{
                          padding: '4px 8px',
                          borderRadius: '4px',
                          backgroundColor: units > 10 ? '#d4edda' : 
                                          units > 5 ? '#fff3cd' : '#f8d7da',
                          color: units > 10 ? '#155724' : 
                                 units > 5 ? '#856404' : '#721c24'
                        }}>
                          {units > 10 ? 'Good Stock' : 
                           units > 5 ? 'Low Stock' : 'Critical'}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ))
      ) : (
        <div className="card">
          <p>No inventory data available. Click "Update Inventory" to add stock information.</p>
        </div>
      )}
    </div>
  );
}

export default Inventory;