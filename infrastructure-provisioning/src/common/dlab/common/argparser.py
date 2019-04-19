import argparse
import os
import platform

from awscli.help import WindowsHelpRenderer, PosixHelpRenderer
from botocore.docs.bcdoc.restdoc import ReSTDocument

from dlab.common import node
from dlab.common import constants


class CommandAction(argparse.Action):

    def __init__(self, option_strings, dest, command_table, **kwargs):
        self.command_table = command_table
        super(CommandAction, self).__init__(
            option_strings, dest, choices=self.choices, **kwargs
        )

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)

    @property
    def choices(self):
        return list(self.command_table)

    @choices.setter
    def choices(self, val):
        pass


def get_renderer():
    # TODO: move classes from awscli.help
    """
    Return the appropriate HelpRenderer implementation for the
    current platform.
    """
    if platform.system() == 'Windows':
        return WindowsHelpRenderer()
    else:
        return PosixHelpRenderer()


class HelpCommand(object):

    def __init__(self):
        self.renderer = get_renderer()
        self.doc = ReSTDocument(target='man')

    @staticmethod
    def _get_file(parsed_globals):
        doc_path_list = [
            os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__)
                )
            ),
            constants.HELP_FILES_FOLDER
        ]

        if hasattr(parsed_globals, constants.COMMAND_NAME):
            if parsed_globals.command != constants.HELP_KEY:
                doc_path_list.append(parsed_globals.command)

        if hasattr(parsed_globals, constants.SUB_COMMAND_NAME):
            doc_path_list.append(parsed_globals.subcommand)
        else:
            doc_path_list.append(constants.CONCEPTS)

        doc_path = os.path.join(*doc_path_list)

        doc_path = doc_path + constants.HELP_FILE_FORMAT
        if os.path.isfile(doc_path):
            return doc_path
        return None

    def __call__(self, args, parsed_globals):
        val = ""
        file_path = self._get_file(parsed_globals)
        if file_path:
            with open(file_path, 'r') as f:
                val = f.read()
        self.renderer.render(val)


class BaseArgumentParser(argparse.ArgumentParser):

    Formatter = argparse.RawTextHelpFormatter

    def __init__(self):
        settings = dict(
            usage=constants.USAGE,
            add_help=False,
            prog=constants.PROJECT_NAME,
            formatter_class=self.Formatter,
            conflict_handler='resolve',
        )
        super(BaseArgumentParser, self).__init__(**settings)
        self._build()

    def _build(self):
        raise NotImplementedError()

    def build_command_table(self):
        return [constants.HELP_KEY]

    @staticmethod
    def has_help(args):
        try:
            index = args.index(constants.HELP_KEY)
            if not index:
                return True
            return bool(args.pop(index))
        except ValueError:
            return False


class CommandAgrParser(BaseArgumentParser):
    command_table = []

    def _build(self):
        command_table = self.build_command_table()
        self.add_argument(
            constants.COMMAND_NAME,
            action=CommandAction,
            command_table=command_table
        )

    def build_command_table(self):
        table = super(CommandAgrParser, self).build_command_table()
        controller_key = 'dlab.services.aws.controllers'
        # TODO: generate controller_key
        nodes = node.registry.find_one(controller_key)
        if nodes:
            table += nodes.keys()
        return table


class SubCommandAgrParser(BaseArgumentParser):
    # TODO: add build sub_command_table
    sub_command_table = {
        'ssn': ['run', 'stop'],
        'edge': ['start', 'stop']
    }

    def __init__(self, command):
        self._command = command
        super(SubCommandAgrParser, self).__init__()

    def _build(self):
        sub_command_table = self.build_command_table()
        self.add_argument(
            constants.SUB_COMMAND_NAME,
            action=CommandAction,
            command_table=sub_command_table
        )

    def build_command_table(self):
        table = super(SubCommandAgrParser, self).build_command_table()
        return table + self.sub_command_table[self._command]
