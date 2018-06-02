import env
import run
import deploy

actions = {}
for _actions in [env._actions, run._actions, deploy._actions]:
    actions.update(_actions)

