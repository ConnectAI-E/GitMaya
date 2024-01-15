import type { FC } from 'react';
import { GithubIcon } from '@/components/icons';
import { Link } from 'react-router-dom';

export const Actions: FC = () => {
  return (
    <div style={{ textAlign: 'center' }}>
      <div className="cta-container inline-flex justify-center gap-3.5">
        <div className="streamer-button group relative mx-auto  w-fit overflow-hidden rounded-xl p-[1px] font-bold transition-all duration-300 hover:shadow-[0_0_2rem_-0.5rem_#fff8] md:mr-0 lg:mr-auto dark:block">
          <Link to="/app/people">
            <span className="inline-flex h-full w-fit items-center gap-2 rounded-xl px-4 py-2 transition-all duration-300 bg-neutral-900 text-white group-hover:bg-black">
              <GithubIcon className="h-4 w-4" />
              Try with your github
            </span>
          </Link>
        </div>
      </div>
      <div style={{ marginTop: '2rem' }} />
      <a
        href=""
        style={{
          color: 'inherit',
          opacity: 0.7,
          fontSize: 14,
        }}
        target="_blank"
      >
        Learn more details →
      </a>
    </div>
  );
};
