import { useState, useEffect } from 'react';
import pdbOptions from '../data/pdb_options.json';
import { initializeFormData, generateCommand, generateCommandJSON } from '../utils/commandGenerator';
import { pdbEngineService } from '../services/pdbEngineService';
import type { FormDataState, CommandConfig, PDBOptions } from '../types';

interface DownloadItem {
  id: string;
  command: string;
  timestamp: string;
  downloadUrl: string;
  filename: string;
  executionTime: number;
  status: 'pending' | 'finished' | 'error';
}

export const useCommandForm = () => {
  const [selectedCommand, setSelectedCommand] = useState('ProteinDesign');
  const [formData, setFormData] = useState<FormDataState>({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [downloads, setDownloads] = useState<DownloadItem[]>([]);

  const commandOptions = Object.keys((pdbOptions as PDBOptions).compatibility);
  const currentConfig = selectedCommand
    ? (pdbOptions as PDBOptions).compatibility[selectedCommand]
    : null;

  // Reset form data when selected command changes
  useEffect(() => {
    if (currentConfig) {
      const newFormData = initializeFormData(currentConfig);
      setFormData(newFormData);
    }
  }, [selectedCommand, currentConfig]);

  // Cleanup download URL when component unmounts
  useEffect(() => {
    return () => {
      if (downloadUrl) {
        URL.revokeObjectURL(downloadUrl);
      }
    };
  }, [downloadUrl]);

  const updateFormField = (key: string, value: string | File | null | boolean) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
    setError(null);
    setSuccess(false);
  };

  const handleSubmit = async () => {
    const startTime = Date.now();
    const downloadId = startTime.toString();
    
    // Add pending download to history immediately
    const pendingDownload: DownloadItem = {
      id: downloadId,
      command: selectedCommand,
      timestamp: new Date().toISOString(),
      downloadUrl: '',
      filename: 'Processing...',
      executionTime: 0,
      status: 'pending',
    };
    setDownloads((prev) => [pendingDownload, ...prev]);
    
    try {
      setIsLoading(true);
      setError(null);
      setSuccess(false);
      
      const commandJSON = generateCommandJSON(selectedCommand, currentConfig, formData);
      
      console.log('Selected command:', selectedCommand);
      console.log('Form data:', formData);
      console.log('Command JSON:', commandJSON);
      
      // Execute command and get blob
      const response = await pdbEngineService.executeCommand(selectedCommand, formData);
      const blob = response.blob;
      
      // Create download URL from blob
      const url = URL.createObjectURL(blob);
      setDownloadUrl(url);
      
      // Get execution time from headers (in seconds)
      const executionTime = parseFloat(response.executionTime || '0');
      const executionTimeMs = Date.now() - startTime;
      
      // Trigger automatic download
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const filename = `${selectedCommand.toLowerCase()}_results_${timestamp}.zip`;
      
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Update the pending download with success status
      setDownloads((prev) => 
        prev.map((item) => 
          item.id === downloadId
            ? {
                ...item,
                downloadUrl: url,
                filename: filename,
                executionTime: executionTime,
                status: 'finished' as const,
              }
            : item
        )
      );
      
      setSuccess(true);
      console.log('Command executed successfully, file downloaded:', filename);
      
    } catch (err: any) {
      const executionTimeMs = Date.now() - startTime;
      const errorMessage = err.response?.data?.message || err.message || 'Error executing command';
      setError(errorMessage);
      console.error('Error executing command:', err);
      
      // Update the pending download with error status
      setDownloads((prev) => 
        prev.map((item) => 
          item.id === downloadId
            ? {
                ...item,
                filename: 'Failed',
                executionTime: executionTimeMs / 1000,
                status: 'error' as const,
              }
            : item
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  const command = generateCommand(selectedCommand, currentConfig, formData);
  const commandJSON = generateCommandJSON(selectedCommand, currentConfig, formData);

  return {
    selectedCommand,
    setSelectedCommand,
    formData,
    updateFormField,
    handleSubmit,
    command,
    commandJSON,
    commandOptions,
    currentConfig,
    isLoading,
    error,
    success,
    downloadUrl,
    downloads,
  };
};
