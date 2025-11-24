interface TextInputProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  name: string;
  placeholder?: string;
  type?: 'text' | 'number' | 'email';
}

export default function TextInput({ 
  label, 
  value, 
  onChange, 
  name, 
  placeholder = '',
  type = 'text'
}: TextInputProps) {
  return (
    <div className="space-y-2">
      <label htmlFor={name} className="block text-sm font-semibold text-blue-900">
        {label}
      </label>
      <input
        type={type}
        id={name}
        name={name}
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-4 py-3 border-2 border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 bg-white text-gray-800 placeholder-gray-400 transition-all hover:border-blue-400"
      />
    </div>
  );
}
