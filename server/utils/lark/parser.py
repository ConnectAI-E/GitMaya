import argparse
import logging

import tasks
from utils.constant import TopicType


class GitMayaLarkParser(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            exit_on_error=False, fromfile_prefix_chars="&"
        )
        self.subparsers = self.parser.add_subparsers()
        self.init_subparsers()
        self.command_list = [
            "/help",
            "/man",
            "/match",
            "/issue",
            "/new",
            "/view",
            "/setting",
            "/visit",
            "/access",
            "/rename",
            "/edit",
            "/link",
            "/label",
            "/archive",
            "/unarchive",
            "/insight",
            "/close",
            "/reopen",
            "@GitMaya",
        ]

    def init_subparsers(self):
        parser_help = self.subparsers.add_parser("/help")
        parser_help.set_defaults(func=self.on_help)
        parser_man = self.subparsers.add_parser("/man")
        parser_man.set_defaults(func=self.on_help)

        parser_match = self.subparsers.add_parser("/match", exit_on_error=False)
        parser_match.add_argument("repo_url", nargs="?")
        parser_match.add_argument("chat_name", nargs="?")
        parser_match.set_defaults(func=self.on_match)

        # /issue [title] [@user_1] [@user_2] [[label_1],[label2]]
        parser_issue = self.subparsers.add_parser("/issue")
        parser_issue.add_argument("argv", nargs="*")
        parser_issue.set_defaults(func=self.on_issue)

        parser_new = self.subparsers.add_parser("/new")
        parser_new.set_defaults(func=self.on_new)

        parser_view = self.subparsers.add_parser("/view")
        parser_view.set_defaults(func=self.on_view)

        parser_log = self.subparsers.add_parser("/log")
        parser_log.set_defaults(func=self.on_log)

        parser_diff = self.subparsers.add_parser("/diff")
        parser_diff.set_defaults(func=self.on_diff)

        parser_setting = self.subparsers.add_parser("/setting")
        parser_setting.set_defaults(func=self.on_setting)

        parser_visit = self.subparsers.add_parser("/visit")
        parser_visit.add_argument("visibility", nargs="?")
        parser_visit.set_defaults(func=self.on_visit)

        parser_access = self.subparsers.add_parser("/access")
        parser_access.add_argument("permission", nargs="?")
        parser_access.add_argument("person", nargs="?")
        parser_access.set_defaults(func=self.on_access)

        # /assign [@user_1] [@user_2]
        parser_assign = self.subparsers.add_parser("/assign")
        parser_assign.add_argument("users", nargs="*")
        parser_assign.set_defaults(func=self.on_assign)

        # /review [@user_1] [@user_2]
        parser_review = self.subparsers.add_parser("/review")
        parser_review.add_argument("users", nargs="*")
        parser_review.set_defaults(func=self.on_review)

        # /rename [title]  tit需要支持空格
        parser_rename = self.subparsers.add_parser("/rename")
        parser_rename.add_argument("title", nargs="*")
        parser_rename.set_defaults(func=self.on_rename)

        # /edit\n new body
        parser_edit = self.subparsers.add_parser("/edit")
        # 这里处理body，就直接从content里面拿
        parser_edit.add_argument("desc", nargs="*")
        parser_edit.set_defaults(func=self.on_edit)

        parser_link = self.subparsers.add_parser("/link")
        parser_link.add_argument("homepage", nargs="?")
        parser_link.set_defaults(func=self.on_link)

        # /label [label1] [label2]
        # /label [label1,label2]
        parser_label = self.subparsers.add_parser("/label")
        parser_label.add_argument("labels", nargs="*")
        parser_label.set_defaults(func=self.on_label)

        parser_pin = self.subparsers.add_parser("/pin")
        parser_pin.set_defaults(func=self.on_pin)

        parser_archive = self.subparsers.add_parser("/archive")
        parser_archive.set_defaults(func=self.on_archive)

        parser_unarchive = self.subparsers.add_parser("/unarchive")
        parser_unarchive.set_defaults(func=self.on_unarchive)

        parser_insight = self.subparsers.add_parser("/insight")
        parser_insight.set_defaults(func=self.on_insight)

        parser_merge = self.subparsers.add_parser("/merge")
        parser_merge.set_defaults(func=self.on_merge)

        parser_close = self.subparsers.add_parser("/close")
        parser_close.add_argument("issue_comment", nargs="?")
        parser_close.set_defaults(func=self.on_close)

        parser_reopen = self.subparsers.add_parser("/reopen")
        parser_reopen.set_defaults(func=self.on_reopen)

        # TODO 这里实际上拿到的信息是 @_user_1，需要检查是不是当前机器人
        parser_at_bot = self.subparsers.add_parser("at_user_1")
        parser_at_bot.add_argument("command", nargs="*")
        parser_at_bot.set_defaults(func=self.on_at_bot)

    def _get_topic_by_args(self, *args):
        # 新增一个判断是不是在issue/pr/repo的话题中
        chat_type, topic = "", ""
        try:
            raw_message = args[3]
            chat_type = raw_message["event"]["message"].get("chat_type", "")
            if "p2p" != chat_type:
                # 判断 pr/issue/repo?
                root_id = raw_message["event"]["message"].get(
                    "root_id", raw_message["event"]["message"]["message_id"]
                )

                if root_id:
                    repo, issue, pr = tasks.get_git_object_by_message_id(root_id)
                    if repo:
                        topic = TopicType.REPO
                    elif issue:
                        topic = TopicType.ISSUE
                    elif pr:
                        topic = TopicType.PULL_REQUEST
        except Exception as e:
            logging.error(e)
        return chat_type, topic

    def on_welcome(self, *args, **kwargs):
        logging.info("on_welcome %r", args)
        tasks.send_welcome_message.delay(*args, **kwargs)

    def on_comment(self, text, *args, **kwargs):
        logging.info("on_comment %r", text)
        _, topic = self._get_topic_by_args(*args)
        if topic == TopicType.ISSUE:
            tasks.create_issue_comment.delay(*args, **kwargs)
        elif topic == TopicType.PULL_REQUEST:
            tasks.create_pull_request_comment.delay(*args, **kwargs)

    def on_help(self, param, unkown, *args, **kwargs):
        logging.info("on_help %r %r", vars(param), unkown)
        chat_type, topic = self._get_topic_by_args(*args)
        if "p2p" == chat_type:
            tasks.send_manage_manual.delay(*args, **kwargs)
        else:
            if TopicType.REPO == topic:
                tasks.send_repo_manual.delay(*args, **kwargs)
            elif TopicType.ISSUE == topic:
                tasks.send_issue_manual.delay(*args, **kwargs)
            elif TopicType.PULL_REQUEST == topic:
                tasks.send_pull_request_manual.delay(*args, **kwargs)
            else:
                tasks.send_chat_manual.delay(*args, **kwargs)
        return "help", param, unkown

    def on_match(self, param, unkown, *args, **kwargs):
        logging.info("on_match %r %r", vars(param), unkown)
        if not param.repo_url and not param.chat_name:
            logging.error("return")
            tasks.send_manage_fail_message.delay(
                "repo_url and chat_name is empty",
                *args,
                **kwargs,
            )
        else:
            tasks.create_chat_group_for_repo.delay(
                param.repo_url,
                param.chat_name,
                *args,
                **kwargs,
            )
        return "match", param, unkown

    def on_issue(self, param, unkown, *args, **kwargs):
        logging.info("on_issue %r %r", vars(param), unkown)
        # /issue [title] [@user_1] [@user_2] [[label_1],[label2]]
        try:
            raw_message = args[3]
            chat_type = raw_message["event"]["message"]["chat_type"]
            mentions = {
                m["key"].replace("@_user", "at_user"): m
                for m in raw_message["event"]["message"].get("mentions", [])
            }
            # 只有群聊才是指定的repo
            if "group" == chat_type:
                title, users, labels = [], [], []
                for arg in param.argv:
                    if not "\n" in arg:
                        if not "at_user" in arg and len(users) == 0:
                            title.append(arg)
                        elif "at_user" in arg:
                            users.append(
                                mentions[arg]["id"]["open_id"]
                                if arg in mentions
                                else ""
                            )
                        else:
                            labels = arg.split(",")
                # 支持title中间有空格
                title = " ".join(title)
                users = [open_id for open_id in users if open_id]
                tasks.create_issue.delay(title, users, labels, *args, **kwargs)
        except Exception as e:
            logging.error(e)
        return "issue", param, unkown

    def on_review(self, param, unkown, *args, **kwargs):
        logging.info("on_review %r %r", vars(param), unkown)
        # /review [@user_1] [@user_2]
        try:
            raw_message = args[3]
            chat_type = raw_message.get("event", {}).get("message", {}).get("chat_type")
            mentions = {
                m["key"].replace("@_user", "at_user"): m
                for m in raw_message.get("event", {})
                .get("message", {})
                .get("mentions", [])
            }
            # 只有群聊才是指定的repo
            if "p2p" != chat_type:
                users = []
                for user in param.users:
                    if "at_user" in user and user in mentions:
                        users.append(mentions[user]["id"]["open_id"])
                    elif "ou_" == user[:3]:
                        users.append(user)
                chat_type, topic = self._get_topic_by_args(*args)
                if TopicType.PULL_REQUEST == topic:
                    tasks.change_pull_request_reviewer.delay(users, *args, **kwargs)
        except Exception as e:
            logging.error(e)
        return "review", param, unkown

    def on_assign(self, param, unkown, *args, **kwargs):
        logging.info("on_assign %r %r", vars(param), unkown)
        # /assign [@user_1] [@user_2]
        try:
            raw_message = args[3]
            chat_type = raw_message.get("event", {}).get("message", {}).get("chat_type")
            mentions = {
                m["key"].replace("@_user", "at_user"): m
                for m in raw_message.get("event", {})
                .get("message", {})
                .get("mentions", [])
            }
            # 只有群聊才是指定的repo
            if "p2p" != chat_type:
                users = []
                for user in param.users:
                    if "at_user" in user and user in mentions:
                        users.append(mentions[user]["id"]["open_id"])
                    elif "ou_" == user[:3]:
                        users.append(user)
                chat_type, topic = self._get_topic_by_args(*args)
                if TopicType.ISSUE == topic:
                    tasks.change_issue_assignees.delay(users, *args, **kwargs)
                elif TopicType.PULL_REQUEST == topic:
                    tasks.change_pull_request_assignees.delay(users, *args, **kwargs)
        except Exception as e:
            logging.error(e)
        return "assign", param, unkown

    def on_new(self, param, unkown, *args, **kwargs):
        logging.info("on_new %r %r", vars(param), unkown)
        chat_type, _ = self._get_topic_by_args(*args)
        if "p2p" == chat_type:
            tasks.send_manage_new_message.delay(*args, **kwargs)
        return "new", param, unkown

    def on_view(self, param, unkown, *args, **kwargs):
        logging.info("on_view %r %r", vars(param), unkown)
        chat_type, topic = self._get_topic_by_args(*args)
        if "p2p" == chat_type:
            tasks.send_manage_view_message.delay(*args, **kwargs)
        else:
            if TopicType.REPO == topic:
                tasks.send_repo_view_message.delay(*args, **kwargs)
            elif TopicType.ISSUE == topic:
                tasks.send_issue_view_message.delay(*args, **kwargs)
            elif TopicType.PULL_REQUEST == topic:
                tasks.send_pull_request_view_message.delay(*args, **kwargs)
            else:
                tasks.send_chat_view_message.delay(*args, **kwargs)

        return "view", param, unkown

    def on_log(self, param, unkown, *args, **kwargs):
        logging.info("on_log %r %r", vars(param), unkown)
        _, topic = self._get_topic_by_args(*args)
        if TopicType.PULL_REQUEST == topic:
            tasks.send_pull_request_log_message.delay(*args, **kwargs)
        return "log", param, unkown

    def on_diff(self, param, unkown, *args, **kwargs):
        logging.info("on_log %r %r", vars(param), unkown)
        _, topic = self._get_topic_by_args(*args)
        if TopicType.PULL_REQUEST == topic:
            tasks.send_pull_request_diff_message.delay(*args, **kwargs)
        return "log", param, unkown

    def on_setting(self, param, unkown, *args, **kwargs):
        logging.info("on_setting %r %r", vars(param), unkown)
        chat_type, _ = self._get_topic_by_args(*args)
        if "p2p" == chat_type:
            tasks.send_manage_setting_message.delay(*args, **kwargs)
        return "setting", param, unkown

    def on_visit(self, param, unkown, *args, **kwargs):
        logging.info("on_visit %r %r", vars(param), unkown)
        if not param.visibility:
            logging.error("return")
            tasks.send_repo_failed_tip.delay(
                "visibility is empty",
                *args,
                **kwargs,
            )
        else:
            tasks.change_repo_visit.delay(
                param.visibility,
                *args,
                **kwargs,
            )
        return "visit", param, unkown

    def on_access(self, param, unkown, *args, **kwargs):
        logging.info("on_access %r %r", vars(param), unkown)
        try:
            raw_message = args[3]
            chat_type = raw_message["event"]["message"]["chat_type"]
            mentions = {
                m["key"].replace("@_user", "at_user"): m
                for m in raw_message["event"]["message"].get("mentions", [])
            }
            # 只有群聊才是指定的repo
            if "group" == chat_type:
                if param.person in mentions:
                    openid = mentions[param.person]["id"]["open_id"]
                    _, topic = self._get_topic_by_args(*args)
                    if TopicType.REPO == topic:
                        tasks.change_repo_collaborator.delay(
                            param.permission, openid, *args, **kwargs
                        )
        except Exception as e:
            logging.error(e)
        return "access", param, unkown

    def on_rename(self, param, unkown, *args, **kwargs):
        logging.info("on_rename %r %r", vars(param), unkown)
        title = " ".join(param.title)
        chat_type, topic = self._get_topic_by_args(*args)
        if TopicType.REPO == topic:
            tasks.change_repo_name.delay(title, *args, **kwargs)
        elif TopicType.ISSUE == topic:
            tasks.change_issue_title.delay(title, *args, **kwargs)
        elif TopicType.PULL_REQUEST == topic:
            tasks.change_pull_request_title.delay(title, *args, **kwargs)
        return "rename", param, unkown

    def on_edit(self, param, unkown, *args, **kwargs):
        logging.info("on_edit %r %r", vars(param), unkown)
        desc = " ".join(param.desc)
        # 移除第一个换行字符
        if len(desc) > 0 and "\n" == desc[0]:
            desc = desc[1:]
        chat_type, topic = self._get_topic_by_args(*args)
        if TopicType.REPO == topic:
            tasks.change_repo_desc.delay(desc, *args, **kwargs)
        elif TopicType.ISSUE == topic:
            tasks.change_issue_desc.delay(desc, *args, **kwargs)
        elif TopicType.PULL_REQUEST == topic:
            tasks.change_pull_request_desc.delay(desc, *args, **kwargs)
        return "edit", param, unkown

    def on_link(self, param, unkown, *args, **kwargs):
        logging.info("on_link %r %r", vars(param), unkown)
        if not param.homepage:
            logging.error("return")
            tasks.send_repo_failed_tip.delay(
                "homepage is empty",
                *args,
                **kwargs,
            )
        else:
            tasks.change_repo_link.delay(
                param.homepage,
                *args,
                **kwargs,
            )
        return "link", param, unkown

    def on_label(self, param, unkown, *args, **kwargs):
        logging.info("on_label %r %r", vars(param), unkown)
        # process_repo_action.delay(*args, **kwargs)
        # 支持空格分隔label也支持逗号分隔
        labels = []
        for label in param.labels:
            labels = labels + label.split(",")
        chat_type, topic = self._get_topic_by_args(*args)
        if TopicType.REPO == topic:
            tasks.change_repo_label.delay(labels, *args, **kwargs)
        elif TopicType.ISSUE == topic:
            tasks.change_issue_label.delay(labels, *args, **kwargs)
        elif TopicType.PULL_REQUEST == topic:
            tasks.change_pull_request_label.delay(labels, *args, **kwargs)
        return "label", param, unkown

    def on_archive(self, param, unkown, *args, **kwargs):
        logging.info("on_archive %r %r", vars(param), unkown)
        _, topic = self._get_topic_by_args(*args)
        if TopicType.REPO == topic:
            tasks.change_repo_archive.delay(True, *args, **kwargs)
        return "archive", param, unkown

    def on_pin(self, param, unkown, *args, **kwargs):
        logging.info("on_pin %r %r", vars(param), unkown)
        _, topic = self._get_topic_by_args(*args)
        if TopicType.ISSUE == topic:
            tasks.pin_issue.delay(*args, **kwargs)
        return "archive", param, unkown

    def on_unarchive(self, param, unkown, *args, **kwargs):
        logging.info("on_unarchive %r %r", vars(param), unkown)
        _, topic = self._get_topic_by_args(*args)
        if TopicType.REPO == topic:
            tasks.change_repo_archive.delay(False, *args, **kwargs)
        return "unarchive", param, unkown

    def on_insight(self, param, unkown, *args, **kwargs):
        logging.info("on_insight %r %r", vars(param), unkown)
        chat_type, topic = self._get_topic_by_args(*args)
        if "p2p" == chat_type:
            pass
        else:
            if TopicType.REPO == topic:
                tasks.send_repo_insight_message.delay(*args, **kwargs)
            elif TopicType.ISSUE == topic:
                pass
            elif TopicType.PULL_REQUEST == topic:
                pass
            else:
                tasks.send_chat_insight_message.delay(*args, **kwargs)
        return "insight", param, unkown

    def on_merge(self, param, unkown, *args, **kwargs):
        logging.info("on_merge %r %r", vars(param), unkown)
        _, topic = self._get_topic_by_args(*args)
        if TopicType.PULL_REQUEST == topic:
            tasks.merge_pull_request.delay(*args, **kwargs)
        return "merge", param, unkown

    def on_close(self, param, unkown, *args, **kwargs):
        logging.info("on_close %r %r", vars(param), unkown)
        _, topic = self._get_topic_by_args(*args)
        if TopicType.ISSUE == topic:
            if TopicType.ISSUE == topic:
                if param.issue_comment:
                    # 过滤 comment 中的 /close
                    args[2]["text"] = param.issue_comment
                    # 链式任务, 先创建 issue comment，再关闭 issue
                    tasks.chain(
                        tasks.create_issue_comment.si(*args, **kwargs)
                        | tasks.close_issue.si(*args, **kwargs)
                    ).delay()
                else:
                    # 如果没有 issue comment，直接关闭 issue
                    tasks.close_issue.delay(*args, **kwargs)
        elif TopicType.PULL_REQUEST == topic:
            tasks.close_pull_request.delay(*args, **kwargs)
        return "close", param, unkown

    def on_reopen(self, param, unkown, *args, **kwargs):
        logging.info("on_reopen %r %r", vars(param), unkown)
        _, topic = self._get_topic_by_args(*args)
        if TopicType.ISSUE == topic:
            tasks.reopen_issue.delay(*args, **kwargs)
        elif TopicType.PULL_REQUEST == topic:
            tasks.reopen_pull_request.delay(*args, **kwargs)
        return "reopen", param, unkown

    def on_at_bot(self, param, unkown, *args, **kwargs):
        logging.info("on_at_user_1 %r %r", vars(param), unkown)

        raw_message = args[3]
        user_id = raw_message["event"]["message"]["mentions"][0]["id"]["user_id"]
        user_key = raw_message["event"]["message"]["mentions"][0]["key"]
        logging.info(f"user_id: {user_id}")
        logging.info(f"user_key: {user_key}")
        # command = param.command
        content = args[2].split(" ", 1)

        # 判断机器人
        if user_key == "@_user_1" and user_id is None:
            command = content[1] if len(content) > 1 else None
            # 判断@bot 后续命令合法即执行
            if command:
                self.parse_args(command, *args, **kwargs)
            return self.on_help(param, unkown, *args, **kwargs)

        return "on_at_bot", param, unkown

    def parse_args(self, command, *args, **kwargs):
        try:
            # edit可能是多行的，第一行可能没有空格
            if "/edit" == command[:5]:
                command = "/edit " + command[5:]
            argv = [a.replace("@_user", "at_user") for a in command.split(" ") if a]
            param, unkown = self.parser.parse_known_args(argv)
            return param.func(param, unkown, *args, **kwargs)
        except Exception as e:
            logging.debug("error %r", e)
            raise e

    def parse_multiple_commands(self, commands, *args, **kwargs):
        results = []
        commands = commands.replace("\n", "").lstrip()

        for command in commands.split(";"):
            # 判断命令是否合法
            if command not in self.command_list:
                tasks.send_manage_fail_message.delay(
                    f"{command} 指令不存在！", *args, **kwargs
                )
                continue

            result = self.parse_args(command, *args, **kwargs)
            results.extend(result)
        return results


if __name__ == "__main__":
    from pprint import pprint

    commands = [
        "/help",
        "/man",
        "/match",
        "/match repo_url",
        "/match repo_url chat_name",
        "/new",
        "/view",
        "/setting",
        "/visit public",
        "/visit private",
        "/visit internal",
        "/access read @xxx",
        "/access triage @xxx",
        "/access write @xxx",
        "/access maintain @xxx",
        "/access admin @xxx",
        "/rename new_name",
        "/rename new name",
        "/edit new_name",
        "/link homepage",
        "/label label1",
        "/archive",
        "/unarchive",
        "/insight",
        "/close",
        "/reopen",
        "/issue",
        "/issue test_title",
        "/issue test title @_user_1",
        "/issue test title @_user_1 @_user_2",
        "/issue test title @_user_1 label1",
        "/issue test title @_user_1 label1,label2",
        "/issue @_user_1",
        "/issue @_user_1 label1,label2",
        "unkown input",
    ]
    parser = GitMayaLarkParser()

    for command in commands:
        result = parser.parse_args(command)
        pprint((command, result))
