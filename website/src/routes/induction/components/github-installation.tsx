// import { Link } from 'react-router-dom';
import { GithubIcon } from '@/components/icons';
import { useOauthDialog } from '@/hooks';

export const GithubInstallation = ({
  setStep,
}: {
  step: number;
  setStep: React.Dispatch<React.SetStateAction<number>>;
}) => {
  const handleSignInGithub = useOauthDialog({
    url: '/api/github/install',
    event: 'installation',
    callback: () => setStep((step) => step + 1),
  });
  return (
    <main className="max-w-4xl">
      <div className="grid grid-cols-1 items-center justify-center mt-8">
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
        <div onClick={handleSignInGithub} className="text-center">
          <div>
            <div className="inline-block justify-center w-full max-w-[300px]">
              <div className="relative group">
                <button className="transition duration-500 relative leading-none flex items-center justify-center text-white font-medium rounded-md py-2.5 text-center px-4 w-full max-w-[300px] bg-maya  h-14 text-base">
                  <div className="flex gap-2 md:gap-4 margin-auto">
                    <GithubIcon size={30} />
                    <span className="m-auto">Add to GitHub</span>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
};
