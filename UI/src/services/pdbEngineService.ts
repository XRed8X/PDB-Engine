import apiClient from './apiClient';

export const pdbEngineService = {
  /**
   * Execute a PDB Engine command and download results
   */
  async executeCommand(command: string, commandData: any): Promise<{ blob: Blob; executionTime: string; status: string }> {
    const formData = new FormData();
    formData.append('command', command);

    const args: Record<string, string> = {};
    const flags: string[] = [];

    Object.entries(commandData).forEach(([key, value]) => {
      if (value instanceof File) {
        formData.append('file', value);
        // Don't add filename to arguments, API will handle it
      } else if (typeof value === 'boolean' && value === true) {
        flags.push(key);
      } else if (value !== null && value !== '' && typeof value !== 'boolean') {
        args[key] = String(value);
      }
    });

    formData.append('arguments', JSON.stringify(args));
    formData.append('flags', JSON.stringify(flags));

    const response = await apiClient.post('/api/execute', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      responseType: 'blob', // Receive file as blob
    });
    
    return {
      blob: response.data,
      executionTime: response.headers['x-execution-time'] || '0',
      status: response.headers['x-job-status'] || 'finished',
    };
  },
};