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
    try {
      setIsLoading(true);
      setError(null);
      setSuccess(false);
      
      const commandJSON = generateCommandJSON(selectedCommand, currentConfig, formData);
      
      console.log('Selected command:', selectedCommand);
      console.log('Form data:', formData);
      console.log('Command JSON:', commandJSON);
      
      // Execute command and get blob
      const blob = await pdbEngineService.executeCommand(selectedCommand, formData);
      
      // Create download URL from blob
      const url = URL.createObjectURL(blob);
      setDownloadUrl(url);
      
      // Trigger automatic download
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const filename = `${selectedCommand.toLowerCase()}_results_${timestamp}.zip`;
      
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Add to downloads history
      const newDownload: DownloadItem = {
        id: Date.now().toString(),
        command: selectedCommand,
        timestamp: new Date().toISOString(),
        downloadUrl: url,
        filename: filename,
      };
      setDownloads((prev) => [newDownload, ...prev]);
      
      setSuccess(true);
      console.log('Command executed successfully, file downloaded:', filename);
      
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || err.message || 'Error executing command';
      setError(errorMessage);
      console.error('Error executing command:', err);
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
