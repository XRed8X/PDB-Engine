import FormTitle from './FormTitle';
import Selector from './Selector';
import FileUploader from './FileUploader';
import TextInput from './TextInput';
import Checkbox from './Checkbox';
import CommandPreview from './CommandPreview';
import Button from '../buttons/Button';
import { useCommandForm } from '../../hooks/useCommandForm';

export default function MainForm() {
  const {
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
  } = useCommandForm();

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg space-y-6">
      <FormTitle title="Build command" />
      
      <Selector
        label="Select Command:"
        name="commandSelector"
        options={commandOptions}
        value={selectedCommand}
        onChange={(value) => setSelectedCommand(value)}
      />

      {currentConfig && (
        <>
          {/* Render Arguments */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {currentConfig.arguments.map((arg) => {
              if (arg === 'pdb') {
                return (
                  <div key={arg} className="md:col-span-3">
                    <FileUploader
                      label={`File (${arg})`}
                      name={arg}
                      accept=".pdb"
                      onChange={(file) => updateFormField(arg, file)}
                    />
                  </div>
                );
              } else {
                return (
                  <TextInput
                    key={arg}
                    label={arg}
                    name={arg}
                    value={formData[arg] as string || ''}
                    placeholder={`Enter ${arg}...`}
                    onChange={(value) => updateFormField(arg, value)}
                  />
                );
              }
            })}
          </div>

          {/* Render Optional Flags */}
          {currentConfig.flags.length > 0 && (
            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <label className="block text-sm font-semibold text-blue-900 mb-3">Optional Flags:</label>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2">
                {currentConfig.flags.map((flag) => (
                  <Checkbox
                    key={flag}
                    label={flag}
                    name={flag}
                    checked={formData[flag] as boolean || false}
                    onChange={(checked) => updateFormField(flag, checked)}
                  />
                ))}
              </div>
            </div>
          )}

          <CommandPreview command={command} />

          {error && (
            <div className="p-4 mb-4 text-red-700 bg-red-100 border border-red-400 rounded">
              <p className="font-semibold">Error:</p>
              <p>{error}</p>
            </div>
          )}

          {success && (
            <div className="p-4 mb-4 text-green-700 bg-green-100 border border-green-400 rounded">
              <p className="font-semibold">Success!</p>
              <p>Results downloaded successfully.</p>
              {downloadUrl && (
                <a 
                  href={downloadUrl} 
                  download 
                  className="text-green-600 underline hover:text-green-800"
                >
                  Click here if download didn't start
                </a>
              )}
            </div>
          )}

          <Button 
            label={isLoading ? "Executing..." : "Execute"}
            onClick={handleSubmit}
            type="primary"
            disabled={isLoading}
          />
        </>
      )}
    </div>
  );
}
