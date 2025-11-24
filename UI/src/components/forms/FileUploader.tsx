interface FileUploaderProps {
  label: string;
  accept?: string;
  onChange: (file: File | null) => void;
  name: string;
}

export default function FileUploader({ label, accept, onChange, name }: FileUploaderProps) {
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    onChange(file);
  };

  return (
    <div className="space-y-2">
      <label htmlFor={name} className="block text-sm font-semibold text-blue-900">
        {label}
      </label>
      <input
        type="file"
        id={name}
        name={name}
        accept={accept}
        onChange={handleFileChange}
        className="w-full px-4 py-3 border-2 border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 bg-white text-gray-800 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-green-500 file:text-white file:font-semibold hover:file:bg-green-600 file:cursor-pointer transition-all"
      />
    </div>
  );
}
