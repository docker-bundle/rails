import env

COMMAND_DEPENDENCES='yarn --ignore-engines && bundle'
COMMAND_DB_MIGRATE='rails db:create && rails db:migrate'
COMMAND_DB_SEED=COMMAND_DB_MIGRATE + ' && rails db:seed'
COMMAND_PREPARE='rails assets:precompile'

def prepare(args = []):
    env.run(['%s && %s'%(COMMAND_DEPENDENCES, COMMAND_PREPARE)], '--no-deps')

def migrate(args = []):
    env.run(['%s && %s'%(COMMAND_DEPENDENCES, COMMAND_DB_MIGRATE)])

def seed(args = []):
    env.run(['%s && %s'%(COMMAND_DEPENDENCES, COMMAND_DB_SEED)])

def rails_new(args = []):
    if 0 == env.run(['gem install rails && rails new . -d postgresql --webpack=vue']):
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
    env.run(['rails c'])

def rails_drop(args = []):
    env.run(['rails db:drop'])

def rails_publish(args = []):
    prepare()
    env.down()
    migrate()
    env.up()

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

actions = {
    'rails:new': {
        'desc': 'Create new rails project here in docker',
        'action': rails_new
    },
    'rails:sync': {
        'desc': 'Install depends, migrate db',
        'action': migrate
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
    actions.update(no_production_actions)

if env.env == 'staging' or env.env == 'production':
    actions.update(no_development_actions)
