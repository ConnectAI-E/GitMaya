import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  useDisclosure,
  Input,
} from '@nextui-org/react';
import { forwardRef, useImperativeHandle, useState } from 'react';
import clsx from 'clsx';
import { StepIcon } from './step-guide';
import { LarkIcon } from '@/components/icons';
import { useForm, Controller } from 'react-hook-form';
import useSWRMutation from 'swr/mutation';
import { installApp, getTeamInfo } from '@/api';
import { useAccountStore } from '@/stores';
import useSwr from 'swr';
import { CopyIcon } from '@/components/icons';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';
import { LarkTutior } from './lark-tutior';
export interface LarkInstallationRef {
  isOpen: boolean;
  onOpen: () => void;
  onClose: () => void;
}

export const LarkInstallation = forwardRef<LarkInstallationRef>((_props, ref) => {
  const account = useAccountStore.use.account();
  const team_id = account?.current_team as string;
  const navigate = useNavigate();

  const { isOpen, onOpen, onClose } = useDisclosure();
  const [step, setStep] = useState(0);
  const { trigger, isMutating } = useSWRMutation(
    `/api/team/${team_id}/lark/app`,
    (_url, { arg }: { arg: Lark.Config }) => installApp(team_id, 'lark', arg),
  );
  const { data: teamInfoData } = useSwr(team_id ? `/api/team/${team_id}` : null, () =>
    getTeamInfo(team_id),
  );

  const teamInfo = teamInfoData?.data;

  const steps = [
    {
      title: '创建机器人',
    },
    {
      title: '填写配置信息',
    },
    {
      title: '获取回调地址',
    },
  ];

  const { control, handleSubmit } = useForm({
    defaultValues: {
      name: '',
      app_id: '',
      app_secret: '',
      encrypt_key: '',
      verification_token: '',
    },
  });

  const StepOne = () => {
    const [action, setAction] = useState('auto');

    return (
      <div>
        <h1 className="text-2xl font-bold mb-4">创建机器人</h1>
        <div className="flex flex-col gap-4">
          <Button
            className={clsx('p-4 text-left connectai-auto-deploy-lark', {
              'bg-maya text-white': action === 'auto',
            })}
            onClick={() => setAction('auto')}
          >
            一键重新部署至（Connect-AI）
          </Button>
          <Button
            className={clsx('p-4 text-left', {
              'bg-maya text-white': action === 'manual',
            })}
            onClick={() => setAction('manual')}
          >
            自行前往开发者平台，创建应用
          </Button>
        </div>
      </div>
    );
  };

  const StepTwo = () => {
    return (
      <form className="flex flex-col gap-4">
        <div className="flex items-center gap-6 max-w-lg">
          <Controller
            name="name"
            control={control}
            rules={{ required: true }}
            render={({ field }) => (
              <Input isRequired label="NAME" placeholder="Enter your robot name " {...field} />
            )}
          />
          <Controller
            name="app_id"
            control={control}
            rules={{ required: true }}
            render={({ field }) => (
              <Input isRequired label="APP_ID" placeholder="Enter your app id " {...field} />
            )}
          />
        </div>
        <div className="flex items-center gap-6 max-w-lg">
          <Controller
            name="app_secret"
            control={control}
            rules={{ required: true }}
            render={({ field }) => (
              <Input
                isRequired
                label="APP_SECRET"
                placeholder="Enter your app secret "
                {...field}
              />
            )}
          />
          <Controller
            name="encrypt_key"
            control={control}
            rules={{ required: true }}
            render={({ field }) => (
              <Input
                isRequired
                label="ENCRYPT_KEY"
                placeholder="Enter your encrypt key "
                {...field}
              />
            )}
          />
        </div>
        <div className="flex items-center gap-6 max-w-lg">
          <Controller
            name="verification_token"
            control={control}
            rules={{ required: true }}
            render={({ field }) => (
              <Input
                isRequired
                label="VERIFICATION_TOKEN"
                placeholder="Enter your verification token "
                {...field}
              />
            )}
          />
        </div>
      </form>
    );
  };

  const StepThird = () => {
    const callbackUrl = `${location.origin}/api/feishu/hook/${teamInfo?.im_application?.app_id}`;

    const copyCallbackUrl = () => {
      navigator.clipboard.writeText(callbackUrl);
      toast.success('Copied !');
    };
    return (
      <div className="flex items-center gap-6 max-w-lg">
        <Input
          isRequired
          label="CALLBACK_URL"
          disabled
          value={callbackUrl}
          endContent={<CopyIcon className="cursor-pointer" onClick={copyCallbackUrl} />}
        />
      </div>
    );
  };

  const save = async (data: Lark.Config) => {
    await trigger(data);
    toast.success('Saved !');
    nextStep();
  };

  const stepComponents: Record<number, React.FC> = {
    0: StepOne,
    1: StepTwo,
    2: StepThird,
  };

  const StepComponent = stepComponents[step];

  useImperativeHandle(ref, () => ({
    isOpen,
    onOpen,
    onClose,
  }));

  const nextStep = () => {
    setStep((step) => step + 1);
  };

  const prevStep = () => {
    setStep((step) => step - 1);
  };

  const finishSetting = () => {
    onClose();
    navigate('/app/people');
  };

  return (
    <Modal size={'5xl'} isOpen={isOpen} onClose={onClose}>
      <ModalContent>
        {(onClose) => (
          <>
            <ModalHeader className="flex items-center gap-1">
              <LarkIcon /> <span>Lark Setting</span>
            </ModalHeader>
            <ModalBody>
              <div className="flex w-full gap-4">
                <div className="w-1/2">
                  <LarkTutior step={step} />
                </div>
                <div className="flex-1">
                  <div>
                    <nav className="w-full">
                      <ol role="list" className="overflow-hidden flex w-full gap-2">
                        {steps.map((stepProps, index) => (
                          <li key={index} className={clsx('pb-10 flex-center flex-1')}>
                            <StepIcon className="flex-shrink-0" index={index} step={step} />
                            <span
                              className={clsx(
                                'text-sm font-medium flex-grow mx-2 whitespace-nowrap',
                                {
                                  'text-maya': index === step,
                                  'text-gray-500': step <= index,
                                  'text-black': step > index,
                                },
                              )}
                            >
                              {stepProps.title}
                            </span>
                            {index !== steps.length - 1 && (
                              <span className="h-1 w-full bg-maya"></span>
                            )}
                          </li>
                        ))}
                      </ol>
                    </nav>
                    <StepComponent />
                  </div>
                </div>
              </div>
            </ModalBody>
            <ModalFooter>
              <Button color="danger" variant="light" onPress={onClose}>
                取消
              </Button>

              {step === 0 && (
                <Button color="primary" onPress={nextStep} className="bg-maya">
                  下一步
                </Button>
              )}
              {step === 1 && (
                <>
                  <Button variant="light" onPress={prevStep}>
                    上一步
                  </Button>
                  <Button
                    disabled={isMutating}
                    color="primary"
                    className="bg-maya"
                    onClick={handleSubmit(save)}
                  >
                    保存
                  </Button>
                  {
                    // TODO: remove this
                  }
                  {import.meta.env.DEV && (
                    <Button color="primary" onPress={nextStep} className="bg-maya">
                      下一步
                    </Button>
                  )}
                </>
              )}
              {step === 2 && (
                <>
                  <Button variant="light" onPress={prevStep}>
                    上一步
                  </Button>
                  <Button color="primary" className="bg-maya" onPress={finishSetting}>
                    完成配置
                  </Button>
                </>
              )}
            </ModalFooter>
          </>
        )}
      </ModalContent>
    </Modal>
  );
});
