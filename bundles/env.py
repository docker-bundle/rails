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
env = os.environ.get('ENV', 'development')
project_name = os.environ.get('PROJECT_NAME')

DOCKER_COMPOSE='docker-compose'
WINPTY = 'winpty'
if 0 == os.system('type %s > /dev/null 2>&1'%WINPTY):
    DOCKER_COMPOSE=WINPTY + ' ' + DOCKER_COMPOSE

def docker_compose(command):
    env_compose_file = ''
    name = project_name
    if env != '':
        name += '_' + env
        env_compose_file = '-f %s.%s'%(config_file_name, env)
    return "%s --project-name %s -f %s %s %s "%(DOCKER_COMPOSE, name, config_file_name, env_compose_file, command)

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
shell = lambda :('exec %s bash'%SERVICE_NAME)
_exec = lambda :('exec %s'%SERVICE_NAME)
logs  = lambda :('logs')

def run(args = [], *, run_args = ''):
    return ("run %s --rm %s sh -c '%s'"%(run_args, SERVICE_NAME, ' '.join(args)))

def action_run(args = []):
    return os.system(docker_compose(run(args)))

#--------------------------------------------------------------------------------------

_actions = {
    'env:init': {'desc': 'Initial Project Env Config','action': init},
    'run': {'desc': 'Run a command with a container', 'action': action_run},
    'exec': {'desc': 'Exec a command in container', 'action': action(docker_compose(_exec()))},
    'shell': {'desc': 'Open a Shell into container, if container not start, use `run bash`', 'action': action(docker_compose(shell()))},
    'logs': {'desc': 'Show logs', 'action': action(docker_compose(logs()))},
    'up': {'desc': 'Create && start server', 'action': action(docker_compose(up()))},
    'down': {'desc': 'Stop && remove  server', 'action': action(docker_compose(down()))},
    'start': {'desc': 'Start server', 'action': action(docker_compose(start()))},
    'stop': {'desc': 'Stop server', 'action': action(docker_compose(stop()))},
    'restart': {'desc': 'Restart server', 'action': action(docker_compose(stop()) + " && " + docker_compose(start()))}
}

