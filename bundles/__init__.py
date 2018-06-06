import env
import run
import deploy
import nginx

def include(*libs):
    actions = {}
    for lib in libs:
        actions.update(lib.exports)
    return actions


actions = include(env,
                  run,
                  deploy,
                  nginx)
