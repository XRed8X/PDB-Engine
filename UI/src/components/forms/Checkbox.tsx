interface CheckboxProps {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  name: string;
}

export default function Checkbox({ label, checked, onChange, name }: CheckboxProps) {
  return (
    <div className="flex items-center space-x-3 p-2 rounded hover:bg-blue-100 transition-colors">
      <input
        type="checkbox"
        id={name}
        name={name}
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="w-5 h-5 text-green-600 border-2 border-blue-300 rounded focus:ring-2 focus:ring-green-500 cursor-pointer"
      />
      <label htmlFor={name} className="text-sm font-medium text-blue-900 cursor-pointer select-none">
        {label}
      </label>
    </div>
  );
}
