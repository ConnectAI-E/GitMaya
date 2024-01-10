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

        parser_setting = self.subparsers.add_parser("/setting")
        parser_setting.set_defaults(func=self.on_setting)

        parser_visit = self.subparsers.add_parser("/visit")
        parser_visit.add_argument("visibility", nargs="?")
        parser_visit.set_defaults(func=self.on_visit)

        parser_access = self.subparsers.add_parser("/access")
        parser_access.add_argument("permission", nargs="?")
        parser_access.add_argument("person", nargs="?")
        parser_access.set_defaults(func=self.on_access)

        parser_rename = self.subparsers.add_parser("/rename")
        parser_rename.add_argument("name", nargs="?")
        parser_rename.set_defaults(func=self.on_rename)

        parser_edit = self.subparsers.add_parser("/edit")
        parser_edit.add_argument("name", nargs="?")
        parser_edit.set_defaults(func=self.on_edit)

        parser_link = self.subparsers.add_parser("/link")
        parser_link.add_argument("homepage", nargs="?")
        parser_link.set_defaults(func=self.on_link)

        parser_label = self.subparsers.add_parser("/label")
        parser_label.add_argument("name", nargs="?")
        parser_label.set_defaults(func=self.on_label)

        parser_archive = self.subparsers.add_parser("/archive")
        parser_archive.set_defaults(func=self.on_archive)

        parser_unarchive = self.subparsers.add_parser("/unarchive")
        parser_unarchive.set_defaults(func=self.on_unarchive)

        parser_insight = self.subparsers.add_parser("/insight")
        parser_insight.set_defaults(func=self.on_insight)

        parser_close = self.subparsers.add_parser("/close")
        parser_close.set_defaults(func=self.on_close)

        parser_reopen = self.subparsers.add_parser("/reopen")
        parser_reopen.set_defaults(func=self.on_reopen)

        # TODO 这里实际上拿到的信息是 @_user_1，需要检查是不是当前机器人
        parser_at_gitmaya = self.subparsers.add_parser("@GitMaya")
        parser_at_gitmaya.set_defaults(func=self.on_at_gitmaya)

    def _get_topic_by_args(self, *args):
        # 新增一个判断是不是在issue/pr/repo的话题中
        chat_type, topic = "", ""
        try:
            raw_message = args[3]
            chat_type = raw_message["event"]["message"]["chat_type"]
            if "group" == chat_type:
                # 判断 pr/issue/repo?
                root_id = raw_message["event"]["message"].get("root_id")
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
                    if not "at_user" in arg and len(users) == 0:
                        title.append(arg)
                    elif "at_user" in arg:
                        users.append(
                            mentions[arg]["id"]["open_id"] if arg in mentions else ""
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

    def on_new(self, param, unkown, *args, **kwargs):
        logging.info("on_new %r %r", vars(param), unkown)
        return "new", param, unkown

    def on_view(self, param, unkown, *args, **kwargs):
        logging.info("on_view %r %r", vars(param), unkown)
        try:
            raw_message = args[3]
            chat_type = raw_message["event"]["message"]["chat_type"]
            user_id = raw_message["event"]["sender"]["sender_id"]["open_id"]
            chat_id = raw_message["event"]["message"]["chat_id"]

            # chat/repo 发送repo主页
            if "p2p" == chat_type:
                tasks.open_user_url.delay(user_id)

            else:
                # 判断 pr/issue/repo
                root_id = raw_message["event"]["message"].get("root_id")
                if root_id:
                    repo, issue, pr = tasks.get_git_object_by_message_id(root_id)
                    if repo:
                        tasks.open_repo_url.delay(chat_id)
                    elif issue:
                        tasks.open_issue_url.delay(root_id)
                    elif pr:
                        tasks.open_pr_url.delay(root_id)
                    else:
                        tasks.open_repo_url.delay(chat_id)
                else:
                    tasks.open_repo_url.delay(chat_id)

        except Exception as e:
            logging.error(e)
        return "view", param, unkown

    def on_setting(self, param, unkown, *args, **kwargs):
        logging.info("on_setting %r %r", vars(param), unkown)
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
        return "access", param, unkown

    def on_rename(self, param, unkown, *args, **kwargs):
        logging.info("on_rename %r %r", vars(param), unkown)
        if not param.name:
            logging.error("return")
            tasks.send_repo_failed_tip.delay(
                "name is empty",
                *args,
                **kwargs,
            )
        else:
            tasks.change_repo_name.delay(
                param.name,
                *args,
                **kwargs,
            )
        return "rename", param, unkown

    def on_edit(self, param, unkown, *args, **kwargs):
        logging.info("on_edit %r %r", vars(param), unkown)
        if not param.desc:
            logging.error("return")
            tasks.send_repo_failed_tip.delay(
                "desc is empty",
                *args,
                **kwargs,
            )
        else:
            tasks.change_repo_desc.delay(
                param.desc,
                *args,
                **kwargs,
            )
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
        return "label", param, unkown

    def on_archive(self, param, unkown, *args, **kwargs):
        logging.info("on_archive %r %r", vars(param), unkown)
        return "archive", param, unkown

    def on_unarchive(self, param, unkown, *args, **kwargs):
        logging.info("on_unarchive %r %r", vars(param), unkown)
        return "unarchive", param, unkown

    def on_insight(self, param, unkown, *args, **kwargs):
        logging.info("on_insight %r %r", vars(param), unkown)
        try:
            raw_message = args[3]
            chat_id = raw_message["event"]["message"]["chat_id"]

            tasks.open_repo_insight.delay(chat_id)

        except Exception as e:
            logging.error(e)
        return "insight", param, unkown

    def on_close(self, param, unkown, *args, **kwargs):
        logging.info("on_close %r %r", vars(param), unkown)
        _, topic = self._get_topic_by_args(*args)
        if TopicType.ISSUE == topic:
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

    def on_at_gitmaya(self, param, unkown, *args, **kwargs):
        logging.info("on_at_gitmaya %r %r", vars(param), unkown)

        content = param.content.strip()

        # TODO @_user 得判断是否是机器人
        # if content.startswith("/"):
        #     # @GitMaya + /command，执行对应命令
        #     commands = content[1:]
        #     return self.parse_multiple_commands(commands, *args, **kwargs)

        # else:
        #     # @GitMaya + 空白内容，返回对应帮助卡片
        #     # TODO 发送话题对应manual卡片
        #     try:
        #         raw_message = args[3]
        #         chat_type = raw_message["event"]["message"]["chat_type"]
        #         thread_type = "repo"

        #         if "p2p" == chat_type:
        #             tasks.send_chat_manual.delay(*args, **kwargs)

        #         else:
        #             # TODO
        #             if "repo" == thread_type:
        #                 tasks.send_repo_manual.delay(*args, **kwargs)

        #     except Exception as e:
        #         logging.error(e)

        return "on_at_gitmaya", param, unkown

    def parse_args(self, command, *args, **kwargs):
        try:
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
