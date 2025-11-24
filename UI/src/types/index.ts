export interface FormDataState {
  [key: string]: string | File | null | boolean;
}

export interface CommandConfig {
  arguments: string[];
  flags: string[];
}

export interface PDBOptions {
  compatibility: {
    [key: string]: CommandConfig;
  };
}
