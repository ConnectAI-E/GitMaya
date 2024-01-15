import { Logo } from '@/components/icons';

export const FallbackElement = () => {
  return (
    <div className="flex items-center justify-center h-screen" role="status">
      <Logo size={48} />
      <span className="sr-only">Loading...</span>
    </div>
  );
};
