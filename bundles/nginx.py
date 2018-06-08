import env
import os
import sys
import docker

nginx_image = 'nginx:1.13.12-alpine'
nginx_config = 'nginx-config'
server_name = env.project_name + '_' + env.env
def config(args = [], *, checkIfExist = True):
    write_path = os.path.join('site', server_name)
    if checkIfExist and os.path.isfile(write_path):
        answer = input('Config file \'%s\' already exist. Overwrite? (Y/N) [N]: '%write_path)
        if answer.lower() != 'y':
            return
    print('         Config Nginx')
    print()
    domain_name = input('Your domain-name(s), seperate by space(\' \'): ')
    print()
    print('         Nginx.conf')
    print('-'*80)
    config =(
"""upstream %(server_name)s_server {
  server %(server_name)s:3000;
}

server {
  server_name %(domain_names)s;
   location ~ ^/(assets)/  {
    root /deploy/%(server_name)s/public;
    gzip_static on;
    expires max;
    add_header Cache-Control public;
   }
   location / {
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Host $http_host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_pass http://%(server_name)s_server;
   }
}"""%{'server_name': server_name,
      'domain_names': domain_name})
    print(config)
    print('-'*80)
    try:
        os.makedirs('site')
    except:
        pass
    f = open(write_path, 'w')
    f.write(config)
    f.flush()
    f.close()
    print('Write to ' + os.path.realpath(write_path))

name = 'nginx-deploy'
def nginx_up(args = []):
    client = docker.from_env()
    try:
        client.networks.get(name)
        print('[NETWORK]          %s up-to-date'%name)
    except:
        client.networks.create(name)
        print('[NETWORK]          %s create'%name)
    try:
        container = client.containers.get(name)
        print('[NGINX]            %s up-to-date'%name)
    except:
        try:
            container = client.containers.run(nginx_image,
                        remove = True,
                        network = name,
                        volumes = {
                            name: {
                                'bind': '/deploy'
                            },
                            nginx_config: {
                                'bind': '/etc/nginx/conf.d/'
                            }
                        },
                        ports =  {'80/tcp': int(os.environ.get('PORT', '80'))},
                        command = 'nginx -t'
                    )
        except:
            print(sys.exc_info()[1].stderr.decode())
            print('x' * 100)
            print('     You may need command `nginx:remove [not-found-host]` to clean unused nginx config file ')
            print('x' * 100)
            return
        container = client.containers.run(nginx_image,
                name = name,
                network = name,
                volumes = {
                    name: {
                        'bind': '/deploy'
                    },
                    nginx_config: {
                        'bind': '/etc/nginx/conf.d/'
                    }
                },
                ports =  {'80/tcp': int(os.environ.get('PORT', '80'))},
                restart_policy = {'Name': 'always'},
                detach = True,
                command = 'sh -c "nginx -t && nginx -g \'daemon off;\'"'
            )
        print('[NGINX]            %s create'%name)
        print(container.logs().decode())

def nginx_down(args = []):
    client = docker.from_env()
    try:
        container = client.containers.get(name)
        container.stop()
        container.remove()
        print('[NGINX]            %s stoped'%name)
    except:
        print(sys.exc_info()[1])
    try:
        client.networks.get(name).remove()
        print('[NETWORK]          %s remove'%name)
    except:
        print(sys.exc_info()[1])

def nginx_clean(args = []):
    client = docker.from_env()
    for _name in [nginx_config, name]:
        try:
            client.volumes.get(_name).remove()
            print('[CONFIG]           %s remove'%_name)
        except:
            print(sys.exc_info()[1])

def nginx_add(args = []):
    if not os.path.isfile(os.path.join('site', server_name)):
        config(checkIfExist = False)
    if 0 != os.system('docker cp site/%(server_name)s %(name)s:/etc/nginx/conf.d/%(server_name)s.conf &&\
        docker exec %(name)s sh -c "(nginx -t && nginx -s reload) || rm -rf /etc/nginx/conf.d/%(server_name)s.conf"'%{'server_name': server_name, 'name': name}):
        print('x' * 100)
        print('     You may `nginx:up` first')
        print('x' * 100)

