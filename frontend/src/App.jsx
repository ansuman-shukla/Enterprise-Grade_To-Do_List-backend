import { useState, useEffect } from 'react';
import TaskInputForm from './components/TaskInputForm';
import TaskList from './components/TaskList';
import { taskAPI, healthCheck } from './services/api';
import './App.css';

function App() {
  const [tasks, setTasks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [backendStatus, setBackendStatus] = useState('checking');

  // Check backend health on component mount
  useEffect(() => {
    checkBackendHealth();
    fetchTasks();
  }, []);

  const checkBackendHealth = async () => {
    try {
      await healthCheck();
      setBackendStatus('connected');
    } catch (error) {
      setBackendStatus('disconnected');
      setError('Backend server is not running. Please start the FastAPI server.');
    }
  };

  const fetchTasks = async () => {
    try {
      setIsLoading(true);
      const fetchedTasks = await taskAPI.getAllTasks();
      setTasks(fetchedTasks);
      setError('');
    } catch (error) {
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTaskCreated = (newTask) => {
    setTasks(prevTasks => [newTask, ...prevTasks]);
    setSuccess('Task created successfully!');
    setTimeout(() => setSuccess(''), 3000);
  };

  const handleTaskEdit = async (taskId, updateData) => {
    try {
      const response = await taskAPI.updateTask(taskId, updateData);
      if (response.success) {
        setTasks(prevTasks =>
          prevTasks.map(task =>
            task.id === taskId ? response.data : task
          )
        );
        setSuccess('Task updated successfully!');
        setTimeout(() => setSuccess(''), 3000);
      }
    } catch (error) {
      setError(error.message);
      setTimeout(() => setError(''), 5000);
    }
  };

  const handleTaskDelete = async (taskId) => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      const response = await taskAPI.deleteTask(taskId);
      if (response.success) {
        setTasks(prevTasks => prevTasks.filter(task => task.id !== taskId));
        setSuccess('Task deleted successfully!');
        setTimeout(() => setSuccess(''), 3000);
      }
    } catch (error) {
      setError(error.message);
      setTimeout(() => setError(''), 5000);
    }
  };

  const handleError = (errorMessage) => {
    setError(errorMessage);
    setTimeout(() => setError(''), 5000);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Enterprise To-Do List</h1>
        <p>Create tasks using natural language - powered by AI</p>

        <div className={`status-indicator ${backendStatus}`}>
          <span className="status-dot"></span>
          {backendStatus === 'connected' && 'Backend Connected'}
          {backendStatus === 'disconnected' && 'Backend Disconnected'}
          {backendStatus === 'checking' && 'Checking Connection...'}
        </div>
      </header>

      {error && (
        <div className="alert alert-error">
          <span className="alert-icon">⚠️</span>
          {error}
        </div>
      )}

      {success && (
        <div className="alert alert-success">
          <span className="alert-icon">✅</span>
          {success}
        </div>
      )}

      <main className="app-main">
        <div className="container">
          <TaskInputForm
            onTaskCreated={handleTaskCreated}
            onError={handleError}
          />

          <TaskList
            tasks={tasks}
            onEdit={handleTaskEdit}
            onDelete={handleTaskDelete}
            isLoading={isLoading}
          />
        </div>
      </main>

      <footer className="app-footer">
        <p>Built with React, FastAPI, MongoDB, and Google Gemini AI</p>
      </footer>
    </div>
  );
}

export default App;
