import { GithubIcon } from '@/components/icons';
import { Footer } from '@/layout/footer';
import { useOauthDialog } from '@/hooks';
import { useNavigate } from 'react-router-dom';
import { useAccountStore } from '@/stores';

const Login = () => {
  const navigate = useNavigate();
  const updateAccount = useAccountStore.use.updateAccount();

  const handleSignInGithub = useOauthDialog({
    url: '/api/github/oauth',
    event: 'oauth',
    callback: () => {
      navigate('/app/people');
      updateAccount();
    },
  });

  return (
    <div className="flex flex-col min-h-screen bg-dark overflow-hidden relative isolate">
      <svg
        className="absolute inset-0 -z-10 h-full w-full stroke-white/10 [mask-image:radial-gradient(100%_100%_at_top_right,white,transparent)]"
        aria-hidden="true"
      >
        <defs>
          <pattern
            id="983e3e4c-de6d-4c3f-8d64-b9761d1534cc"
            width="200"
            height="200"
            x="50%"
            y="-1"
            patternUnits="userSpaceOnUse"
          >
            <path d="M.5 200V.5H200" fill="none"></path>
          </pattern>
        </defs>
        <svg x="50%" y="-1" className="overflow-visible fill-gray-800/20">
          <path
            d="M-200 0h201v201h-201Z M600 0h201v201h-201Z M-400 600h201v201h-201Z M200 800h201v201h-201Z"
            strokeWidth="0"
          ></path>
        </svg>
        <rect
          width="100%"
          height="100%"
          strokeWidth="0"
          fill="url(#983e3e4c-de6d-4c3f-8d64-b9761d1534cc)"
        ></rect>
      </svg>
      <svg
        viewBox="0 0 1108 632"
        aria-hidden="true"
        className="absolute top-10 left-[calc(50%-4rem)] -z-10 w-[69.25rem] max-w-none transform-gpu blur-3xl sm:left-[calc(50%-18rem)] lg:left-48 lg:top-[calc(50%-30rem)] xl:left-[calc(50%-24rem)]"
      >
        <path
          fill="url(#175c433f-44f6-4d59-93f0-c5c51ad5566d)"
          fillOpacity=".2"
          d="M235.233 402.609 57.541 321.573.83 631.05l234.404-228.441 320.018 145.945c-65.036-115.261-134.286-322.756 109.01-230.655C968.382 433.026 1031 651.247 1092.23 459.36c48.98-153.51-34.51-321.107-82.37-385.717L810.952 324.222 648.261.088 235.233 402.609Z"
        ></path>
        <defs>
          <linearGradient
            id="175c433f-44f6-4d59-93f0-c5c51ad5566d"
            x1="1220.59"
            x2="-85.053"
            y1="432.766"
            y2="638.714"
            gradientUnits="userSpaceOnUse"
          >
            <stop stopColor="#4F46E5"></stop>
            <stop offset="1" stopColor="#80CAFF"></stop>
          </linearGradient>
        </defs>
      </svg>
      <div className="grow flex flex-col">
        <div className="w-full grow items-center justify-center flex p-2">
          <div className="p-[1px]  rounded-xl shadow-xl bg-maya">
            <div className="items-center justify-center flex flex-col gap-y-4 p-20 rounded-xl bg-[#1e293b]">
              <h1 className="text-black-light-light text-3xl font-bold">
                <span> Welcome to </span>
                <span className="text-maya font-extrabold">GitMaya</span>
                <span>, let's get started!</span>
              </h1>
              <div className="flex flex-col text-left w-full gap-y-6 items-center mt-6">
                <p className="text-black-light-light text-md w-full text-center">
                  · Sign in with your team's repository
                  <span className="text-gray-400 font-light">(preferred)</span>.
                </p>
                <div className="flex flex-col lg:flex-row w-full gap-4 align-top content-end justify-center">
                  <div className="flex flex-col items-center ">
                    <button
                      onClick={handleSignInGithub}
                      type="button"
                      className="text-black bg-white font-bold rounded-lg text-base px-5 py-2.5 text-center inline-flex items-center dark:hover:bg-white/90 me-2 mb-2 w-64 justify-center"
                    >
                      <GithubIcon className="me-2" size={20} />
                      Sign in with Github
                    </button>
                  </div>
                  {/* <div className="flex flex-col items-center">
                    <button
                      type="button"
                      className="text-black bg-white font-bold rounded-lg text-base px-5 py-2.5 text-center inline-flex items-center dark:hover:bg-white/90 me-2 mb-2 w-64 justify-center"
                    >
                      <GitLabIcon className="me-2" size={20} />
                      Sign in with GitLab
                      <span className="text-gray-400 font-light text-xs ml-1">(SaaS)</span>
                    </button>
                  </div>
                  <div className="flex flex-col items-center">
                    <button
                      disabled
                      type="button"
                      className="text-black bg-white font-bold rounded-lg text-base px-5 py-2.5 text-center inline-flex items-center dark:hover:bg-white/90 me-2 mb-2 cursor-not-allowed w-64 justify-center"
                    >
                      <GitLabIcon className="me-2 fill-black" size={20} />
                      Sign in with GitLab
                    </button>
                    <p className="text-gray-400 text-xs mx-2">
                      Hosted on https://
                      <span className="text-black-light-light font-light">
                        <input
                          className="border-none  focus:border-info focus:ring-info w-36 p-1 text-sm rounded-sm"
                          type="text"
                          placeholder="gitlab.gitmaya.com"
                        />
                      </span>
                    </p>
                  </div> */}
                </div>
              </div>
              {/* <p className="text-md w-full">
                · Not a developer? Log in with your team's Slack workspace
                <span className="text-gray-400 font-light">(in view-only mode)</span>.
              </p>
              <button
                type="button"
                className="text-black bg-white font-bold rounded-lg text-base px-5 py-2.5 text-center inline-flex items-center dark:hover:bg-white/90 me-2 mb-2 w-64 justify-center"
              >
                <SlackIcon className="me-2" size={20} />
                Sign in with Slack
              </button> */}
            </div>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default Login;
