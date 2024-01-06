from celery_app import celery
from model.schema import BindUser, ObjID, Repo, RepoUser, User, db
from model.team import add_team_member
from utils.github.organization import GitHubAppOrg
from utils.user import create_github_user


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

    for member in members:
        # 已存在的用户不会重复创建
        _, new_bind_user_id = create_github_user(
            github_id=member["id"],
            name=member["login"],
            email=member.get("email", None),
            avatar=member["avatar_url"],
            access_token=None,
            application_id=application_id,
            extra={},
        )

        add_team_member(team_id, new_bind_user_id)

    # 拉取所有组织仓库，创建 Repo
    repos = github_app.get_org_repos(org_name)
    try:
        for repo in repos:
            # 检查是否已经存在
            if Repo.query.filter_by(repo_id=repo["id"]).first() is not None:
                continue

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
            print(repo_users)

            # 检查是否有 bind_user
            for repo_user in repo_users:
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

                new_repo_user = RepoUser(
                    id=ObjID.new_id(),
                    application_id=application_id,
                    repo_id=new_repo.id,
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
    installation_id: str, org_name: str, team_id: str
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

    if members is None or not isinstance(members, list):
        return None

    for member in members:
        # 已存在的用户不会重复创建
        _, new_bind_user_id = create_github_user(
            github_id=member["id"],
            name=member["login"],
            email=member.get("email", None),
            avatar=member["avatar_url"],
            access_token=None,
            application_id=None,
            extra={},
        )

        add_team_member(team_id, new_bind_user_id)

    return members
