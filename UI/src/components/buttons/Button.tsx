interface ButtonProps {
  label: string;
  onClick: () => void;
  type?: 'primary' | 'secondary' | 'danger';
  disabled?: boolean;
}

export default function Button({ 
  label, 
  onClick, 
  type = 'primary',
  disabled = false 
}: ButtonProps) {
  const baseStyles = 'w-full md:w-auto px-8 py-3 rounded-lg font-semibold text-white transition-all duration-200 transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100';
  
  const typeStyles = {
    primary: 'bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 shadow-lg hover:shadow-xl',
    secondary: 'bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 shadow-lg hover:shadow-xl',
    danger: 'bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 shadow-lg hover:shadow-xl'
  };

  return (
    <button
      className={`${baseStyles} ${typeStyles[type]}`}
      onClick={onClick}
      disabled={disabled}
    >
      {label}
    </button>
  );
}
