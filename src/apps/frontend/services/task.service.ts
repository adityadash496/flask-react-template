import APIService from 'frontend/services/api.service';
import { ApiResponse } from 'frontend/types';
import { JsonObject } from 'frontend/types/common-types';
import { CreateTaskData, Task, TaskModel, UpdateTaskData } from 'frontend/types/task';
import { getAccessTokenFromStorage } from 'frontend/utils/storage-util';

interface PaginatedTasksResponse {
  items: JsonObject[];
  pagination_params: JsonObject;
  total_count: number;
  total_pages: number;
}

interface TaskDeletionResponse {
  task_id: string;
  deleted_at: string;
  success: boolean;
}

export default class TaskService extends APIService {
  getTasks = async (accountId: string): Promise<ApiResponse<Task[]>> => {
    const accessToken = getAccessTokenFromStorage();
    if (!accessToken) {
      throw new Error('Access token not found');
    }

    const response = await this.apiClient.get<PaginatedTasksResponse>(
      `/accounts/${accountId}/tasks`,
      {
        headers: {
          Authorization: `Bearer ${accessToken.token}`,
        },
      }
    );
    const tasks = response.data.items.map((item: JsonObject) => new TaskModel(item));
    return new ApiResponse(tasks);
  };

  getTask = async (accountId: string, taskId: string): Promise<ApiResponse<Task>> => {
    const accessToken = getAccessTokenFromStorage();
    if (!accessToken) {
      throw new Error('Access token not found');
    }

    const response = await this.apiClient.get<JsonObject>(
      `/accounts/${accountId}/tasks/${taskId}`,
      {
        headers: {
          Authorization: `Bearer ${accessToken.token}`,
        },
      }
    );
    return new ApiResponse(new TaskModel(response.data));
  };

  createTask = async (
    accountId: string,
    data: CreateTaskData
  ): Promise<ApiResponse<Task>> => {
    const accessToken = getAccessTokenFromStorage();
    if (!accessToken) {
      throw new Error('Access token not found');
    }

    const response = await this.apiClient.post<JsonObject>(
      `/accounts/${accountId}/tasks`,
      {
        title: data.title,
        description: data.description,
      },
      {
        headers: {
          Authorization: `Bearer ${accessToken.token}`,
        },
      }
    );
    return new ApiResponse(new TaskModel(response.data));
  };

  updateTask = async (
    accountId: string,
    taskId: string,
    data: UpdateTaskData
  ): Promise<ApiResponse<Task>> => {
    const accessToken = getAccessTokenFromStorage();
    if (!accessToken) {
      throw new Error('Access token not found');
    }

    const response = await this.apiClient.patch<JsonObject>(
      `/accounts/${accountId}/tasks/${taskId}`,
      {
        title: data.title,
        description: data.description,
      },
      {
        headers: {
          Authorization: `Bearer ${accessToken.token}`,
        },
      }
    );
    return new ApiResponse(new TaskModel(response.data));
  };

  deleteTask = async (
    accountId: string,
    taskId: string
  ): Promise<ApiResponse<void>> => {
    const accessToken = getAccessTokenFromStorage();
    if (!accessToken) {
      throw new Error('Access token not found');
    }

    await this.apiClient.delete<TaskDeletionResponse>(
      `/accounts/${accountId}/tasks/${taskId}`,
      {
        headers: {
          Authorization: `Bearer ${accessToken.token}`,
        },
      }
    );
    return new ApiResponse();
  };
}
