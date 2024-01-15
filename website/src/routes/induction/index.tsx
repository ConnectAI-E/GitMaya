import { Footer } from '@/layout/footer';
import { ContactForm, StepGuide, GithubInstallation, WorkSpaceInstallation } from './components';
import { useState } from 'react';
import { HeaderContent } from '@/layout/app';

type StepComponentType = React.FC<{
  step: number;
  setStep: React.Dispatch<React.SetStateAction<number>>;
}>;

const stepComponents: Record<number, StepComponentType> = {
  0: ContactForm,
  1: GithubInstallation,
  2: WorkSpaceInstallation,
};

const stepHeaders: Record<number, JSX.Element> = {
  0: (
    <HeaderContent title="Let's meet each other! 👋">
      <p className="text-md text-black-light-light max-w-7xl px-4 sm:px-6 lg:px-8 mx-auto mt-6">
        We would like to be able to reach out to you via email to better understand the needs of
        your team and to provide taylored assistance if needed.
      </p>
      <p className="text-md text-black-light-light max-w-7xl px-4 sm:px-6 lg:px-8 mx-auto mt-6">
        If you require help or want to provide feedback to GitMaya, you can also contact us at:
        hello@gitmaya.com.
      </p>
    </HeaderContent>
  ),
  1: (
    <HeaderContent title="Connect to your code repository">
      <p className="text-md text-black-light-light max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        Choose the code repository that your team uses. Follow the installation process so that
        Pullpo can connect and keep track of your development metrics.
      </p>
      <p className="text-md text-black-light-light max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        To get you started, Pullpo will process data from the last three months. This can take a few
        minutes depending on the size of your organization.
      </p>
    </HeaderContent>
  ),
  2: (
    <HeaderContent title="Connect to your code repository">
      <p className="text-md text-black-light-light max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        Choose the code repository that your team uses. Follow the installation process so that
        Pullpo can connect and keep track of your development metrics.
      </p>
      <p className="text-md text-black-light-light max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        To get you started, Pullpo will process data from the last three months. This can take a few
        minutes depending on the size of your organization.
      </p>
    </HeaderContent>
  ),
};

const Induction = () => {
  const [step, setStep] = useState(0);
  const StepComponent = stepComponents[step];
  const StepHeader = stepHeaders[step];

  return (
    <div className="bg-black-light-light flex-grow flex flex-col">
      <div className="bg-black">{StepHeader}</div>
      <main className="container max-w-7xl mx-auto px-4 sm:px-6 flex-grow bg-white">
        <div className="grow flex max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <StepGuide step={step} setStep={setStep} />
          <div className="grow p-8">{<StepComponent step={step} setStep={setStep} />}</div>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default Induction;
