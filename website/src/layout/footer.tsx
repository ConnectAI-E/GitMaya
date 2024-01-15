import { useLocalStorageState } from 'ahooks';
import clsx from 'clsx';
import { Logo } from '@/components/icons';
import { Link } from 'react-router-dom';

export const Footer = ({ className }: { className?: string }) => {
  const [showCookie, setShowCookie] = useLocalStorageState(`showCookie`, {
    serializer: JSON.stringify,
    deserializer: JSON.parse,
    defaultValue: true,
  });
  return (
    <footer className={className}>
      <div className="static bottom-0 w-full">
        <div className="h-[1px] w-full bg-maya"></div>
        <div className="flex items-center max-w-6xl mx-auto px-4 sm:px-6 my-8">
          <div className="flex items-center">
            <Link to="/">
              <Logo height={35} width={35} />
            </Link>
          </div>
          <div className="text-xl font-black mx-4 text-gradient text-maya">GitMaya</div>
          <div className="text-black-light text-sm">© All rights reserved.</div>
          <div className="ml-auto flex gap-5">
            <a href="/" target="_blank" rel="noopener noreferrer">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="30"
                height="30"
                aria-labelledby="icon"
                viewBox="0 0 50 50"
                strokeWidth=""
                stroke=""
              >
                <g fill="#cbd5e1">
                  <path
                    fillRule="evenodd"
                    clipRule="evenodd"
                    d="M39.5833 0H10.4167C4.66458 0 0 4.66458 0 10.4167V39.5833C0 45.3354 4.66458 50 10.4167 50H39.5833C45.3375 50 50 45.3354 50 39.5833V10.4167C50 4.66458 45.3375 0 39.5833 0ZM16.6667 39.5833H10.4167V16.6667H16.6667V39.5833ZM13.5417 14.025C11.5292 14.025 9.89583 12.3792 9.89583 10.35C9.89583 8.32083 11.5292 6.675 13.5417 6.675C15.5542 6.675 17.1875 8.32083 17.1875 10.35C17.1875 12.3792 15.5562 14.025 13.5417 14.025ZM41.6667 39.5833H35.4167V27.9083C35.4167 20.8917 27.0833 21.4229 27.0833 27.9083V39.5833H20.8333V16.6667H27.0833V20.3438C29.9917 14.9563 41.6667 14.5583 41.6667 25.5021V39.5833Z"
                  ></path>
                </g>
              </svg>
            </a>
            <a href="/" target="_blank" rel="noopener noreferrer">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="30"
                height="30"
                aria-labelledby="icon"
                viewBox="0 0 30 30"
                strokeWidth=""
                stroke=""
              >
                <g fill="#cbd5e1">
                  <path d="M6.30293 18.9576C6.30293 20.6922 4.88599 22.1091 3.15147 22.1091C1.41694 22.1091 0 20.6922 0 18.9576C0 17.2231 1.41694 15.8062 3.15147 15.8062H6.30293V18.9576ZM7.89088 18.9576C7.89088 17.2231 9.30782 15.8062 11.0423 15.8062C12.7769 15.8062 14.1938 17.2231 14.1938 18.9576V26.8485C14.1938 28.5831 12.7769 30 11.0423 30C9.30782 30 7.89088 28.5831 7.89088 26.8485V18.9576Z"></path>
                  <path d="M11.0423 6.30293C9.30782 6.30293 7.89088 4.88599 7.89088 3.15147C7.89088 1.41694 9.30782 0 11.0423 0C12.7769 0 14.1938 1.41694 14.1938 3.15147V6.30293H11.0423ZM11.0423 7.89088C12.7769 7.89088 14.1938 9.30782 14.1938 11.0423C14.1938 12.7769 12.7769 14.1938 11.0423 14.1938H3.15147C1.41694 14.1938 0 12.7769 0 11.0423C0 9.30782 1.41694 7.89088 3.15147 7.89088H11.0423V7.89088Z"></path>
                  <path d="M23.697 11.0423C23.697 9.30782 25.114 7.89088 26.8485 7.89088C28.583 7.89088 30 9.30782 30 11.0423C30 12.7769 28.583 14.1938 26.8485 14.1938H23.697V11.0423ZM22.1091 11.0423C22.1091 12.7769 20.6921 14.1938 18.9576 14.1938C17.2231 14.1938 15.8062 12.7769 15.8062 11.0423V3.15147C15.8062 1.41694 17.2231 0 18.9576 0C20.6921 0 22.1091 1.41694 22.1091 3.15147V11.0423V11.0423Z"></path>
                  <path d="M18.9576 23.6971C20.6921 23.6971 22.1091 25.114 22.1091 26.8485C22.1091 28.5831 20.6921 30 18.9576 30C17.2231 30 15.8062 28.5831 15.8062 26.8485V23.6971H18.9576ZM18.9576 22.1091C17.2231 22.1091 15.8062 20.6922 15.8062 18.9576C15.8062 17.2231 17.2231 15.8062 18.9576 15.8062H26.8485C28.583 15.8062 30 17.2231 30 18.9576C30 20.6922 28.583 22.1091 26.8485 22.1091H18.9576Z"></path>
                </g>
              </svg>
            </a>
          </div>
        </div>
      </div>
      <div
        className={clsx(
          'fixed z-40 bottom-0 w-full text-white bg-[#1e293b] h-50 ',
          `${showCookie ? 'block' : 'hidden'}`,
        )}
      >
        <div className="max-w-6xl mx-auto px-5 py-5 sm:px-6 flex items-center">
          <div>
            We use cookies in this website to give you the best experience on our site. To find out
            more, read our
            <a href="/" target="_blank" rel="noopener noreferrer" className="text-blue-400">
              <span> privacy policy </span>
            </a>
            and
            <a href="/" target="_blank" rel="noopener noreferrer" className="text-blue-400">
              <span> cookies policy </span>
            </a>
          </div>
          <div className="ml-3">
            <button
              onClick={() => setShowCookie(false)}
              className="text-white bg-maya p-[3px] rounded-lg w-full max-w-[300px] font-bold h-9 text-sm"
            >
              <div className="bg-black hover:bg-[#1e293b] flex w-full h-full items-center justify-center  rounded-md px-4">
                <div>Okay</div>
              </div>
            </button>
          </div>
        </div>
      </div>
    </footer>
  );
};