def nginx_remove(args = []):
    target = server_name
    if len(args) > 0:
        target = args[0]
    if 0 != os.system('docker exec %(name)s sh -c "rm /etc/nginx/conf.d/%(server_name)s.conf && nginx -s reload || exit 0"'%{'server_name': target, 'name': name}):
        client = docker.from_env()
        try:
            container = client.containers.run(nginx_image,
                    remove = True,
                    volumes = {
                        nginx_config: {
                            'bind': '/etc/nginx/conf.d/'
                        }
                    },
                    command = 'sh -c "rm /etc/nginx/conf.d/%(server_name)s.conf"'%{'server_name': target}
                )
            print(container.decode())
        except:
            print(sys.exc_info()[1])

#----------------------------------------------------------------------------

exports = {}
if env.env == 'staging' or env.env == 'production':
    exports = {
        'nginx:config': {
            'desc': 'Configure nginx',
            'action': config
        },
        'nginx:add': {
            'desc': 'Add this project to nginx',
            'action': nginx_add
        },
        'nginx:remove': {
            'desc': 'Remove [project (default this)] from nginx',
            'action': nginx_remove
        },
        'nginx:up': {
            'desc': 'Start Nginx server, -e PORT=? set port(default 80)',
            'action': nginx_up
        },
        'nginx:down': {
            'desc': 'Stop Nginx server',
            'action': nginx_down
        },
        'nginx:clean': {
            'desc': 'Clean Nginx config',
            'action': nginx_clean
        }
    }

                ports =  {'80/tcp': int(os.environ.get('PORT', '80'))},
                restart_policy = {'Name': 'always'},
                detach = True,
                command = 'sh -c "nginx -t && nginx -g \'daemon off;\'"'
            )
        print('[NGINX]            %s create'%name)
        print(container.logs().decode())

def nginx_down(args = []):
    client = docker.from_env()
    try:
        container = client.containers.get(name)
        container.stop()
        container.remove()
        print('[NGINX]            %s stoped'%name)
    except:
        print(sys.exc_info()[1])
    try:
        client.networks.get(name).remove()
        print('[NETWORK]          %s remove'%name)
    except:
        print(sys.exc_info()[1])

def nginx_clean(args = []):
    client = docker.from_env()
    for _name in ['nginx-config', name]:
        try:
            client.volumes.get(_name).remove()
            print('[CONFIG]           %s remove'%_name)
        except:
            print(sys.exc_info()[1])

def nginx_add(args = []):
    if not os.path.isfile(os.path.join('site', server_name)):
        config()
    os.system('docker cp site/%(server_name)s %(name)s:/etc/nginx/conf.d/%(server_name)s.conf &&\
        docker exec %(name)s sh -c "(nginx -t && nginx -s reload) || rm -rf /etc/nginx/conf.d/%(server_name)s.conf"'%{'server_name': server_name, 'name': name})

def nginx_remove(args = []):
    os.system('docker exec %(name)s sh -c "rm /etc/nginx/conf.d/%(server_name)s.conf && nginx -s reload"'%{'server_name': server_name, 'name': name})

#----------------------------------------------------------------------------

exports = {}
if env.env == 'staging' or env.env == 'production':
    exports = {
        'nginx:config': {
            'desc': 'Configure nginx',
            'action': config
        },
        'nginx:add': {
            'desc': 'Commit nginx.conf to nginx',
            'action': nginx_add
        },
        'nginx:remove': {
            'desc': 'Remove nginx.conf from nginx',
            'action': nginx_remove
        },
        'nginx:up': {
            'desc': 'Start Nginx server, -e PORT=? set port(default 80)',
            'action': nginx_up
        },
        'nginx:down': {
            'desc': 'Stop Nginx server',
            'action': nginx_down
        },
        'nginx:clean': {
            'desc': 'Clean Nginx config',
            'action': nginx_clean
        }
    }
