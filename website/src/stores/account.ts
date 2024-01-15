import { create } from 'zustand';
import { createSelectors } from './helper';
import i18n from '@/i18n';
import { getAccount } from '@/api';

interface AccountState {
  account: Github.Account | null;
  setAccount: (account: Github.Account) => void;
  lang: string;
  setLang: (lang: string) => void;
  updateAccount: () => Promise<void>;
}

const useAccountStoreBase = create<AccountState>((set) => ({
  account: null,
  setAccount: (account) => set({ account }),
  lang: localStorage.getItem('lang') || 'en_US',
  setLang: (lang) => {
    i18n.changeLanguage(lang);
    localStorage.setItem('lang', lang);
    set({ lang });
  },
  updateAccount: async () => {
    const { data } = await getAccount();
    set({ account: data });
  },
}));

export const useAccountStore = createSelectors(useAccountStoreBase);
