import env
import run
import os
import sys

VOLUME_PATH = "/deploy/" + env.project_name + "_" + env.env
def copy_project_into_volume():
    import docker
    client = docker.from_env()
    container = client.containers.run('alpine/git',
            "-c 'mkdir -p %(output_path)s  && git archive --format=tar %(env)s | tar -x -C  %(output_path)s &&\
                    cp -r docker/env/%(env)s/* %(output_path)s/'"%{ 'output_path': VOLUME_PATH + "_new",
                        'env': env.env, 'remote': env.get_env('REMOTE', 'origin')},
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

ADD_DEPLOY_CONFIG = '-f docker-compose.yml.deploy'

def run_deploy(command):
    return env.run([command], compose_args = ADD_DEPLOY_CONFIG)

def deploy(args = []):
    copy_project_into_volume()
    if 0 != run_deploy("cd %(output_path)s_new && %(prepare)s && cd .. && mv %(output_path)s %(output_path)s_old &&\
            rm -rf %(output_path)s_old && mv %(output_path)s_new %(output_path)s"\
            %{'prepare': (run.COMMAND_DEPENDENCES + ' && ' + run.COMMAND_PREPARE), 'output_path': VOLUME_PATH}):
        return
    env.down()
    if 0 != run_deploy(run.COMMAND_DB_MIGRATE):
        return
    env.docker_compose()(ADD_DEPLOY_CONFIG + ' up --build -d ' + env.SERVICE_NAME)

if env.env == 'staging' or env.env == 'production':
    actions = {
        'rails:deploy': {
            'desc': """Deploy into docker as Server.
                                  Before use it:
                                  * Put config file into docker/env/${ENV}/
                                  * create ${ENV} branch in git.""",
            'action': deploy
        }
    }
