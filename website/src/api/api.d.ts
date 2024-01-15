declare namespace Github {
  interface Account {
    current_team: string;
    is_team_admin: boolean;
    user: User;
  }
  interface User {
    avatar: string;
    created: string;
    email: string;
    extra: {
      avatar_url: string;
      bio: null | string;
      blog: string;
      company: null | string;
      created_at: string;
      email: string;
      events_url: string;
      followers: number;
      followers_url: string;
      following: number;
      following_url: string;
      gists_url: string;
      gravatar_id: string;
      hireable: null | boolean;
      html_url: string;
      id: number;
      location: string;
      login: string;
      name: string;
      node_id: string;
      organizations_url: string;
      public_gists: number;
      public_repos: number;
      received_events_url: string;
      repos_url: string;
      site_admin: boolean;
      starred_url: string;
      subscriptions_url: string;
      twitter_username: null | string;
      type: string;
      updated_at: string;
      url: string;
    };
    id: string;
    modified: string;
    name: string;
    status: number;
    telephone: null | string;
    unionid: string;
  }

  interface Team {
    created: string;
    description: string | null;
    extra: Record<string, unknown>;
    id: string;
    modified: string;
    name: string;
    status: number;
    user_id: string;
  }

  interface TeamMember {
    code_user: {
      avatar: string;
      email: string;
      id: string;
      name: string;
      user_id: string;
    };
    id: string;
    im_user: { avatar: string; email: string; id: string; name: string; user_id: string };
    status: number;
  }

  interface TeamInfo {
    code_application: CodeApplication;
    im_application: ImApplication;
    team: Team;
  }

  interface CodeApplication {
    created: string;
    extra: Record<string, unknown>;
    id: string;
    installation_id: string;
    modified: string;
    platform: string;
    status: number;
    team_id: string;
  }

  interface ImApplication {
    app_id: string;
    app_secret: string;
    created: string;
    extra: Record<string, unknown>;
    id: string;
    modified: string;
    platform: string;
    status: number;
    team_id: string;
  }

  interface Repo {
    chat: {
      chat_id: string;
      id: string;
      name: string;
    };
    id: string;
    name: string;
    users: User[];
  }
}

declare namespace Lark {
  interface Config {
    name: string;
    app_id: string;
    app_secret: string;
    encrypt_key: string;
    verification_token: string;
  }

  interface User {
    label: string;
    value: string;
    avatar: string;
    email?: string;
  }
}
