import apiClient from './apiClient';
import type { FormDataState } from '../types';

export interface CommandExecutionRequest {
  command: string;
  arguments: Record<string, string>;
  flags: string[];
  file?: File;
}

export interface CommandExecutionResponse {
  job_id: string;
  status: string;
  message: string;
  command: string;
}

export interface JobStatusResponse {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress?: number;
  result?: any;
  error?: string;
}

export const pdbEngineService = {
  /**
   * Execute a PDB Engine command
   */
  async executeCommand(command: string, commandData: any): Promise<CommandExecutionResponse> {
    // Check if there's a file in the command data
    const hasFile = Object.values(commandData).some(value => value instanceof File);

    if (hasFile) {
      // Use FormData for file upload
      const formData = new FormData();
      formData.append('command', command);

      const args: Record<string, string> = {};
      const flags: string[] = [];

      Object.entries(commandData).forEach(([key, value]) => {
        if (value instanceof File) {
          formData.append('file', value);
          args[key] = value.name; // Store filename in arguments
        } else if (typeof value === 'boolean' && value === true) {
          flags.push(key);
        } else if (value !== null && value !== '' && typeof value !== 'boolean') {
          args[key] = String(value);
        }
      });

      formData.append('arguments', JSON.stringify(args));
      formData.append('flags', JSON.stringify(flags));

      const response = await apiClient.post<CommandExecutionResponse>('/execute', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } else {
      // Use JSON for commands without files
      const payload: {
        command: string;
        arguments: Record<string, any>;
        flags: string[];
      } = {
        command: command,
        arguments: {},
        flags: []
      };

      Object.entries(commandData).forEach(([key, value]) => {
        if (typeof value === 'boolean' && value === true) {
          payload.flags.push(key);
        } else if (value !== null && value !== '' && typeof value !== 'boolean') {
          payload.arguments[key] = value;
        }
      });

      const response = await apiClient.post<CommandExecutionResponse>('/execute', payload);
      return response.data;
    }
  },

  /**
   * Get job status
   */
  async getJobStatus(jobId: string): Promise<JobStatusResponse> {
    const response = await apiClient.get<JobStatusResponse>(
      `/api/jobs/${jobId}/status`
    );
    return response.data;
  },

  /**
   * Download job results
   */
  async downloadJobResults(jobId: string): Promise<Blob> {
    const response = await apiClient.get(`/api/jobs/${jobId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * Cancel a running job
   */
  async cancelJob(jobId: string): Promise<void> {
    await apiClient.post(`/api/jobs/${jobId}/cancel`);
  },
};
