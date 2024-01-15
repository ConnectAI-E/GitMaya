import request from '@/utils/request';

export const getAccount = () => request.get<Github.Account>('/api/account');

export const getTeams = () => request.get<Github.Team[]>('/api/team/');

export const getTeamInfo = (team_id: string) =>
  request.get<Github.TeamInfo>(`/api/team/${team_id}`);

export const getTeamMember = (team_id: string) =>
  request.get<Github.TeamMember[]>(`/api/team/${team_id}/member`);

export const bindTeamMember = (
  team_id: string,
  data: {
    code_user_id: string;
    im_user_id: string;
  },
) => request.put(`/api/team/${team_id}/member`, data);

export const getPlatformMember = <T>(team_id: string, platform: string) =>
  request.get<T>(`/api/team/${team_id}/${platform}/user`);

export const installApp = (team_id: string, platform: string, data: unknown) =>
  request.post(`/api/team/${team_id}/${platform}/app`, data);

export const switchTeam = (data: { current_team: string }) => request.post('/api/account', data);

export const getRepos = (
  team_id: string,
  params?: {
    page: number;
    size: number;
  },
) => request.get<Github.Repo[]>(`/api/team/${team_id}/repo`, { params });

export const createChat = (team_id: string, repo_id: string) =>
  request.post(`/api/team/${team_id}/repo/${repo_id}/chat`, {
    name: '', // default
  });

export const updatePlatformUser = (team_id: string, platform: string) =>
  request.post(`/api/team/${team_id}/${platform}/user`);
