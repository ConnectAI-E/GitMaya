import {
  Navbar as NextUINavbar,
  NavbarContent,
  NavbarMenu,
  NavbarMenuToggle,
  NavbarBrand,
  NavbarItem,
  NavbarMenuItem,
} from '@nextui-org/navbar';

import { link as linkStyles } from '@nextui-org/theme';

import clsx from 'clsx';
import { GithubIcon, DiscordIcon, Logo } from '@/components/icons';
// import { ThemeSwitch } from '@/components/theme-switch';
import { I18nSwitch } from '@/components/i18n-switch';

import { useTranslation } from 'react-i18next';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useAccountStore } from '@/stores';
import { Avatar } from '@/components/avatar';

import { appSiteConfig } from '@/config/app';

import useSwr from 'swr';

import { getTeams, switchTeam } from '@/api';

import { Select, SelectItem, Link } from '@nextui-org/react';
import { useMemo } from 'react';
import useSWRMutation from 'swr/mutation';

export const Navbar = () => {
  const navigate = useNavigate();
  const account = useAccountStore.use.account();
  const updateAccount = useAccountStore.use.updateAccount();

  const team_id = account?.current_team as string;
  console.log('Dogtiti ~ Navbar ~ team_id:', team_id);

  const { trigger } = useSWRMutation(
    `api/account`,
    (
      _url,
      {
        arg,
      }: {
        arg: {
          current_team: string;
        };
      },
    ) => switchTeam(arg),
  );

  const { data } = useSwr('/api/team', getTeams);

  const teams =
    useMemo(
      () =>
        data?.data
          .map((item) => ({
            label: item.name,
            value: item.id,
          }))
          .concat({
            label: 'Create a team',
            value: 'create',
          }),
      [data?.data],
    ) || [];

  const { t } = useTranslation();

  const selectTeam = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const team_id = e.target.value;
    if (team_id === 'create') {
      navigate('/app/induction');
    } else {
      await trigger({
        current_team: team_id,
      });
      updateAccount();
    }
  };

  return (
    <NextUINavbar maxWidth="xl" position="sticky">
      <NavbarContent className="basis-1/5 sm:basis-full" justify="start">
        <NavbarBrand as="li" className="gap-3 max-w-fit">
          <Link className="flex justify-start items-center gap-1" href="/">
            <Logo />
            <div className="text-xl font-black mx-4 text-gradient text-maya">GitMaya</div>
          </Link>
        </NavbarBrand>
        <ul className="hidden lg:flex gap-4 justify-start ml-2">
          {appSiteConfig.navItems.map((item) => (
            <NavbarItem key={item.href}>
              <Link
                className={clsx(
                  linkStyles({ color: 'foreground' }),
                  'data-[active=true]:text-primary data-[active=true]:font-medium',
                )}
                color="foreground"
                href={item.href}
              >
                {item.label}
              </Link>
            </NavbarItem>
          ))}
        </ul>
      </NavbarContent>
      <NavbarContent className="hidden sm:flex basis-1/5 sm:basis-full" justify="end">
        <NavbarItem className="hidden sm:flex">
          <Select
            label="Select a team"
            className="max-w-xs min-w-48"
            size="sm"
            onChange={selectTeam}
            selectedKeys={[team_id || 'create']}
            items={teams}
            disallowEmptySelection
          >
            {(team) => (
              <SelectItem key={team.value} value={team.value}>
                {team.label}
              </SelectItem>
            )}
          </Select>
        </NavbarItem>
        <NavbarItem className="hidden sm:flex gap-2">
          <Link isExternal href={appSiteConfig.links.github} aria-label="Github">
            <GithubIcon className="text-default-500" />
          </Link>
          <Link isExternal href={appSiteConfig.links.discord} aria-label="Discord">
            <DiscordIcon className="text-default-500" />
          </Link>
          {/* <ThemeSwitch /> */}
          <I18nSwitch />
        </NavbarItem>
        <NavbarItem className="hidden sm:flex">
          {account ? (
            <Avatar
              name={account.user?.name}
              email={account.user?.email}
              avatarUrl={account.user?.avatar}
            />
          ) : (
            <RouterLink to={'/login'}>
              <button className="text-white bg-maya p-[3px] rounded-lg w-full max-w-[300px] font-bold h-9 text-sm">
                <div className="bg-black hover:bg-[#1e293b] flex w-full h-full items-center justify-center  rounded-md px-4">
                  {t('Sign in')}
                </div>
              </button>
            </RouterLink>
          )}
        </NavbarItem>
      </NavbarContent>
      <NavbarContent className="sm:hidden basis-1 pl-4" justify="end">
        <Link isExternal href={appSiteConfig.links.github} aria-label="Github">
          <GithubIcon className="text-default-500" />
        </Link>
        {/* <ThemeSwitch /> */}
        <NavbarMenuToggle />
      </NavbarContent>
      <NavbarMenu>
        <div className="mx-4 mt-2 flex flex-col gap-2">
          {appSiteConfig.navMenuItems.map((item, index) => (
            <NavbarMenuItem key={`${item}-${index}`}>
              <Link
                color={
                  index === 2
                    ? 'primary'
                    : index === appSiteConfig.navMenuItems.length - 1
                      ? 'danger'
                      : 'foreground'
                }
                href="#"
                size="lg"
              >
                {item.label}
              </Link>
            </NavbarMenuItem>
          ))}
        </div>
      </NavbarMenu>
    </NextUINavbar>
  );
};
