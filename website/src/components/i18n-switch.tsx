import { Dropdown, DropdownTrigger, DropdownMenu, DropdownItem } from '@nextui-org/react';
import { I18nIcon } from '@/components/icons';
import i18n from '@/i18n';

export const I18nSwitch = () => {
  const onAction = (key: string | number) => {
    i18n.changeLanguage(key as string);
  };
  return (
    <div className="flex items-center gap-4">
      <Dropdown placement="bottom-end">
        <DropdownTrigger>
          <span className="text-default-500 cursor-pointer">
            <I18nIcon />
          </span>
        </DropdownTrigger>
        <DropdownMenu aria-label="I18n Actions" variant="flat" onAction={onAction}>
          <DropdownItem key="en-US">English</DropdownItem>
          <DropdownItem key="zh-CN">简体中文</DropdownItem>
          <DropdownItem key="vi-VN">Tiếng Việt</DropdownItem>
        </DropdownMenu>
      </Dropdown>
    </div>
  );
};
