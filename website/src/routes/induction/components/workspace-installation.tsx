import { LarkWhiteIcon } from '@/components/icons';
import { LarkInstallation, type LarkInstallationRef } from './lark-installation';
import { useRef } from 'react';
export const WorkSpaceInstallation = () => {
  const larkInstallationRef = useRef<LarkInstallationRef | null>(null);

  const installLark = () => {
    larkInstallationRef.current?.onOpen();
  };

  return (
    <main className="max-w-4xl">
      <div className="grid grid-cols-1 items-center justify-center mt-8 gap-8">
        {/* <Link className="flex items-center text-center text-sm underline text-primary" to="/login">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            aria-hidden="true"
            className="h-5 w-5"
          >
            <path
              fill-rule="evenodd"
              d="M12.79 5.23a.75.75 0 01-.02 1.06L8.832 10l3.938 3.71a.75.75 0 11-1.04 1.08l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 011.06.02z"
              clip-rule="evenodd"
            ></path>
          </svg>
          Using GitLab ?
        </Link> */}
        <div className="text-center">
          <div className="inline-block justify-center w-full max-w-[300px]">
            <div className="relative group">
              <button
                onClick={installLark}
                className="transition duration-500 relative leading-none flex items-center justify-center text-white font-medium rounded-md py-2.5 text-center px-4 w-full max-w-[300px] bg-maya  h-14 text-base"
              >
                <div className="flex gap-2 md:gap-4 margin-auto">
                  <LarkWhiteIcon size={30} />
                  <span className="m-auto">Add to Lark</span>
                </div>
              </button>
            </div>
          </div>
        </div>
        {/* <div className="items-center">
          <div className="inline-block justify-center w-full max-w-[300px]">
            <div className="relative group">
              <button className="transition duration-500 relative leading-none flex items-center justify-center text-white font-medium rounded-md py-2.5 text-center px-4 w-full max-w-[300px]  h-14 text-base bg-gray-500 cursor-not-allowed">
                <div className="flex gap-2 md:gap-4 margin-auto">
                  <SlackIcon size={30} />
                  <span className="m-auto">Add to Slack</span>
                </div>
              </button>
            </div>
          </div>
        </div>
        <div className="items-center">
          <div className="inline-block justify-center w-full max-w-[300px]">
            <div className="relative group">
              <button className="transition duration-500 relative leading-none flex items-center justify-center text-white font-medium rounded-md py-2.5 text-center px-4 w-full max-w-[300px] h-14 text-base bg-gray-500 cursor-not-allowed">
                <div className="flex gap-2 md:gap-4 margin-auto">
                  <DiscordIcon size={30} />
                  <span className="m-auto">Add to Discord</span>
                </div>
              </button>
            </div>
          </div>
        </div> */}
      </div>
      <LarkInstallation ref={larkInstallationRef} />
    </main>
  );
};
