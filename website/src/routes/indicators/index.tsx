import { Hero } from '@/layout/app';

const Indicators = () => {
  return (
    <div className="bg-black-light-light flex-grow flex flex-col">
      <Hero>
        <div className="flex-center">
          <h1 className="text-3xl font-bold text-white mr-5">Engineering indicators.</h1>
          <a
            href="mailto:marco@pullpo.io"
            className="rounded-full bg-primary/10 px-3 py-1 text-sm font-semibold leading-6 text-primary ring-1 ring-inset ring-primary/20"
          >
            <div className="flex items-center justify-center">
              <span>Beta. Tell us what you think</span>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
                aria-hidden="true"
                className="w-4 h-4"
              >
                <path
                  fill-rule="evenodd"
                  d="M3 10a.75.75 0 01.75-.75h10.638L10.23 5.29a.75.75 0 111.04-1.08l5.5 5.25a.75.75 0 010 1.08l-5.5 5.25a.75.75 0 11-1.04-1.08l4.158-3.96H3.75A.75.75 0 013 10z"
                  clip-rule="evenodd"
                ></path>
              </svg>
            </div>
          </a>
        </div>
      </Hero>
      <main className="container -mt-40 max-w-7xl mx-auto px-4 sm:px-6 flex-grow bg-white">
        Indicators
      </main>
    </div>
  );
};

export default Indicators;
