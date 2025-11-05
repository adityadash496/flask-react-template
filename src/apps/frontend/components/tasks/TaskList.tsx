import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';

import TaskForm from './TaskForm';
import TaskItem from './TaskItem';

import { useAccountContext } from 'frontend/contexts';
import { TaskService } from 'frontend/services';
import { Task, TaskFormData } from 'frontend/types/task';

const taskService = new TaskService();

const TaskList: React.FC = () => {
  const { accountDetails } = useAccountContext();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isFormOpen, setIsFormOpen] = useState<boolean>(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await taskService.getTasks(accountDetails.id);
      if (response.data) {
        // Sort by newest first (assuming newer tasks have higher IDs or use a timestamp if available)
        const sortedTasks = response.data.sort((a, b) => b.id.localeCompare(a.id));
        setTasks(sortedTasks);
      }
    } catch (err) {
      const errorMessage = 'Failed to fetch tasks. Please try again.';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (accountDetails.id) {
      // eslint-disable-next-line no-void
      void fetchTasks();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [accountDetails.id]);

  const handleOpenForm = () => {
    setEditingTask(null);
    setIsFormOpen(true);
  };

  const handleCloseForm = () => {
    setIsFormOpen(false);
    setEditingTask(null);
  };

  const handleEdit = (task: Task) => {
    setEditingTask(task);
    setIsFormOpen(true);
  };

  const handleSubmit = (data: TaskFormData) => {
    // eslint-disable-next-line no-void
    void (async () => {
      try {
        setIsSubmitting(true);
        if (editingTask) {
          // Update existing task
          await taskService.updateTask(accountDetails.id, editingTask.id, data);
          toast.success('Task updated successfully!');
        } else {
          // Create new task
          await taskService.createTask(accountDetails.id, data);
          toast.success('Task created successfully!');
        }
        handleCloseForm();
        await fetchTasks();
      } catch (err) {
        toast.error('Failed to save task. Please try again.');
      } finally {
        setIsSubmitting(false);
      }
    })();
  };

  const handleDelete = (taskId: string) => {
    // eslint-disable-next-line no-void
    void (async () => {
      try {
        await taskService.deleteTask(accountDetails.id, taskId);
        toast.success('Task deleted successfully!');
        await fetchTasks();
      } catch (err) {
        toast.error('Failed to delete task. Please try again.');
      }
    })();
  };

  const handleRetryClick = () => {
    // eslint-disable-next-line no-void
    void fetchTasks();
  };

  if (loading) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <div className="size-12 animate-spin rounded-full border-4 border-solid border-primary border-r-transparent"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-danger bg-danger/10 p-6 text-center">
        <p className="text-danger">{error}</p>
        <button
          onClick={handleRetryClick}
          className="mt-4 rounded-lg bg-primary px-4 py-2 font-medium text-white transition hover:bg-primary/90"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-title-md font-bold text-black">My Tasks</h2>
        <button
          onClick={handleOpenForm}
          className="rounded-lg bg-primary px-6 py-3 font-medium text-white transition hover:bg-primary/90 active:bg-primary/80"
          aria-label="Add new task"
        >
          + Add New Task
        </button>
      </div>

      {isFormOpen && (
        <div className="mb-6 rounded-lg border border-stroke bg-white p-6 shadow-card">
          <h3 className="mb-4 text-title-sm font-semibold text-black">
            {editingTask ? 'Edit Task' : 'Create New Task'}
          </h3>
          <TaskForm
            task={editingTask}
            isLoading={isSubmitting}
            onSubmit={handleSubmit}
            onCancel={handleCloseForm}
          />
        </div>
      )}

      {tasks.length === 0 ? (
        <div className="rounded-lg border border-stroke bg-white p-12 text-center">
          <p className="text-lg text-body">No tasks yet. Create your first task to get started!</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {tasks.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              onEdit={handleEdit}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default TaskList;
