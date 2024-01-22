from celery_app import celery
from model.repo import create_repo_from_github
from model.schema import CodeApplication, Team, db
from utils.github.organization import GitHubAppOrg
from utils.github.repo import GitHubAppRepo
from utils.user import create_github_member


@celery.task()
def pull_github_repo(
    org_name: str, installation_id: str, application_id: str, team_id: str
):
    """Pull repo from GitHub, build Repo and RepoUser.

    Args:
        org_name: GitHub organization name.
        installation_id: GitHub App installation id.
        application_id: Code application id.
    """
    # 获取 jwt 和 installation_token

    github_app = GitHubAppOrg(installation_id)

    # 拉取所有组织成员，创建 User 和 BindUser
    members = github_app.get_org_members(org_name)
    # org 只有一个人的时候，members = 0
    if members is None:
        raise Exception("Failed to get org members.")

    # 创建 user 和 team member
    create_github_member(members, application_id, team_id)

    # 拉取所有组织仓库，创建 Repo
    repos = github_app.get_org_repos_accessible()
    github_app = GitHubAppRepo(installation_id)
    try:
        for repo in repos:
            create_repo_from_github(
                repo=repo,
                org_name=org_name,
                application_id=application_id,
                github_app=github_app,
            )

    except Exception as e:
        db.session.rollback()
        raise e


@celery.task()
def pull_github_members(
    installation_id: str, org_name: str, team_id: str, application_id: str = None
) -> list | None:
    """Background task to pull members from GitHub.

    Args:
        installation_id: GitHub App installation id.
        org_name: GitHub organization name.

    Returns:
        list: GitHub members.
    """
    github_app = GitHubAppOrg(installation_id)

    members = github_app.get_org_members(org_name)

    create_github_member(members, application_id, team_id)
    return True


@celery.task()
def pull_github_repo_all():
    """Pull all repo from GitHub, build Repo and RepoUser."""

    task_ids = []
    # 查询所有的 application 和对应的 team
    for team in db.session.query(Team).all():
        application = CodeApplication.query.filter_by(
            team_id=team.id, status=0, platform="github"
        ).first()

        if application is None:
            continue

        task = pull_github_repo.delay(
            org_name=team.name,
            installation_id=application.installation_id,
            application_id=application.id,
            team_id=team.id,
        )
        task_ids.append(task.id)

    return task_ids
