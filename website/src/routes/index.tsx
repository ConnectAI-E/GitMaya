import { createBrowserRouter, Navigate } from 'react-router-dom';
import Layout from '@/layout';
import AppLayout from '@/layout/app';

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        lazy: async () => {
          const Component = (await import('@/routes/home')).default;
          return {
            Component,
          };
        },
      },
    ],
  },
  {
    path: '/login',
    lazy: async () => {
      const Component = (await import('@/routes/login')).default;
      return {
        Component,
      };
    },
  },
  {
    path: '/app',
    element: <AppLayout />,
    children: [
      {
        index: true,
        element: <Navigate to="/app/people" replace={true} />,
      },
      {
        path: 'indicators',
        lazy: async () => {
          const Component = (await import('@/routes/indicators')).default;
          return {
            Component,
          };
        },
      },
      {
        path: 'induction',
        lazy: async () => {
          const Component = (await import('@/routes/induction')).default;
          return {
            Component,
          };
        },
      },
      {
        path: 'people',
        lazy: async () => {
          const Component = (await import('@/routes/people')).default;
          return {
            Component,
          };
        },
      },
      {
        path: 'repo',
        lazy: async () => {
          const Component = (await import('@/routes/repo')).default;
          return {
            Component,
          };
        },
      },
    ],
  },
]);

export default router;
