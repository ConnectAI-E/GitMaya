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
    homepage: str = None
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


class RepoEvent(BaseEvent):
    action: str
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
