import { Hero } from '@/layout/app';
import { Footer } from '@/layout/footer';
import {
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  User,
  Select,
  SelectItem,
  Spinner,
} from '@nextui-org/react';
import { useCallback } from 'react';
import { getPlatformMember, getTeamMember, bindTeamMember, updatePlatformUser } from '@/api';
import useSwr from 'swr';
import useSWRMutation from 'swr/mutation';
import { useAccountStore } from '@/stores';
import { RefreshIcon } from '@/components/icons';

const columns = [
  {
    name: 'GitHub handle',
    uid: 'github',
  },
  {
    name: 'Lark handle',
    uid: 'lark',
  },
  { name: 'Role', uid: 'role' },
];

const People = () => {
  const account = useAccountStore.use.account();

  const team_id = account?.current_team as string;

  const { trigger } = useSWRMutation(
    `api/team/${team_id}/member`,
    (
      _url,
      {
        arg,
      }: {
        arg: {
          code_user_id: string;
          im_user_id: string;
        };
      },
    ) => bindTeamMember(team_id, arg),
  );

  const { trigger: triggerLarkUser } = useSWRMutation(`api/team/${team_id}/lark/user`, () =>
    updatePlatformUser(team_id, 'lark'),
  );

  const { data, mutate } = useSwr(team_id ? `/api/team/${team_id}/member` : null, () =>
    getTeamMember(team_id),
  );

  const {
    data: larkUserData,
    isLoading,
    mutate: mutateLark,
  } = useSwr(team_id ? `/api/team/${team_id}/lark/user` : null, () =>
    getPlatformMember<Lark.User[]>(team_id, 'lark'),
  );

  const teamMember = data?.data || [];

  const larkUsers = larkUserData?.data;

  const bindMember = async (e: React.ChangeEvent<HTMLSelectElement>, user: Github.TeamMember) => {
    const { value } = e.target;
    try {
      await trigger({
        code_user_id: user.code_user.id,
        im_user_id: value,
      });
      mutate();
    } catch (error) {
      console.error(error);
    }
  };

  const renderCell = useCallback(
    (user: Github.TeamMember, columnKey: string) => {
      switch (columnKey) {
        case 'github':
          return (
            <User
              name={user.code_user.name}
              avatarProps={{ radius: 'lg', src: user.code_user.avatar }}
              description={user.code_user.email}
            >
              {user.code_user.email}
            </User>
          );
        case 'lark':
          return (
            <Select
              label="Select a user"
              className="max-w-xs"
              size="sm"
              onChange={(e) => bindMember(e, user)}
              items={larkUsers}
              defaultSelectedKeys={[user.im_user?.id]}
              disallowEmptySelection
            >
              {(user) => <SelectItem key={user.value}>{user.label}</SelectItem>}
            </Select>
          );

        default:
          return null;
      }
    },
    [larkUsers],
  );

  const refreshUser = async () => {
    mutate();
    mutateLark();
    triggerLarkUser();
  };

  return (
    <div className="flex-grow flex flex-col">
      <div className="bg-black-light-light flex-grow flex flex-col">
        <Hero>
          <div className="flex justify-between items-center mb-5">
            <h1 className="text-3xl font-bold text-white mr-5">My organization</h1>
          </div>
          <div
            className="flex items-center p-4 mb-4 text-sm text-yellow-800 rounded-lg bg-yellow-50 dark:bg-gray-800 dark:text-yellow-300"
            role="alert"
          >
            <svg
              className="flex-shrink-0 inline w-4 h-4 me-3"
              aria-hidden="true"
              xmlns="http://www.w3.org/2000/svg"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5ZM9.5 4a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3ZM12 15H8a1 1 0 0 1 0-2h1v-3H8a1 1 0 0 1 0-2h2a1 1 0 0 1 1 1v4h1a1 1 0 0 1 0 2Z" />
            </svg>
            <span className="sr-only">Info</span>
            <div>
              <span className="font-medium">Configuration needed!</span> Please, associate the
              GitHub username to the respective Slack handle of each of your team members.
            </div>
          </div>
        </Hero>
        <main className="bg-light container -mt-32 max-w-7xl mx-auto flex-grow relative">
          {isLoading ? (
            <Spinner label="Loading..." color="warning" className="absolute inset-0" />
          ) : (
            <Table>
              <TableHeader columns={columns}>
                {(column) => {
                  return (
                    <TableColumn key={column.uid} align="start">
                      <div className="flex items-center gap-2">
                        {column.name}
                        {column.uid !== 'role' && (
                          <RefreshIcon size={18} className="cursor-pointer" onClick={refreshUser} />
                        )}
                      </div>
                    </TableColumn>
                  );
                }}
              </TableHeader>
              <TableBody items={teamMember}>
                {(item) => (
                  <TableRow key={item.id}>
                    {(columnKey) => <TableCell>{renderCell(item, columnKey as string)}</TableCell>}
                  </TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </main>
      </div>
      <Footer />
    </div>
  );
};

export default People;
