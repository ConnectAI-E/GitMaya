import { SunFilledIcon, MoonFilledIcon } from '@/components/icons';
import useDarkMode from 'use-dark-mode';
export const ThemeSwitch = () => {
  const darkMode = useDarkMode(false);
  return (
    <div className="text-default-500 cursor-pointer">
      {darkMode.value ? (
        <MoonFilledIcon onClick={darkMode.disable} />
      ) : (
        <SunFilledIcon onClick={darkMode.enable} />
      )}
    </div>
  );
};
