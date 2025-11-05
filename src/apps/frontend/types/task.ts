import { JsonObject } from 'frontend/types/common-types';

export interface Task {
  id: string;
  account_id: string;
  title: string;
  description: string;
}

export interface CreateTaskData {
  title: string;
  description: string;
}

export interface UpdateTaskData {
  title: string;
  description: string;
}

export interface TaskFormData {
  title: string;
  description: string;
}

export interface TaskListState {
  tasks: Task[];
  loading: boolean;
  error: string | null;
}

export class TaskModel implements Task {
  id: string;
  account_id: string;
  title: string;
  description: string;

  constructor(json: JsonObject) {
    this.id = json.id as string;
    this.account_id = json.account_id as string;
    this.title = json.title as string;
    this.description = json.description as string;
  }
}
