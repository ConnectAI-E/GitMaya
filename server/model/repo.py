from app import db
from model.schema import BindUser, ObjID, Repo, RepoUser, User
from utils.github.repo import GitHubAppRepo


def create_repo_from_github(
    repo: dict, org_name: str, application_id: str, github_app: GitHubAppRepo
) -> Repo:
    """Create repo from github

    Args:
        repo (dict): repo info from github
        org_name (str): organization name
        application_id (str): application id
        github_app (GitHubAppRepo): github app instance

    Returns:
        Repo: repo instance
    """

    # 检查是否已经存在
    try:
        current_repo = Repo.query.filter_by(repo_id=repo["id"]).first()

        if current_repo is None:
            new_repo = Repo(
                id=ObjID.new_id(),
                application_id=application_id,
                repo_id=repo["id"],
                name=repo["name"],
                description=repo["description"],
            )
            db.session.add(new_repo)
            db.session.flush()

            current_repo = new_repo

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

            # 根据 permission 创建 repo_user
            permissions = repo_user["permissions"]
            if permissions["admin"]:
                permission = "admin"
            elif permissions["maintain"]:
                permission = "maintain"
            elif permissions["push"]:
                permission = "push"
            else:
                continue

            if current_repo_user is not None:
                # 更新权限
                current_repo_user.permission = permission
                db.session.add(current_repo_user)
                db.session.flush()
                continue

            new_repo_user = RepoUser(
                id=ObjID.new_id(),
                application_id=application_id,
                repo_id=current_repo.id,
                bind_user_id=bind_user.id,
                permission=permission,
            )
            db.session.add(new_repo_user)
            db.session.flush()

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        raise e

    return current_repo
