import type { Dispatch, SetStateAction } from 'react';
import clsx from 'clsx';

type StepProps = {
  title: string;
  description: string;
};

export const StepIcon = ({
  index,
  step,
  onClick,
  className,
}: {
  index: number;
  step: number;
  onClick?: () => void;
  className?: string;
}) => (
  <span
    onClick={onClick}
    className={clsx(
      'flex h-9 items-center',
      {
        'cursor-pointer': step >= index,
      },
      className,
    )}
    aria-hidden="true"
  >
    <span
      className={clsx('relative z-10 flex h-8 w-8 items-center justify-center rounded-full', {
        'group-hover:bg-pink-600 bg-maya': step > index,
        'bg-white border-2': step <= index,
        'border-[#ec4899]': index === step,
        'border-gray-300': index !== step,
      })}
    >
      {step > index ? (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
          aria-hidden="true"
          className="h-5 w-5 text-white"
        >
          <path
            fill-rule="evenodd"
            d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z"
            clip-rule="evenodd"
          ></path>
        </svg>
      ) : (
        index === step && <span className="h-2.5 w-2.5 rounded-full bg-maya"></span>
      )}
    </span>
  </span>
);

export const StepGuide = ({
  step,
  setStep,
}: {
  step: number;
  setStep: Dispatch<SetStateAction<number>>;
}) => {
  const steps: StepProps[] = [
    {
      title: 'Contact details',
      description: 'How can we communicate with you?',
    },
    {
      title: 'Add your code repository',
      description: 'Pullpo connects to GitHub.',
    },
    {
      title: 'Add your Lark workspace',
      description: 'Enable developer feedback and PR - Channels.',
    },
  ];

  return (
    <nav aria-label="install-step" className="w-max m-10 self-top">
      <ol role="list" className="overflow-hidden">
        {steps.map((stepProps, index) => (
          <li key={index} className="pb-10 relative">
            {index !== steps.length - 1 && (
              <div
                className={clsx('absolute left-4 top-4 -ml-px mt-0.5 h-full w-0.5', {
                  'bg-maya': step > index,
                  'bg-gray-300': step <= index,
                })}
                aria-hidden="true"
              ></div>
            )}
            <div className={clsx('group relative flex items-start')}>
              <StepIcon
                index={index}
                step={step}
                onClick={() => {
                  // TODO: remove this
                  if (import.meta.env.DEV) {
                    setStep(index);
                  }
                }}
              />
              <span className="ml-4 flex min-w-0 flex-col">
                <span
                  className={clsx('text-sm font-medium', {
                    'text-maya': index === step,
                    'text-gray-500': step <= index,
                    'text-black': step > index,
                  })}
                >
                  {stepProps.title}
                </span>
                <span className="text-sm text-gray-500">{stepProps.description}</span>
              </span>
            </div>
          </li>
        ))}
      </ol>
    </nav>
  );
};
