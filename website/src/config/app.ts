export type AppSiteConfig = typeof appSiteConfig;

export const appSiteConfig = {
  name: 'Next.js + NextUI',
  description: 'Make beautiful websites regardless of your design experience.',
  navItems: [
    {
      label: 'People',
      href: '/app/people',
    },
    {
      label: 'Repo',
      href: '/app/repo',
    },
  ],
  navMenuItems: [
    {
      label: 'People',
      href: '/app/people',
    },
    {
      label: 'Repo',
      href: '/app/repo',
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
