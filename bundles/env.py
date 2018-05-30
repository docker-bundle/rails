import os

def load_env():
    env_set = {}
    try:
        for e in list(filter(lambda x:x!='', map(lambda x:x.strip(), open('.env').readlines()))):
            k,v = e.split('=')
            env_set[k] = v
    except:
        pass
    return env_set

env_set = load_env()

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
    print()

def get_env(env_name, default = ''):
    if env_name in env_set:
        return env_set[env_name]
    if env_name in os.environ:
        return os.environ[env_name]
    return default

project_name = get_env('PROJECT_NAME')

if project_name == '':
    init()

#--------------------------------------------------------------------------------------

config_file_name = 'docker-compose.yml'
env = get_env('ENV', 'development')

DOCKER_COMPOSE='docker-compose'
WINPTY = 'winpty'
if 0 == os.system('type %s > /dev/null 2>&1'%WINPTY):
    DOCKER_COMPOSE=WINPTY + ' ' + DOCKER_COMPOSE

def docker_compose():
    env_compose_file = ''
    name = project_name
    if env != '':
        name += '_' + env
        env_compose_file = '-f %s.%s'%(config_file_name, env)
    def run(command):
        return os.system("%s --project-name %s -f %s %s %s"%(DOCKER_COMPOSE, name, config_file_name, env_compose_file, command))
    return run

def action(command):
    def _run(args = []):
        _command = command
        if len(args) > 0:
            _command += (' ' + ' '.join(args))
        return docker_compose()(_command)
    return _run

SERVICE_NAME = 'app'

up = action('up --build -d %s'%SERVICE_NAME)
down = action('down --remove-orphans')
start = action('start')
stop = action('stop')
def restart(args = []):
    stop()
    start()
def run(args = []):
    return docker_compose()("run --rm %s sh -c '%s'"%(SERVICE_NAME, ' '.join(args)))
shell = action('exec %s bash'%SERVICE_NAME)
_exec = action('exec %s'%SERVICE_NAME)
logs  = action('logs')

#--------------------------------------------------------------------------------------

actions = {
    'env:init': {'desc': 'Initial Project Env Config','action': init},
    'run': {'desc': 'Run a command with a container', 'action': run},
    'exec': {'desc': 'Exec a command in container', 'action': _exec},
    'shell': {'desc': 'Open a Shell into container, if container not start, use `run bash`', 'action': shell},
    'logs': {'desc': 'Show logs', 'action': logs},
    'up': {'desc': 'Create && start server', 'action': up},
    'down': {'desc': 'Stop && remove  server', 'action': down},
    'start': {'desc': 'Start server', 'action': start},
    'stop': {'desc': 'Stop server', 'action': stop},
    'restart': {'desc': 'Restart server', 'action': restart}
}
