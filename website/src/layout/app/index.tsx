import { Outlet } from 'react-router-dom';
import { Navbar } from '@/layout/app/navbar';

const AppLayout = () => {
  return (
    <div className="relative flex flex-col h-screen ">
      <Navbar />
      <Outlet />
    </div>
  );
};

export const HeaderContent = ({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) => (
  <header className="pt-10 pb-10">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold text-white">{title}</h1>
    </div>
    <div>{children}</div>
  </header>
);

export const Hero = ({ children }: { children?: React.ReactNode }) => {
  return (
    <div className="bg-black pb-32">
      <header className="pt-10">
        <div className="max-w-7xl mx-auto">{children}</div>
      </header>
    </div>
  );
};

export default AppLayout;
