import env
import run
import os
import sys

VOLUME_PATH = "/deploy/" + env.project_name + "_" + env.env
def copy_project_into_volume(copy_target):
    import docker
    client = docker.from_env()
    container = client.containers.run('alpine/git',
            "-c 'rm -rf %(output_path)s && mkdir -p %(output_path)s  && ((git archive --format=tar %(branch)s | tar -x -C  %(output_path)s) \
                    || for item in `ls -a | grep -vE \"^\..$|^\.$|docker|tmp|log|node_modules\"`; do cp -r $item %(output_path)s/$item; done) &&\
                    cp -r docker/env/%(env)s/* %(output_path)s/'"%{ 'output_path': VOLUME_PATH + "_new",
                        'env': env.env, 'branch': os.environ.get('BRANCH', 'HEAD')},
            volumes = {
                copy_target: {
                    'bind': '/deploy'
                },
                os.path.dirname(os.getcwd()): {
                    'bind': '/home/app'
                }
            },
            remove = True,
            working_dir = '/home/app',
            entrypoint='sh'
            )

def deploy(mode, onlyUp = False):
    ADD_DEPLOY_CONFIG = ' -f docker-compose.yml.deploy -f docker-compose.yml.%s '%mode
    def call_docker_compose_deploy(command):
        return os.system(env.docker_compose(ADD_DEPLOY_CONFIG + command))
    def call_docker_compose_deploy_new(command):
        return os.system('NEW=_new ' + env.docker_compose(ADD_DEPLOY_CONFIG + command))
    if not onlyUp:
        if 0 != call_docker_compose_deploy_new(env.run(["cd %(output_path)s_new && %(prepare)s"\
                %{'prepare': (run.COMMAND_DEPENDENCES + ' && ' + run.COMMAND_PREPARE), 'output_path': VOLUME_PATH}])):
            return
        call_docker_compose_deploy_new(env.down())
        if 0 != call_docker_compose_deploy_new(env.run(["cd .. &&\
                rm -rf %(output_path)s && mv %(output_path)s_new %(output_path)s"\
                %{'output_path': VOLUME_PATH}])):
            return
        if 0 != call_docker_compose_deploy(env.run(["cd .. &&\
                rm -rf %(output_path)s_new"\
                %{'output_path': VOLUME_PATH}])):
            return
        if 0 != call_docker_compose_deploy(env.run([run.COMMAND_DB_MIGRATE])):
            return
    call_docker_compose_deploy(env.up())

def show_deploy_path(path):
    print('='*80)
    print('     Deploy path: %s'%path)
    print('='*80)

def deploy_local(args = []):
    copy_project_into_volume(os.path.realpath('./deploy'))
    deploy(env.env, len(args) > 0 and args[0] == '--up')
    show_deploy_path(os.path.realpath('.' + VOLUME_PATH))

def deploy_nginx(args = []):
    copy_project_into_volume('nginx-deploy')
    deploy('nginx', len(args) > 0 and args[0] == '--up')
    show_deploy_path(VOLUME_PATH)

exports = {}
if env.env == 'staging' or env.env == 'production':
    exports = {
        'rails:deploy': {
            'desc': """Deploy into docker as Server.
                                  Before use it:
                                  * Put config file into docker/env/${ENV}/
                                  * -e BRANCH=<YOUR DEPLOY GIT BRANCH>
                                  * --up: only up server""",
            'action': deploy_local
        },
        'rails:deploy:nginx': {
            'desc': """Deploy into docker as Server, Serve by nginx in docker.
                                  Before use it:
                                  * Put config file into docker/env/${ENV}/
                                  * -e BRANCH=<YOUR DEPLOY GIT BRANCH>
                                  * --up: only up server""",
            'action': deploy_nginx
        }
    }



