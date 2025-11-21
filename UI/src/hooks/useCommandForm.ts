import { useState, useEffect } from 'react';
import pdbOptions from '../data/pdb_options.json';
import { initializeFormData, generateCommand, generateCommandJSON } from '../utils/commandGenerator';
import { pdbEngineService } from '../services/pdbEngineService';
import type { FormDataState, CommandConfig, PDBOptions } from '../types';

export const useCommandForm = () => {
  const [selectedCommand, setSelectedCommand] = useState('ProteinDesign');
  const [formData, setFormData] = useState<FormDataState>({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);

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

  const updateFormField = (key: string, value: string | File | null | boolean) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
    setError(null);
  };

  const handleSubmit = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const commandJSON = generateCommandJSON(selectedCommand, currentConfig, formData);
      
      console.log('Selected command:', selectedCommand);
      console.log('Form data:', formData);
      console.log('Command JSON:', commandJSON);
      
      const response = await pdbEngineService.executeCommand(selectedCommand, formData);
      
      setJobId(response.job_id);
      console.log('Job created:', response);
      
      // TODO: Redirect to job status page or show success message
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
    jobId,
  };
};
