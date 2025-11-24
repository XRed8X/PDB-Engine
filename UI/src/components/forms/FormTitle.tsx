interface FormTitleProps {
  title: string;
}

export default function FormTitle({ title }: FormTitleProps) {
  return (
    <h2 className="text-2xl md:text-3xl font-bold text-blue-800 mb-6 pb-4 border-b-2 border-green-500">
      {title}
    </h2>
  );
}
