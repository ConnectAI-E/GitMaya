export type SiteConfig = typeof siteConfig;

export const siteConfig = {
  name: 'Next.js + NextUI',
  description: 'Make beautiful websites regardless of your design experience.',
  navItems: [
    {
      label: 'Home',
      href: '/',
    },
    {
      label: 'People',
      href: '/app/people',
    },
  ],
  navMenuItems: [
    {
      label: 'Profile',
      href: '/profile',
    },
    {
      label: 'Dashboard',
      href: '/dashboard',
    },
    {
      label: 'Projects',
      href: '/projects',
    },
    {
      label: 'Team',
      href: '/team',
    },
    {
      label: 'Calendar',
      href: '/calendar',
    },
    {
      label: 'Settings',
      href: '/settings',
    },
    {
      label: 'Help & Feedback',
      href: '/help-feedback',
    },
    {
      label: 'Logout',
      href: '/logout',
    },
  ],
  links: {
    github: 'https://github.com/ConnectAI-E/GitMaya-Frontend',
    twitter: 'https://github.com/ConnectAI-E/GitMaya-Frontend',
    docs: 'https://github.com/ConnectAI-E/GitMaya-Frontend',
    discord: 'https://github.com/ConnectAI-E/GitMaya-Frontend',
    sponsor: 'https://github.com/ConnectAI-E/GitMaya-Frontend',
  },
};
