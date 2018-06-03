import env
import run
import os
import sys

VOLUME_PATH = "/deploy/" + env.project_name + "_" + env.env
def copy_project_into_volume():
    import docker
    client = docker.from_env()
    container = client.containers.run('alpine/git',
            "-c 'mkdir -p %(output_path)s  && git archive --format=tar %(branch)s | tar -x -C  %(output_path)s &&\
                    cp -r docker/env/%(env)s/* %(output_path)s/'"%{ 'output_path': VOLUME_PATH + "_new",
                        'env': env.env, 'branch': os.environ.get('BRANCH', env.env)},
            volumes = {
                'nginx-deploy': {
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

ADD_DEPLOY_CONFIG = ' -f docker-compose.yml.deploy '
def call_docker_compose_deploy(command):
    return os.system(env.docker_compose(ADD_DEPLOY_CONFIG + command))

def deploy(args = []):
    run.init_volumes()
    copy_project_into_volume()
    if 0 != call_docker_compose_deploy(env.run(["cd %(output_path)s_new && %(prepare)s"\
            %{'prepare': (run.COMMAND_DEPENDENCES + ' && ' + run.COMMAND_PREPARE), 'output_path': VOLUME_PATH}])):
        return
    call_docker_compose_deploy(env.down())
    if 0 != call_docker_compose_deploy(env.run(["cd .. && mv %(output_path)s %(output_path)s_old &&\
            rm -rf %(output_path)s_old && mv %(output_path)s_new %(output_path)s"\
            %{'output_path': VOLUME_PATH}])):
        return
    if 0 != call_docker_compose_deploy(env.run([run.COMMAND_DB_MIGRATE])):
        return
    call_docker_compose_deploy(env.up())

_actions = {}
if env.env == 'staging' or env.env == 'production':
    _actions = {
        'rails:deploy': {
            'desc': """Deploy into docker as Server.
                                  Before use it:
                                  * Put config file into docker/env/${ENV}/
                                  * create ${ENV} branch in git.""",
            'action': deploy
        }
    }

