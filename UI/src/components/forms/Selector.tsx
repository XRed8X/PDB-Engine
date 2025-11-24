interface SelectorProps {
  label: string;
  options: string[];
  value: string;
  onChange: (value: string) => void;
  name: string;
}

export default function Selector({ label, options, value, onChange, name }: SelectorProps) {
  return (
    <div className="space-y-2">
      <label htmlFor={name} className="block text-sm font-semibold text-blue-900">
        {label}
      </label>
      <select
        id={name}
        name={name}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-4 py-3 border-2 border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 bg-white text-gray-800 transition-all hover:border-blue-400"
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </div>
  );
}
