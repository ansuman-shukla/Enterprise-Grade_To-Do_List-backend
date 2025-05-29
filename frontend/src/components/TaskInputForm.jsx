import { useState } from 'react';
import { taskAPI } from '../services/api';

const TaskInputForm = ({ onTaskCreated, onError }) => {
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!inputText.trim()) {
      onError('Please enter a task description');
      return;
    }

    setIsLoading(true);
    
    try {
      const response = await taskAPI.parseTask(inputText.trim());
      
      if (response.success) {
        setInputText(''); // Clear input on success
        onTaskCreated(response.data);
      } else {
        onError(response.message || 'Failed to create task');
      }
    } catch (error) {
      onError(error.message || 'Failed to create task');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="task-input-form">
      <h2>Add New Task</h2>
      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Describe your task in natural language... "
            rows={4}
            disabled={isLoading}
            className="task-input"
          />
        </div>
        
        <button 
          type="submit" 
          disabled={isLoading || !inputText.trim()}
          className={`submit-btn ${isLoading ? 'loading' : ''}`}
        >
          {isLoading ? 'Processing...' : 'Create Task'}
        </button>
      </form>
      
    </div>
  );
};

export default TaskInputForm;
