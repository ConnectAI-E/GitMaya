import { Input, Checkbox, Select, SelectItem } from '@nextui-org/react';
import { useAccountStore } from '@/stores';
import { useForm, Controller, SubmitHandler } from 'react-hook-form';
interface IFormInput {
  firstName?: string;
  lastName?: string;
  email?: string;
  role?: keyof typeof Roles;
}

export const ContactForm = ({
  setStep,
}: {
  step: number;
  setStep: React.Dispatch<React.SetStateAction<number>>;
}) => {
  const account = useAccountStore.use.account();

  const { control, handleSubmit } = useForm({
    defaultValues: {
      firstName: account?.user.name,
      lastName: '',
      email: account?.user.email,
      role: 'Developer' as keyof typeof Roles,
    },
  });

  const save: SubmitHandler<IFormInput> = (data) => {
    console.log(data);
    setStep((step) => step + 1);
  };

  return (
    <div>
      <form className="flex flex-col gap-4">
        <div className="flex items-center gap-6 max-w-lg">
          <Controller
            name="firstName"
            control={control}
            rules={{ required: true }}
            render={({ field }) => (
              <Input
                isRequired
                label="First name"
                placeholder="Enter your first name "
                {...field}
              />
            )}
          />
          <Controller
            name="lastName"
            control={control}
            render={({ field }) => (
              <Input label="Last name" placeholder="Enter your last name " {...field} />
            )}
          />
        </div>
        <div className="max-w-lg">
          <Controller
            name="email"
            control={control}
            rules={{ required: true }}
            render={({ field }) => (
              <Input
                isRequired
                label="Email address"
                placeholder="Enter your email"
                type="email"
                {...field}
              />
            )}
          />
        </div>
        <div className="max-w-lg">
          <Controller
            name="role"
            control={control}
            rules={{ required: true }}
            render={({ field }) => (
              <Select
                {...field}
                defaultSelectedKeys={['Developer']}
                isRequired
                label="Role"
                placeholder="Select an role"
                value={field.value as string}
              >
                {Roles.map((role) => (
                  <SelectItem key={role.value} value={role.value}>
                    {role.label}
                  </SelectItem>
                ))}
              </Select>
            )}
          />
        </div>
        <div className="max-w-lg mb-2">
          <Checkbox className="items-start">
            <span className="text-black">I'd like to subscribe to the monthly newsletter</span>
            <p className="text-gray-500">
              Subscribe to our monthly newsletter to be the first one to hear about product updates.
              No spam, we promise.
            </p>
          </Checkbox>
        </div>
      </form>
      <div className="max-w-lg flex">
        <div className="ml-auto">
          <div className="inline-block justify-center w-full max-w-[300px]">
            <div className="relative group">
              <button
                onClick={handleSubmit(save)}
                className="transition duration-500 relative leading-none flex items-center justify-center text-white rounded-md py-2.5 text-center px-4 w-full max-w-[300px] bg-maya font-bold h-9 text-sm"
              >
                <div className="flex gap-2 md:gap-4 margin-auto">
                  <span className="m-auto">Save</span>
                </div>
              </button>
            </div>
          </div>
        </div>
        <div className="ml-2">
          <button className="text-white bg-maya p-[3px] rounded-lg w-full max-w-[300px] font-bold h-9 text-sm">
            <div className="bg-white text-black hover:bg-gray-200 flex w-full h-full items-center justify-center  rounded-md px-4">
              <div>Cancel</div>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

export const Roles = [
  {
    label: 'Developer',
    value: 'Developer',
  },
  {
    label: 'Team Leader',
    value: 'Team Leader',
  },
  {
    label: 'Engineering Director',
    value: 'Engineering Director',
  },
  {
    label: 'VP/CTO',
    value: 'VP/CTO',
  },
  {
    label: 'Product Manager',
    value: 'Product Manager',
  },
  {
    label: 'Other',
    value: 'Other',
  },
];
