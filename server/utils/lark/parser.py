import argparse
import logging

import tasks


class GitMayaLarkParser(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser(exit_on_error=False)
        self.subparsers = self.parser.add_subparsers()
        self.init_subparsers()

    def init_subparsers(self):
        parser_help = self.subparsers.add_parser("/help")
        parser_help.set_defaults(func=self.on_help)
        parser_man = self.subparsers.add_parser("/man")
        parser_man.set_defaults(func=self.on_help)

        parser_match = self.subparsers.add_parser("/match", exit_on_error=False)
        parser_match.add_argument("repo_url", nargs="?")
        parser_match.add_argument("chat_name", nargs="?")
        parser_match.set_defaults(func=self.on_match)

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

    def on_help(self, param, unkown, *args, **kwargs):
        logging.info("on_help %r %r", vars(param), unkown)
        # TODO call task.delay
        tasks.send_manage_manual.delay(*args, **kwargs)
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

    def on_new(self, param, unkown, *args, **kwargs):
        logging.info("on_new %r %r", vars(param), unkown)
        return "new", param, unkown

    def on_view(self, param, unkown, *args, **kwargs):
        logging.info("on_view %r %r", vars(param), unkown)
        return "view", param, unkown

    def on_setting(self, param, unkown, *args, **kwargs):
        logging.info("on_setting %r %r", vars(param), unkown)
        return "setting", param, unkown

    def on_visit(self, param, unkown, *args, **kwargs):
        logging.info("on_visit %r %r", vars(param), unkown)
        return "visit", param, unkown

    def on_access(self, param, unkown, *args, **kwargs):
        logging.info("on_access %r %r", vars(param), unkown)
        return "access", param, unkown

    def on_rename(self, param, unkown, *args, **kwargs):
        logging.info("on_rename %r %r", vars(param), unkown)
        return "rename", param, unkown

    def on_edit(self, param, unkown, *args, **kwargs):
        logging.info("on_edit %r %r", vars(param), unkown)
        return "edit", param, unkown

    def on_link(self, param, unkown, *args, **kwargs):
        logging.info("on_link %r %r", vars(param), unkown)
        return "link", param, unkown

    def on_label(self, param, unkown, *args, **kwargs):
        logging.info("on_label %r %r", vars(param), unkown)
        return "label", param, unkown

    def on_archive(self, param, unkown, *args, **kwargs):
        logging.info("on_archive %r %r", vars(param), unkown)
        return "archive", param, unkown

    def on_unarchive(self, param, unkown, *args, **kwargs):
        logging.info("on_unarchive %r %r", vars(param), unkown)
        return "unarchive", param, unkown

    def on_insight(self, param, unkown, *args, **kwargs):
        logging.info("on_insight %r %r", vars(param), unkown)
        return "insight", param, unkown

    def on_close(self, param, unkown, *args, **kwargs):
        logging.info("on_close %r %r", vars(param), unkown)
        return "close", param, unkown

    def on_reopen(self, param, unkown, *args, **kwargs):
        logging.info("on_reopen %r %r", vars(param), unkown)
        return "reopen", param, unkown

    def parse_args(self, command, *args, **kwargs):
        try:
            # TODO
            command = command.replace("@_user_1", "")
            command = command.replace("@_user_2", "")
            argv = [a for a in command.split(" ") if a]
            param, unkown = self.parser.parse_known_args(argv)
            return param.func(param, unkown, *args, **kwargs)
        except Exception as e:
            logging.debug("error %r", e)


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
        "unkown input",
    ]
    parser = GitMayaLarkParser()

    for command in commands:
        result = parser.parse_args(command)
        pprint((command, result))
