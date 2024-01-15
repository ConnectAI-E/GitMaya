import { Outlet } from 'react-router-dom';
import { Footer } from '@/layout/footer';
import { Navbar } from '@/layout/narbar';

const Layout = () => {
  return (
    <div className="relative flex flex-col h-screen">
      <Navbar />
      <main className="container mx-auto max-w-7xl pt-32 px-6 flex-grow">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
};

export default Layout;
