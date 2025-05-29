import { useState } from 'react';

const TaskItem = ({ task, onEdit, onDelete }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({
    task_name: task.task_name,
    assignee: task.assignee || '',
    due_date_time: task.due_date_time ? new Date(task.due_date_time).toISOString().slice(0, 16) : '',
    priority: task.priority
  });

  const formatDate = (dateString) => {
    if (!dateString) return 'No due date';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = date - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    const formatted = date.toLocaleDateString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
    
    if (diffDays < 0) {
      return `${formatted} (Overdue)`;
    } else if (diffDays === 0) {
      return `${formatted} (Today)`;
    } else if (diffDays === 1) {
      return `${formatted} (Tomorrow)`;
    } else {
      return formatted;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'P1': return '#ff4757'; // Red
      case 'P2': return '#ff6b35'; // Orange
      case 'P3': return '#ffa502'; // Yellow
      case 'P4': return '#2ed573'; // Green
      default: return '#747d8c'; // Gray
    }
  };

  const handleSave = () => {
    const updateData = {
      task_name: editData.task_name,
      assignee: editData.assignee || null,
      due_date_time: editData.due_date_time ? new Date(editData.due_date_time).toISOString() : null,
      priority: editData.priority
    };
    
    onEdit(task.id, updateData);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditData({
      task_name: task.task_name,
      assignee: task.assignee || '',
      due_date_time: task.due_date_time ? new Date(task.due_date_time).toISOString().slice(0, 16) : '',
      priority: task.priority
    });
    setIsEditing(false);
  };

  if (isEditing) {
    return (
      <div className="task-item editing">
        <div className="edit-form">
          <div className="form-group">
            <label>Task Name:</label>
            <input
              type="text"
              value={editData.task_name}
              onChange={(e) => setEditData({...editData, task_name: e.target.value})}
              className="edit-input"
            />
          </div>
          
          <div className="form-group">
            <label>Assignee:</label>
            <input
              type="text"
              value={editData.assignee}
              onChange={(e) => setEditData({...editData, assignee: e.target.value})}
              placeholder="Optional"
              className="edit-input"
            />
          </div>
          
          <div className="form-group">
            <label>Due Date & Time:</label>
            <input
              type="datetime-local"
              value={editData.due_date_time}
              onChange={(e) => setEditData({...editData, due_date_time: e.target.value})}
              className="edit-input"
            />
          </div>
          
          <div className="form-group">
            <label>Priority:</label>
            <select
              value={editData.priority}
              onChange={(e) => setEditData({...editData, priority: e.target.value})}
              className="edit-select"
            >
              <option value="P1">P1 - Highest</option>
              <option value="P2">P2 - High</option>
              <option value="P3">P3 - Medium</option>
              <option value="P4">P4 - Low</option>
            </select>
          </div>
          
          <div className="edit-actions">
            <button onClick={handleSave} className="save-btn">Save</button>
            <button onClick={handleCancel} className="cancel-btn">Cancel</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="task-item">
      <div className="task-header">
        <div className="task-title">
          <h3>{task.task_name}</h3>
          <span 
            className="priority-badge"
            style={{ backgroundColor: getPriorityColor(task.priority) }}
          >
            {task.priority}
          </span>
        </div>
        <div className="task-actions">
          <button onClick={() => setIsEditing(true)} className="edit-btn">
            Edit
          </button>
          <button onClick={() => onDelete(task.id)} className="delete-btn">
            Delete
          </button>
        </div>
      </div>
      
      <div className="task-details">
        {task.assignee && (
          <div className="task-detail">
            <strong>Assigned to:</strong> {task.assignee}
          </div>
        )}
        
        <div className="task-detail">
          <strong>Due:</strong> {formatDate(task.due_date_time)}
        </div>
        
        {task.original_text && (
          <div className="task-detail original-text">
            <strong>Original input:</strong> "{task.original_text}"
          </div>
        )}
        
        <div className="task-timestamps">
          <small>
            Created: {new Date(task.created_at).toLocaleDateString()} | 
            Updated: {new Date(task.updated_at).toLocaleDateString()}
          </small>
        </div>
      </div>
    </div>
  );
};

export default TaskItem;
