import env
import os
import sys

server_name = env.project_name + '_' + env.env
def conf(args = []):
    if len(args) == 0:
        print('Usage:')
        print('     nginx:config [domain1] [domain2] ...')
        return
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
      'domain_names': ' '.join(args)})
    print(config)
    print('-'*80)
    try:
        os.makedirs('site')
    except:
        pass
    write_path = os.path.join('site', server_name)
    f = open(write_path, 'w')
    f.write(config)
    f.flush()
    f.close()
    print('Write to ' + write_path)

name = 'nginx-deploy'
def nginx_up(args = []):
    import docker
    client = docker.from_env()
    try:
        network = client.networks.get(name)
        print('[NETWORK]          %s up-to-date'%name)
    except:
        client.networks.create(name)
        print('[NETWORK]          %s create'%name)
    try:
        container = client.containers.get(name)
        print('[NGINX]          %s up-to-date'%name)
    except:
        container = client.containers.run('nginx:1.13.12-alpine',
                name = name,
                network = name,
                volumes = {
                    name: {
                        'bind': '/deploy'
                    },
                    'nginx-config': {
                        'bind': '/etc/nginx/conf.d/'
                    }
                },
                ports =  {'80/tcp': 80},
                detach = True,
                remove = True
            )
        print('[NGINX]          %s create'%name)

def nginx_down(args = []):
    import docker
    client = docker.from_env()
    try:
        container = client.containers.get(name)
        container.stop()
        print('[NGINX]            %s stoped'%name)
    except:
        print(sys.exc_info()[1])
    try:
        network = client.networks.get(name)
        network.remove()
        print('[NETWORK]          %s remove'%name)
    except:
        print(sys.exc_info()[1])

def nginx_add(args = []):
    os.system('docker cp site/%(server_name)s %(name)s:/etc/nginx/conf.d//%(server_name)s.conf && docker exec %(name)s nginx -s reload'%{'server_name': server_name, 'name': name})

def nginx_remove(args = []):
    os.system('docker exec %(name)s sh -c "rm /etc/nginx/conf.d/%(server_name)s.conf && nginx -s reload"'%{'server_name': server_name, 'name': name})

#----------------------------------------------------------------------------

exports = {}
if env.env == 'staging' or env.env == 'production':
    exports = {
        'nginx:config': {
            'desc': 'Configure nginx',
            'action': conf
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
            'desc': 'Start Nginx server',
            'action': nginx_up
        },
        'nginx:down': {
            'desc': 'Stop Nginx server',
            'action': nginx_down
        }
    }
