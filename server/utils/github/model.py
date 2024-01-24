from typing import Optional

from pydantic import BaseModel


class Installation(BaseModel):
    id: int


class Sender(BaseModel):
    type: str
    login: str  # name
    id: int


class Organization(BaseModel):
    login: str
    id: int


class BaseEvent(BaseModel):
    organization: Optional[Organization] = None
    sender: Sender
    installation: Optional[Installation] = None


class Repository(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    topics: Optional[list[str]] = []
    visibility: str  # public/private
    private: bool
    archived: bool
    homepage: Optional[str] = None
    open_issues_count: int
    stargazers_count: int
    forks_count: int

    updated_at: str


class Label(BaseModel):
    id: int
    name: str
    description: Optional[str] = None


class User(BaseModel):
    id: int
    login: str
    type: str
    avatar_url: Optional[str] = None
    email: Optional[str] = None


class PRInIssue(BaseModel):
    url: str


class Issue(BaseModel):
    id: int
    number: int
    title: str
    body: Optional[str] = None
    state: str  # open/closed
    labels: Optional[list[Label]] = []
    comments: int
    created_at: str
    updated_at: str
    assignee: Optional[User] = None
    assignees: Optional[list[User]] = []
    pull_request: Optional[PRInIssue] = None


class PerformedViaGithubApp(BaseModel):
    id: int
    name: str  # == GITHUB_APP_NAME in env
    owner: User


class IssueComment(BaseModel):
    id: int
    body: str
    performed_via_github_app: Optional[PerformedViaGithubApp] = None


class Branch(BaseModel):
    label: str
    ref: str
    sha: str


class PullRequest(BaseModel):
    id: int
    number: int
    title: str
    body: Optional[str] = None
    state: str  # open/closed
    merged: Optional[bool] = False
    labels: Optional[list[Label]] = []
    comments: int
    created_at: str
    updated_at: str
    assignee: Optional[User] = None
    assignees: Optional[list[User]] = []
    base: Branch
    head: Branch

    comments: int
    review_comments: int
    commits: int
    additions: int
    deletions: int
    changed_files: int
    requested_reviewers: Optional[list[User]] = []


class MemberShip(BaseModel):
    role: str
    state: str
    user: User


class Committer(BaseModel):
    date: Optional[str] = None
    name: str
    email: str
    username: str


Author = Committer


class Commit(BaseModel):
    id: str
    message: str
    author: Author
    committer: Committer
    url: str


class RepoEvent(BaseEvent):
    action: str
    repository: Repository


class StarEvent(BaseEvent):
    action: str
    starred_at: Optional[str] = None
    repository: Repository


class ForkEvent(BaseEvent):
    action: Optional[str] = None
    forkee: object
    repository: Repository


class IssueEvent(BaseEvent):
    action: str
    issue: Issue
    repository: Repository


class IssueCommentEvent(BaseEvent):
    action: str
    issue: Issue
    comment: IssueComment
    repository: Repository


class PullRequestEvent(BaseEvent):
    action: str
    pull_request: PullRequest
    repository: Repository


class OrganizationEvent(BaseEvent):
    action: str
    organization: Organization
    membership: Optional[MemberShip] = None


class PushEvent(BaseEvent):
    after: str
    before: str
    ref: str
    commits: list[Commit]
    repository: Repository
