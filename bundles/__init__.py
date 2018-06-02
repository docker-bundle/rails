import env
import run
import deploy
import nginx_conf

actions = {}
for _actions in [env._actions, run._actions, deploy._actions, nginx_conf._actions]:
    actions.update(_actions)

