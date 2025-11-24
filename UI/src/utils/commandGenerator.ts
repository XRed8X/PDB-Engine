import type { FormDataState, CommandConfig } from '../types';

export const generateCommand = (
  selectedCommand: string,
  currentConfig: CommandConfig | null,
  formData: FormDataState
): string => {
  if (!selectedCommand || !currentConfig) return '';

  let command = `--command=${selectedCommand}`;

  // Add arguments
  currentConfig.arguments.forEach((arg) => {
    const value = formData[arg];
    if (value) {
      if (value instanceof File) {
        command += ` --${arg}=${value.name}`;
      } else if (typeof value === 'string' && value.trim()) {
        command += ` --${arg}=${value}`;
      }
    }
  });

  // Add flags
  currentConfig.flags.forEach((flag) => {
    if (formData[flag] === true) {
      command += ` --${flag}`;
    }
  });

  return command;
};

export const generateCommandJSON = (
  selectedCommand: string,
  currentConfig: CommandConfig | null,
  formData: FormDataState
) => {
  if (!selectedCommand || !currentConfig) return null;

  const commandData: any = {
    command: selectedCommand,
    arguments: {},
    flags: [],
  };

  // Add arguments
  currentConfig.arguments.forEach((arg) => {
    const value = formData[arg];
    if (value) {
      if (value instanceof File) {
        commandData.arguments[arg] = value.name;
      } else if (typeof value === 'string' && value.trim()) {
        commandData.arguments[arg] = value;
      }
    }
  });

  // Add flags
  currentConfig.flags.forEach((flag) => {
    if (formData[flag] === true) {
      commandData.flags.push(flag);
    }
  });

  return commandData;
};

export const initializeFormData = (config: CommandConfig): FormDataState => {
  const newFormData: FormDataState = {};

  // Initialize arguments
  config.arguments.forEach((arg) => {
    if (arg === 'pdb') {
      newFormData[arg] = null; // File
    } else {
      newFormData[arg] = ''; // String
    }
  });

  // Initialize flags
  config.flags.forEach((flag) => {
    newFormData[flag] = false; // Boolean
  });

  return newFormData;
};
