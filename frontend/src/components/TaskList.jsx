import TaskItem from './TaskItem';

const TaskList = ({ tasks, onEdit, onDelete, isLoading }) => {
  if (isLoading) {
    return (
      <div className="task-list">
        <div className="loading">
          <p>Loading tasks...</p>
        </div>
      </div>
    );
  }

  if (!tasks || tasks.length === 0) {
    return (
      <div className="task-list">
        <div className="empty-state">
          <h3>No tasks yet</h3>
          <p>Create your first task using natural language above!</p>
        </div>
      </div>
    );
  }

  // Sort tasks by priority and due date
  const sortedTasks = [...tasks].sort((a, b) => {
    // First sort by priority (P1 > P2 > P3 > P4)
    const priorityOrder = { P1: 4, P2: 3, P3: 2, P4: 1 };
    const priorityDiff = priorityOrder[b.priority] - priorityOrder[a.priority];
    
    if (priorityDiff !== 0) {
      return priorityDiff;
    }
    
    // Then sort by due date (earlier dates first)
    if (a.due_date_time && b.due_date_time) {
      return new Date(a.due_date_time) - new Date(b.due_date_time);
    } else if (a.due_date_time) {
      return -1; // Tasks with due dates come first
    } else if (b.due_date_time) {
      return 1;
    }
    
    // Finally sort by creation date (newest first)
    return new Date(b.created_at) - new Date(a.created_at);
  });

  // Group tasks by priority for better organization
  const groupedTasks = sortedTasks.reduce((groups, task) => {
    const priority = task.priority;
    if (!groups[priority]) {
      groups[priority] = [];
    }
    groups[priority].push(task);
    return groups;
  }, {});

  const priorityLabels = {
    P1: 'High Priority',
    P2: 'Medium-High Priority',
    P3: 'Medium Priority',
    P4: 'Low Priority'
  };

  return (
    <div className="task-list">
      <div className="task-list-header">
        <h2>Your Tasks ({tasks.length})</h2>
      </div>
      
      {['P1', 'P2', 'P3', 'P4'].map(priority => {
        const priorityTasks = groupedTasks[priority];
        if (!priorityTasks || priorityTasks.length === 0) return null;
        
        return (
          <div key={priority} className={`priority-group priority-${priority.toLowerCase()}`}>
            <h3 className="priority-header">
              {priorityLabels[priority]} ({priorityTasks.length})
            </h3>
            <div className="tasks-grid">
              {priorityTasks.map(task => (
                <TaskItem
                  key={task.id}
                  task={task}
                  onEdit={onEdit}
                  onDelete={onDelete}
                />
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default TaskList;
