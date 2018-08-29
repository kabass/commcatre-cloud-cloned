from __future__ import print_function
from __future__ import absolute_import

import jsonobject
from decimal import Decimal

import jinja2
import os
import re
import sys

import yaml

from commcare_cloud.commands.command_base import CommandBase, Argument


GitVersionProperty = jsonobject.StringProperty


class ChangelogEntry(jsonobject.JsonObject):
    _allow_dynamic_properties = False
    # filename is the only property that is populated from outside the yaml file
    filename = jsonobject.StringProperty()
    title = jsonobject.StringProperty()
    key = jsonobject.StringProperty()
    date = jsonobject.DateProperty()
    optional_per_env = jsonobject.BooleanProperty()
    min_commcare_version = GitVersionProperty()
    max_commcare_version = GitVersionProperty()
    context = jsonobject.StringProperty()
    details = jsonobject.StringProperty()
    update_steps = jsonobject.StringProperty()


def compile_changelog():
    # Parse the contents of the changelog dir
    changelog_contents = []
    files_to_ignore = ['0000-changelog.yml.example']
    changelog_dir = 'changelog'
    sorted_files = _sort_files(changelog_dir)
    for change_file_name in sorted_files:
        if change_file_name not in files_to_ignore:
            changelog_contents.append(load_changelog_entry(os.path.join(changelog_dir, change_file_name)))
    return changelog_contents


def load_changelog_entry(path):
    try:
        with open(path) as f:
            change_yaml = yaml.load(f)
            change_yaml['filename'] = re.sub(r'\.yml$', '.md', path.split('/')[-1])
            # yaml.load already parses dates, using this instead of ChangelogEntry.wrap
            return ChangelogEntry(**change_yaml)
    except Exception:
        print("Error parsing the file {}.".format(path), file=sys.stderr)
        raise


def _sort_files(directory):
    """
    Sorts filenames by descending alphanumeric order, userful for organizing the changelog index.md
    """
    def _natural_keys(text):
        retval = [int(c) if c.isdigit() else c for c in text[:4]]
        return retval
    unsorted_files = os.listdir(directory)
    unsorted_files.sort(key=_natural_keys, reverse=True)
    return unsorted_files


class MakeChangelogIndex(CommandBase):
    command = 'make-changelog-index'
    help = "Build the commcare-cloud CLI tool's changelog index"
    arguments = ()

    def run(self, args, unknown_args):
        j2 = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)), keep_trailing_newline=True)

        changelog_contents = compile_changelog()

        template = j2.get_template('changelog-index.md.j2')
        print(template.render(changelog_contents=changelog_contents).rstrip())


class MakeChangelog(CommandBase):
    command = 'make-changelog'
    help = "Build the commcare-cloud CLI tool's individual changelog files"
    arguments = (
        Argument(dest='changelog_yml', help="""Path to the yaml changelog file"""),
    )

    def run(self, args, unknown_args):
        changelog_yml = args.changelog_yml
        ordinal = int(Decimal(changelog_yml.split('/')[-1].split('-')[0]))
        j2 = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)), keep_trailing_newline=True)

        changelog_entry = load_changelog_entry(changelog_yml)
        template = j2.get_template('changelog.md.j2')

        print(template.render(changelog_entry=changelog_entry, ordinal=ordinal).rstrip())
