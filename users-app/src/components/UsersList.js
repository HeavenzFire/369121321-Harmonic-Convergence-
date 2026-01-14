import React, { useState, useEffect } from 'react';

const UsersList = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await fetch('https://jsonplaceholder.typicode.com/users');
        if (!response.ok) {
          throw new Error('Failed to fetch users');
        }
        const data = await response.json();
        setUsers(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <strong className="font-bold">Error:</strong>
          <span className="block sm:inline"> {error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-center mb-8 text-gray-800">Users List</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {users.map((user) => (
          <div key={user.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-300">
            <h2 className="text-xl font-semibold text-gray-800 mb-2">{user.name}</h2>
            <p className="text-gray-600 mb-1"><strong>Username:</strong> {user.username}</p>
            <p className="text-gray-600 mb-1"><strong>Email:</strong> {user.email}</p>
            <p className="text-gray-600 mb-1"><strong>Phone:</strong> {user.phone}</p>
            <p className="text-gray-600 mb-2"><strong>Website:</strong> {user.website}</p>
            <div className="text-sm text-gray-500">
              <p><strong>Address:</strong> {user.address.street}, {user.address.city}</p>
              <p><strong>Company:</strong> {user.company.name}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default UsersList;