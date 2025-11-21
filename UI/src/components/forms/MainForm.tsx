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
    commandOptions,
    currentConfig,
    isLoading,
    error,
    jobId,
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
            <div className="p-4 bg-red-50 border-2 border-red-300 rounded-lg">
              <p className="text-red-800 font-semibold">Error:</p>
              <p className="text-red-700">{error}</p>
            </div>
          )}

          {jobId && (
            <div className="p-4 bg-green-50 border-2 border-green-300 rounded-lg">
              <p className="text-green-800 font-semibold">Success!</p>
              <p className="text-green-700">Job ID: {jobId}</p>
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
