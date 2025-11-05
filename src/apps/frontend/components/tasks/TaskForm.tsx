import { useFormik } from 'formik';
import React, { useEffect } from 'react';
import * as Yup from 'yup';

import { Button, FormControl, VerticalStackLayout } from 'frontend/components';
import Input from 'frontend/components/input';
import { ButtonKind, ButtonType } from 'frontend/types/button';
import { Task, TaskFormData } from 'frontend/types/task';

interface TaskFormProps {
  task?: Task | null;
  isLoading: boolean;
  onSubmit: (data: TaskFormData) => void;
  onCancel: () => void;
}

const TaskForm: React.FC<TaskFormProps> = ({
  task,
  isLoading,
  onSubmit,
  onCancel,
}) => {
  const formik = useFormik({
    initialValues: {
      title: task?.title || '',
      description: task?.description || '',
    },
    validationSchema: Yup.object({
      title: Yup.string()
        .required('Title is required')
        .max(100, 'Title must be at most 100 characters'),
      description: Yup.string()
        .required('Description is required')
        .max(500, 'Description must be at most 500 characters'),
    }),
    onSubmit: (values) => {
      onSubmit(values);
    },
  });

  // Update form values when task changes (for edit mode)
  useEffect(() => {
    if (task) {
      // eslint-disable-next-line no-void
      void formik.setValues({
        title: task.title,
        description: task.description,
      });
    } else {
      formik.resetForm();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [task]);

  const getFormikError = (field: keyof TaskFormData) =>
    formik.touched[field] ? formik.errors[field] : '';

  return (
    <form onSubmit={formik.handleSubmit}>
      <VerticalStackLayout gap={5}>
        <FormControl label="Title" error={getFormikError('title')}>
          <Input
            name="title"
            placeholder="Enter task title"
            value={formik.values.title}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={getFormikError('title')}
            disabled={isLoading}
            autoFocus
          />
        </FormControl>

        <FormControl label="Description" error={getFormikError('description')}>
          <textarea
            name="description"
            placeholder="Enter task description"
            value={formik.values.description}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            disabled={isLoading}
            rows={4}
            className={`w-full rounded-lg border p-4 outline-none focus:border-primary focus-visible:shadow-none ${
              getFormikError('description') ? 'border-red-500' : 'border-stroke'
            }`}
          />
        </FormControl>

        <div className="flex gap-3">
          <Button
            type={ButtonType.SUBMIT}
            kind={ButtonKind.PRIMARY}
            isLoading={isLoading}
            disabled={!formik.isValid || isLoading}
          >
            {task ? 'Update Task' : 'Create Task'}
          </Button>
          <button
            type="button"
            onClick={onCancel}
            disabled={isLoading}
            className="rounded-lg border border-stroke bg-white px-4 py-2 font-medium text-black transition hover:bg-gray active:bg-gray-2"
          >
            Cancel
          </button>
        </div>
      </VerticalStackLayout>
    </form>
  );
};

export default TaskForm;
