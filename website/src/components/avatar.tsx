import {
  DropdownItem,
  DropdownTrigger,
  Dropdown,
  DropdownMenu,
  Avatar as NextAvatar,
} from '@nextui-org/react';

interface AvatarProps {
  name: string;
  email: string;
  avatarUrl: string;
}

export const Avatar = ({ email, name, avatarUrl }: AvatarProps) => {
  return (
    <Dropdown placement="bottom-end">
      <DropdownTrigger>
        <NextAvatar
          isBordered
          as="button"
          className="transition-transform"
          color="default"
          size="sm"
          name={name}
          src={avatarUrl}
        />
      </DropdownTrigger>
      <DropdownMenu aria-label="Profile Actions" variant="flat">
        <DropdownItem key="profile" className="h-14 gap-2">
          <p className="font-semibold">{name}</p>
          <p className="font-semibold">{email}</p>
        </DropdownItem>
        <DropdownItem key="logout" color="danger">
          Log Out
        </DropdownItem>
      </DropdownMenu>
    </Dropdown>
  );
};
