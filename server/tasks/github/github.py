from celery_app import celery
from model.schema import (
    BindUser,
    CodeApplication,
    ObjID,
    Repo,
    RepoUser,
    Team,
    User,
    db,
)
from utils.github.organization import GitHubAppOrg
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
    if members is None or not isinstance(members, list):
        raise Exception("Failed to get org members.")

    # 创建 user 和 team member
    create_github_member(members, application_id, team_id)

    # 拉取所有组织仓库，创建 Repo
    repos = github_app.get_org_repos(org_name)
    try:
        for repo in repos:
            # 检查是否已经存在
            current_repo = Repo.query.filter_by(repo_id=repo["id"]).first()

            new_repo = Repo(
                id=ObjID.new_id(),
                application_id=application_id,
                owner_bind_id=None,  # TODO: 暂定不填写
                repo_id=repo["id"],
                name=repo["name"],
                description=repo["description"],
            )
            db.session.add(new_repo)
            db.session.flush()

            # 拉取仓库成员，创建 RepoUser
            repo_users = github_app.get_repo_collaborators(repo["name"], org_name)

            for repo_user in repo_users:
                # 检查是否有 bind_user，没有则跳过
                bind_user = (
                    db.session.query(BindUser)
                    .filter(
                        User.unionid == repo_user["id"],
                        BindUser.platform == "github",
                        BindUser.application_id == application_id,
                        BindUser.user_id == User.id,
                    )
                    .first()
                )
                if bind_user is None:
                    continue

                # 检查是否有 repo_user，有则跳过
                current_repo_user = (
                    db.session.query(RepoUser)
                    .filter(
                        RepoUser.repo_id == current_repo.id,
                        RepoUser.bind_user_id == bind_user.id,
                        RepoUser.application_id == application_id,
                    )
                    .first()
                )
                if current_repo_user is not None:
                    continue

                new_repo_user = RepoUser(
                    id=ObjID.new_id(),
                    application_id=application_id,
                    repo_id=current_repo.id,
                    bind_user_id=bind_user.id,
                )
                db.session.add(new_repo_user)
                db.session.commit()

        db.session.commit()
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

    return create_github_member(members, application_id, team_id)


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
