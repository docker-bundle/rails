import os

def load_env():
    try:
        for e in list(filter(lambda x:x!='', map(lambda x:x.strip(), open('.env').readlines()))):
            k,v = e.split('=')
            os.environ[k] = v
    except:
        pass

def input_default(text, default):
    value = input(text + ' [' + default + ']:')
    if value == '':
        value = default
    return value

def init(args = []):
    print()
    project_name = input_default("Please input your project name", os.path.basename(os.path.dirname(os.getcwd())))
    env_file = open('.env', 'w')
    env_file.write("PROJECT_NAME=%s"%project_name.replace(' ', '_').replace(':', '_'))
    env_file.flush()
    env_file.close()
    os.environ['PROJECT_NAME'] = project_name
    print()

#--------------------------------------------------------------------------------------

load_env()

if not os.environ.get('PROJECT_NAME'):
    init()

config_file_name = 'docker-compose.yml'
env = os.environ['ENV'] = os.environ.get('ENV', 'development')
project_name = os.environ.get('PROJECT_NAME')

DOCKER_COMPOSE='docker-compose'
WINPTY = 'winpty'
if 0 == os.system('type %s > /dev/null 2>&1'%WINPTY):
    DOCKER_COMPOSE=WINPTY + ' ' + DOCKER_COMPOSE


def docker_compose(command):
    return "%s --project-name %s -f %s %s "%(DOCKER_COMPOSE, project_name + '_' + env, config_file_name, command)

def docker_compose_env(command):
    env_compose_file = ' -f %s.%s '%(config_file_name, env)
    return docker_compose(env_compose_file + command)

def action(command):
    def _run(args = []):
        _command = command
        if len(args) > 0:
            _command += (' ' + ' '.join(args))
        return os.system(_command)
    return _run

SERVICE_NAME = 'app'

up = lambda :('up --build -d %s'%SERVICE_NAME)
down = lambda :('down --remove-orphans')
start = lambda :('start')
stop = lambda :('stop')
_exec = lambda :('exec %s'%SERVICE_NAME)
logs  = lambda :('logs')

def restart(args = []):
    arg_str = ''
    if len(args) > 0:
        arg_str = (' ' + ' '.join(args))
    return os.system(docker_compose_env(stop() + arg_str) + " && " + docker_compose_env(start() + arg_str))

def run(args = [], *, run_args = ''):
    return ("run %s --rm %s sh -c '%s'"%(run_args, SERVICE_NAME, ' '.join(args)))

def shell(args = []):
    arg_str = ' sh -c "bash || exit 0" '
    return 0 == os.system(docker_compose_env(_exec() + arg_str)) or \
            0 == os.system(docker_compose_env(run([arg_str])))

def action_run(args = []):
    return os.system(docker_compose_env(run(args)))

#--------------------------------------------------------------------------------------

exports = {
    'env:init': {'desc': 'Initial Project Env Config','action': init},
    'run': {'desc': 'Run a command with a container', 'action': action_run},
    'exec': {'desc': 'Exec a command in container', 'action': action(docker_compose_env(_exec()))},
    'shell': {'desc': 'Open a Shell into container, if container not start, use `run bash`', 'action': shell},
    'logs': {'desc': 'Show logs', 'action': action(docker_compose_env(logs()))},
    'up': {'desc': 'Create && start server', 'action': action(docker_compose_env(up()))},
    'down': {'desc': 'Stop && remove  server', 'action': action(docker_compose_env(down()))},
    'start': {'desc': 'Start server', 'action': action(docker_compose_env(start()))},
    'stop': {'desc': 'Stop server', 'action': action(docker_compose_env(stop()))},
    'restart': {'desc': 'Restart specify server, if not, restart all', 'action': restart},
    'ps': {'desc': 'Show containers', 'action': action(docker_compose_env('ps'))},
    'compose': {'desc': 'Use as docker-compose\n' + ' -'*50, 'action': action(docker_compose_env(''))},
}
