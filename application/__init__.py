import os, re, sys

from flask import Flask
from router_config import MODULES


def create_app(name=__name__):
    app = Flask(name, static_path='/static')
    load_config(app)
    register_modules(app)
    return app


def load_config(app):
    app.config.from_object("config")


def register_modules(app):
    app_dir = os.path.abspath(__file__)
    sys.path.append(os.path.dirname(app_dir) + "/modules")

    for module in MODULES:
        module_router = "%s.router" % module["name"]
        register = False
        try:
            router = __import__(module_router, globals(), locals(), [], -1)
        except ImportError:
            print(module["name"] + " can not be loaded")
        else:
            url = None
            if "url" in module:
                url = module["url"]
            if app.config["DEBUG"]:
                print("[MODULE] Registered module router in %s to URL %s" % module_router, url)
            if url == "/":
                url = None
            register = True
        finally:
            load_module_dependencies(app, module)

        if register:
            app.register_module(router.module, url_prefix=url)


def load_module_dependencies(app, module):
    if 'models' in module and module['models'] == False:
        return

    name = module["name"]
    if app.config["DEBUG"]:
        print("[MODEL] loding model %s" % name)

    models = "%s.models" % name

    try:
        models = __import__(models, globals(), locals(), [], -1)
    except ImportError as ex:
        if re.match(r'No module named', ex.message):
            print('[MODEL] Unable to load the model for %s: %s' % (models, ex.message))
        else:
            print('[MODEL] Other(%s): %s' % (models, ex.message))
        return False
    return True