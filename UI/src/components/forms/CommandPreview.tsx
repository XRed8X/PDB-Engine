interface CommandPreviewProps {
  command: string;
  label?: string;
}

export default function CommandPreview({ command, label = 'Generated command:' }: CommandPreviewProps) {
  return (
    <div className="space-y-2 mt-2">
      <label className="block text-sm font-semibold text-blue-900">
        {label}
      </label>
      <div className="bg-gradient-to-r from-blue-50 to-green-50 border-2 border-blue-300 rounded-lg p-4 min-h-[100px] flex items-center">
        <pre className="text-sm text-gray-800 font-mono whitespace-pre-wrap break-all w-full">
          {command || 'Command will generate here...'}
        </pre>
      </div>
    </div>
  );
}
