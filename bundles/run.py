import os
import env
import docker

COMMAND_DEPENDENCES='yarn --ignore-engines && bundler'
COMMAND_DB_MIGRATE='rails db:create && rails db:migrate'
COMMAND_DB_SEED=COMMAND_DB_MIGRATE + ' && rails db:seed'
COMMAND_PREPARE='rails assets:clean && rails assets:clobber && rails assets:precompile'
COMMAND_DROP = COMMAND_DEPENDENCES + '&& rails db:drop'

volumes = ['yarn', 'bundle']
def init_volumes():
    client = docker.from_env()
    for volume in volumes:
        volume = env.project_name + '_' + volume
        try:
            client.volumes.get(volume)
        except:
            client.volumes.create(volume)
            print('[VOLUME]     \'%s\' is created'%volume)
def clean_deps(args = []):
    client = docker.from_env()
    for volume in volumes + [env.env + '_node_modules']:
        volume = env.project_name + '_' + volume
        try:
            client.volumes.get(volume).remove()
            print('[VOLUME]     \'%s\' is removed'%volume)
        except:
            print('[VOLUME]     \'%s\' remove failed, not found or on use'%volume)

def prepare(args = []):
    os.system(env.docker_compose_env(env.run(['%s && %s'%(COMMAND_DEPENDENCES, COMMAND_PREPARE)], run_args = '--no-deps')))

def sync(args = []):
    if 0 != os.system(env.docker_compose_env(env.run(['%s && %s'%(COMMAND_DEPENDENCES, COMMAND_DB_MIGRATE)]))):
        config_info()

def migrate(args = []):
    os.system(env.docker_compose_env(env.run(['%s'%(COMMAND_DB_MIGRATE)])))

def seed(args = []):
    if 0 != os.system(env.docker_compose_env(env.run(['%s && %s'%(COMMAND_DEPENDENCES, COMMAND_DB_SEED)]))):
        config_info()

def rails_new(args = []):
    if 0 == os.system(env.docker_compose_env(env.run(['gem install rails && rails new . -d postgresql --webpack=vue']))):
        print('='*80)
        print("\n            INSTALL FINISH\n")
        config_info()
        show_hint()

def config_info():
    print()
    print("""You may need modify some config manually as default database connection config

Open `config/database.yml`:
---------------------------------------------------------------------------------------
default: &default
  ...

   +++
   username: postgres
   password:
   host: <%= ENV.fetch('DATABASE_HOSTNAME', '127.0.0.1') %>
   port: 5432
   +++

  ...
---------------------------------------------------------------------------------------
""")

def show_hint():
    print()
    print("""Watch file change in development env

Manually modify code into file

[Webpack-dev]

Open `config/webpacker.yml`:
---------------------------------------------------------------------------------------
development:
    ...
    dev_server:
        ...
        watch_options:
            ...

+            poll: process.env['DOCKER_ENV'] !== undefined

            ...
---------------------------------------------------------------------------------------

[Rails-dev]

Open `config/environments/development.rb`
---------------------------------------------------------------------------------------

- config.file_watcher = ActiveSupport::EventedFileUpdateChecker

+ config.file_watcher = ENV['DOCKER_ENV'].present? ? ActiveSupport::FileUpdateChecker : ActiveSupport::EventedFileUpdateChecker

---------------------------------------------------------------------------------------

[Rails-production] (optional)

Open `config/environments/production.rb`
---------------------------------------------------------------------------------------

  # Use a different cache store in production.
- # config.cache_store = :mem_cache_store
+ config.cache_store = :redis_store,  "#{ENV.fetch('REDIS_URL', 'redis://127.0.0.1:6379/')}/0/cache"

---------------------------------------------------------------------------------------

Open `Gemfile`
---------------------------------------------------------------------------------------
+++
gem 'redis'
gem 'redis-store'
gem 'redis-rails'
+++
---------------------------------------------------------------------------------------
run `rails:sync`

""")

def hint(args = []):
    config_info()
    show_hint()

def rails_c(args = []):
    os.system(env.docker_compose_env(env.run(['rails c'])))

def rails_drop(args = []):
    os.system(env.docker_compose_env(env.run([COMMAND_DROP])))

def rails_reset(args = []):
    os.system(env.docker_compose_env(env.run(['%s && %s'%(COMMAND_DROP, COMMAND_DB_SEED)])))

def rails_publish(args = []):
    prepare()
    os.system(env.docker_compose_env(env.down()))
    migrate()
    os.system(env.docker_compose_env(env.up()))

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
init_volumes()

exports = {
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
    },
    'rails:clean': {
        'desc': 'Clean depends',
        'action': clean_deps
    },
    'rails:hint': {
        'desc': 'Show hint',
        'action': hint
    },
}

no_production_actions = {
    'rails:drop': {
        'desc': 'Drop database (only available development/staging environments)',
        'action': rails_drop
    },
    'rails:reset': {
        'desc': 'Drop && seed (only available development/staging environments)',
        'action': rails_reset
    },
}

no_development_actions = {
    'rails:publish': {
        'desc': 'Compile assets and restart all servers (only available staging/production environments)',
        'action': rails_publish
    }
}

if env.env != 'production':
    exports.update(no_production_actions)

if env.env == 'staging' or env.env == 'production':
    exports.update(no_development_actions)
