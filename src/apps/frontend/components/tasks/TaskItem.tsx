import React from 'react';

import { Task } from 'frontend/types/task';

interface TaskItemProps {
  task: Task;
  onEdit: (task: Task) => void;
  onDelete: (taskId: string) => void;
}

const TaskItem: React.FC<TaskItemProps> = ({ task, onEdit, onDelete }) => {
  const handleDelete = () => {
    // eslint-disable-next-line no-alert
    if (window.confirm('Are you sure you want to delete this task?')) {
      onDelete(task.id);
    }
  };

  return (
    <div className="rounded-lg border border-stroke bg-white p-6 shadow-card transition-shadow hover:shadow-4">
      <div className="mb-4">
        <h3 className="text-title-xsm font-semibold text-black">{task.title}</h3>
      </div>
      <div className="mb-4">
        <p className="text-body">{task.description}</p>
      </div>
      <div className="flex gap-3">
        <button
          onClick={() => onEdit(task)}
          className="rounded-lg bg-primary px-4 py-2 font-medium text-white transition hover:bg-primary/90 active:bg-primary/80"
          aria-label={`Edit task ${task.title}`}
        >
          Edit
        </button>
        <button
          onClick={handleDelete}
          className="rounded-lg bg-danger px-4 py-2 font-medium text-white transition hover:bg-danger/90 active:bg-danger/80"
          aria-label={`Delete task ${task.title}`}
        >
          Delete
        </button>
      </div>
    </div>
  );
};

export default TaskItem;
