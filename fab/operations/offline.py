import os

from fabric.api import env, local
from fab.utils import generate_bower_command
from fab.const import (
    OFFLINE_STAGING_DIR,
    WHEELS_ZIP_NAME,
    BOWER_ZIP_NAME,
    NPM_ZIP_NAME,
)


def prepare_zipfiles():
    local(
        'git clone --depth 1 --recursive https://github.com/dimagi/commcare-hq.git {}/commcare-hq'
        .format(OFFLINE_STAGING_DIR)
    )

    # Let's create bower and npm zip files

    # Bower
    local('cd {}/commcare-hq && {}'.format(OFFLINE_STAGING_DIR, generate_bower_command('install', {
        'interactive': 'false',
    })))
    zip_folder(
        os.path.join(OFFLINE_STAGING_DIR, BOWER_ZIP_NAME),
        os.path.join(OFFLINE_STAGING_DIR, 'commcare-hq', 'bower_components')
    )

    # NPM
    local('cd {}/commcare-hq && npm install --production'.format(OFFLINE_STAGING_DIR))
    zip_folder(
        os.path.join(OFFLINE_STAGING_DIR, NPM_ZIP_NAME),
        os.path.join(OFFLINE_STAGING_DIR, 'commcare-hq', 'node_modules')
    )

    prepare_pip_wheels(os.path.join('requirements', 'requirements.txt'))
    prepare_pip_wheels(os.path.join('requirements', 'prod-requirements.txt'))
    zip_folder(
        os.path.join(OFFLINE_STAGING_DIR, WHEELS_ZIP_NAME),
        os.path.join(OFFLINE_STAGING_DIR, 'commcare-hq', 'wheelhouse')
    )


def zip_folder(destination, folder):
    local('tar -czf {} {}'.format(destination, folder))


def prepare_pip_wheels(requirements_file):
    local(
        'cd {}/commcare-hq && pip wheel --wheel-dir=wheelhouse -r {}'
        .format(OFFLINE_STAGING_DIR, requirements_file)
    )


def prepare_formplayer_build():
    jenkins_formplayer_build_url = 'https://jenkins.dimagi.com/job/formplayer/lastSuccessfulBuild/artifact/build/libs/formplayer.jar'

    local('wget -nv {} -O {}/formplayer.jar'.format(jenkins_formplayer_build_url, OFFLINE_STAGING_DIR))
