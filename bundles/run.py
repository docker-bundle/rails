import os
import env

COMMAND_DEPENDENCES='yarn --ignore-engines && bundle'
COMMAND_DB_MIGRATE='rails db:create && rails db:migrate'
COMMAND_DB_SEED=COMMAND_DB_MIGRATE + ' && rails db:seed'
COMMAND_PREPARE='rails assets:precompile'

def init_volumes():
    import docker
    client = docker.from_env()
    volumes = ['yarn', 'node_modules', 'bundle']
    for volume in volumes:
        volume = env.project_name + '_' + volume
        try:
            client.volumes.get(volume)
            print('[VOLUME]     \'%s\' is up-to-date'%volume)
        except:
            client.volumes.create(volume)
            print('[VOLUME]     \'%s\' is created'%volume)

def prepare(args = []):
    init_volumes()
    os.system(env.docker_compose(env.run(['%s && %s'%(COMMAND_DEPENDENCES, COMMAND_PREPARE)], run_args = '--no-deps')))

def sync(args = []):
    init_volumes()
    os.system(env.docker_compose(env.run(['%s && %s'%(COMMAND_DEPENDENCES, COMMAND_DB_MIGRATE)])))

def migrate(args = []):
    init_volumes()
    os.system(env.docker_compose(env.run(['%s'%(COMMAND_DB_MIGRATE)])))

def seed(args = []):
    init_volumes()
    os.system(env.docker_compose(env.run(['%s && %s'%(COMMAND_DEPENDENCES, COMMAND_DB_SEED)])))

def rails_new(args = []):
    init_volumes()
    if 0 == os.system(env.docker_compose(env.run(['gem install rails && rails new . -d postgresql --webpack=vue']))):
        print(
"""
=============================================================================================
            INSTALL FINISH
=============================================================================================

Now you will add this config (inside '++++') manually by default database connection config

Open `config/database.yml`:
------------------------------------------------------------------------------
default: &default
  ...
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  username: postgres
  password:
  host: <%= ENV.fetch('DATABASE_HOSTNAME', '127.0.0.1') %>
  port: 5432
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  ...
------------------------------------------------------------------------------
""")

def rails_c(args = []):
    init_volumes()
    os.system(env.docker_compose(env.run(['rails c'])))

def rails_drop(args = []):
    init_volumes()
    os.system(env.docker_compose(env.run(['rails db:drop'])))

def rails_publish(args = []):
    init_volumes()
    prepare()
    os.system(env.docker_compose(env.down()))
    migrate()
    os.system(env.docker_compose(env.up()))

all_envs = ['development', 'staging', 'production']
if env.env not in all_envs:
    print("-"*100)
    print('[ERROR]          ENV must in [' + ','.join(all_envs) + ']')
    print("-"*100)
    exit()

print("-"*100)
print("                         Rails on Docker")
print("")
print("    ENV=%s               [development(default), staging, production]    ( -e ENV=?)"%(env.env))
print("-"*100)

_actions = {
    'rails:new': {
        'desc': 'Create new rails project here in docker',
        'action': rails_new
    },
    'rails:migrate': {
        'desc': 'Migrate db',
        'action': migrate
    },
    'rails:sync': {
        'desc': 'Install depends, migrate db',
        'action': sync
    },
    'rails:seed': {
        'desc': 'Install depends, migrate db and run seed',
        'action': seed
    },
    'rails:c': {
        'desc': 'Rails console',
        'action': rails_c
    },
    'rails:build': {
        'desc': 'Build static assets (for staging/production environments)',
        'action': prepare
    }
}

no_production_actions = {
    'rails:db:drop': {
        'desc': 'Drop database (only available development/staging environments)',
        'action': rails_drop
    }
}

no_development_actions = {
    'rails:publish': {
        'desc': 'Compile assets and restart all servers (only available staging/production environments)',
        'action': rails_publish
    }
}

if env.env != 'production':
    _actions.update(no_production_actions)

if env.env == 'staging' or env.env == 'production':
    _actions.update(no_development_actions)

