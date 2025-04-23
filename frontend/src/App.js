import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [databases, setDatabases] = useState([]);
  const [newDb, setNewDb] = useState({
    name: '',
    type: 'postgres',
    storage: '1Gi'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedDb, setSelectedDb] = useState(null);

  // Fetch databases on component mount
  useEffect(() => {
    fetchDatabases();
  }, []);

  const fetchDatabases = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/databases');
      const data = await response.json();
      setDatabases(data.databases);
    } catch (err) {
      setError('Failed to fetch databases');
      console.error(err);
    }
  };

  const createDatabase = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:5000/api/databases', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newDb),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create database');
      }
      
      const data = await response.json();
      setDatabases([...databases, data]);
      setNewDb({ name: '', type: 'postgres', storage: '1Gi' });
    } catch (err) {
      setError(err.message);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const deleteDatabase = async (id) => {
    if (!window.confirm('Are you sure you want to delete this database?')) {
      return;
    }
    
    try {
      const response = await fetch(`http://localhost:5000/api/databases/${id}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to delete database');
      }
      
      setDatabases(databases.filter(db => db.id !== id));
      if (selectedDb && selectedDb.id === id) {
        setSelectedDb(null);
      }
    } catch (err) {
      setError(err.message);
      console.error(err);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Home DBaaS</h1>
        <p>Create and manage databases on your home Kubernetes cluster</p>
      </header>
      
      <main>
        <section className="create-db">
          <h2>Create a new database</h2>
          {error && <div className="error">{error}</div>}
          
          <form onSubmit={createDatabase}>
            <div className="form-group">
              <label htmlFor="db-name">Database Name:</label>
              <input 
                type="text" 
                id="db-name" 
                value={newDb.name} 
                onChange={(e) => setNewDb({...newDb, name: e.target.value})}
                required
                placeholder="e.g., myproject" 
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="db-type">Database Type:</label>
              <select 
                id="db-type" 
                value={newDb.type} 
                onChange={(e) => setNewDb({...newDb, type: e.target.value})}
              >
                <option value="postgres">PostgreSQL</option>
                <option value="mysql">MySQL</option>
                <option value="mongodb">MongoDB</option>
                <option value="kafka">Kafka</option>
              </select>
            </div>
            
            <div className="form-group">
              <label htmlFor="db-storage">Storage Size:</label>
              <select 
                id="db-storage" 
                value={newDb.storage} 
                onChange={(e) => setNewDb({...newDb, storage: e.target.value})}
              >
                <option value="1Gi">1 GB</option>
                <option value="5Gi">5 GB</option>
                <option value="10Gi">10 GB</option>
                <option value="20Gi">20 GB</option>
              </select>
            </div>
            
            <button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create Database'}
            </button>
          </form>
        </section>
        
        <section className="db-list">
          <h2>Your Databases</h2>
          
          {databases.length === 0 ? (
            <p>No databases deployed yet. Create one to get started!</p>
          ) : (
            <ul>
              {databases.map(db => (
                <li key={db.id} onClick={() => setSelectedDb(db)}>
                  <div>
                    <strong>{db.name}</strong> ({db.type})
                    <button onClick={(e) => { e.stopPropagation(); deleteDatabase(db.id); }} className="delete-btn">
                      Delete
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
        
        {selectedDb && (
          <section className="db-details">
            <h2>{selectedDb.name} Details</h2>
            <div className="detail-card">
              <div>
                <h3>Connection Details</h3>
                <p><strong>Host:</strong> {selectedDb.connection}</p>
                <p><strong>Port:</strong> {selectedDb.port}</p>
                <p><strong>Database:</strong> {selectedDb.name}</p>
              </div>
              
              <div>
                <h3>Admin Credentials</h3>
                <p><strong>Username:</strong> {selectedDb.credentials.admin.username}</p>
                <p><strong>Password:</strong> {selectedDb.credentials.admin.password}</p>
              </div>
              
              <div>
                <h3>Read-Only Credentials</h3>
                <p><strong>Username:</strong> {selectedDb.credentials.readonly.username}</p>
                <p><strong>Password:</strong> {selectedDb.credentials.readonly.password}</p>
              </div>
              
              <div>
                <h3>Monitoring</h3>
                <a href={selectedDb.dashboard} target="_blank" rel="noopener noreferrer">
                  View Dashboard
                </a>
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;