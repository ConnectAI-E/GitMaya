import { Hero } from '@/layout/app';
import { Footer } from '@/layout/footer';
import {
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  Spinner,
  AvatarGroup,
  Avatar,
  Tooltip,
  AvatarIcon,
  Dropdown,
  DropdownTrigger,
  DropdownMenu,
  DropdownItem,
  Button,
} from '@nextui-org/react';
import { useCallback } from 'react';
import { getRepos, createChat } from '@/api';
import useSwr from 'swr';
import useSWRMutation from 'swr/mutation';
import { useAccountStore } from '@/stores';
import { RefreshIcon } from '@/components/icons';

const columns = [
  {
    name: 'Repo',
    uid: 'repo',
  },
  { name: 'Member', uid: 'member' },
  {
    name: 'Chat',
    uid: 'chat',
  },
  { name: 'Actions', uid: 'actions' },
];

const Repo = () => {
  const account = useAccountStore.use.account();

  const team_id = account?.current_team as string;

  const { trigger } = useSWRMutation(
    `/api/team/${team_id}/repo/repo_id/chat`,
    (
      _url,
      {
        arg,
      }: {
        arg: {
          repo_id: string;
        };
      },
    ) => createChat(team_id, arg.repo_id),
  );

  const { data, mutate, isLoading } = useSwr(team_id ? `/api/team/${team_id}/repo` : null, () =>
    getRepos(team_id, { size: 999, page: 1 }),
  );

  const teamRepos = data?.data || [];

  const handleCreateChat = async (repo_id: string) => {
    try {
      await trigger({
        repo_id,
      });
      mutate();
    } catch (error) {
      console.error(error);
    }
  };

  const viewChat = async (openChatId: string) => {
    const larkAppLinkUrl = `https://applink.feishu.cn/client/chat/open?openChatId=${openChatId}`;
    window.open(larkAppLinkUrl, '_blank');
  };

  const renderCell = useCallback((repo: Github.Repo, columnKey: string) => {
    switch (columnKey) {
      case 'repo':
        return <div>{repo.name}</div>;
      case 'member':
        return (
          <AvatarGroup
            className="justify-start"
            isBordered
            max={3}
            renderCount={(count) => (
              <div className="flex items-center">
                <Tooltip
                  content={repo.users
                    ?.slice(0, count)
                    ?.map((user) => user.name)
                    .join(', ')}
                >
                  <Avatar
                    icon={<AvatarIcon />}
                    name={count.toString()}
                    classNames={{
                      icon: 'text-black/80',
                    }}
                  />
                </Tooltip>
              </div>
            )}
          >
            {repo.users?.map((user) => (
              <Tooltip content={user.name}>
                <Avatar src={user.avatar} name={user.name} />
              </Tooltip>
            ))}
          </AvatarGroup>
        );
      case 'chat':
        return <div>{repo?.chat?.name}</div>;
      case 'actions':
        return (
          <Dropdown>
            <DropdownTrigger>
              <Button className="bg-maya text-white" variant="bordered">
                Actions
              </Button>
            </DropdownTrigger>
            <DropdownMenu aria-label="Example with disabled actions" disabledKeys={['frozen']}>
              {repo.chat ? (
                <DropdownItem key="create" onPress={() => viewChat(repo.chat?.chat_id)}>
                  View chat
                </DropdownItem>
              ) : (
                <DropdownItem key="create" onPress={() => handleCreateChat(repo.id)}>
                  Create chat
                </DropdownItem>
              )}
              <DropdownItem key="frozen" className="text-danger" color="danger">
                Frozen
              </DropdownItem>
            </DropdownMenu>
          </Dropdown>
        );

      default:
        return null;
    }
  }, []);

  const refreshUser = async () => {
    mutate();
  };

  return (
    <div className="flex-grow flex flex-col">
      <div className="bg-black-light-light flex-grow flex flex-col">
        <Hero>
          <div className="flex justify-between items-center mb-5">
            <h1 className="text-3xl font-bold text-white mr-5">Repo Manager</h1>
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
                    <TableColumn key={column.uid}>
                      <div className="flex items-center gap-2">
                        {column.name}
                        {column.uid == 'repo' && (
                          <RefreshIcon size={18} className="cursor-pointer" onClick={refreshUser} />
                        )}
                      </div>
                    </TableColumn>
                  );
                }}
              </TableHeader>
              <TableBody items={teamRepos}>
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

export default Repo;
