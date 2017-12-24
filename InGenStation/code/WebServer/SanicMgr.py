import sanic
# from sanic.response import text, html
from sanic.exceptions import NotFound, ServerError, RequestTimeout,\
                             InvalidUsage
from sanic.views import CompositionView
import sanic_auth
import logging
import base64

from ..CustomLogging import Log
from ..Sql import SQL
from ..RoachHab import RoachHab

class SanicMgr:
    from sanic.config import Config
    Config.KEEP_ALIVE = False
    app = sanic.Sanic(__name__, log_config=None)
    log = Log()
    sql = SQL()


    def __init__(self, args):
        SanicMgr.log = Log(args)

        SanicMgr.log.debug("Booted with Manager")

        self.sql.connect()

        if args.purpose == 'dragon':
            # self.hab = RoachHab(args)
            raise NotImplementedError("Dragon hab is not yet implemented")
        elif  args.purpose == 'bug':
            self.hab = RoachHab(args)
        elif  args.purpose == 'test':
            self.hab = RoachHab(args)

        if  args.purpose in ['test', 'bug']:
            view = CompositionView()
            view.add(['GET'], self.hab.all_temperature_handler)
            SanicMgr.app.add_route(view, '/temp/')

            view = CompositionView()
            view.add(['GET'], self.hab.temperature_handler)
            SanicMgr.app.add_route(view, '/temp/<sensor_id>')

            view = CompositionView()
            view.add(['GET','PUT','POST','DELETE'], self.hab.heater_state)
            SanicMgr.app.add_route(view, '/heater/<state>')

            view = CompositionView()
            view.add(['GET'], self.hab.heater_state)
            SanicMgr.app.add_route(view, '/heater/')

            SanicMgr.app.static('/ui','./html/')
            SanicMgr.app.static('/js','./js/')

            SanicMgr.app.add_task(self.hab.run)
        SanicMgr.log.info(f"Finished boot as {args.purpose}")


    @app.route("/test", methods=["GET","POST",])
    async def test(request):
        if 'authorization' in request.headers:
            authString = base64.urlsafe_b64decode(request.headers['authorization'].split()[1]).decode()
            # authString = str(authString)
            username,password = authString.split(":")
            if username == 'john' and password == 'murray':
                return sanic.response.text(f"Authoed!\n{username}\n{password}")
        ret_val = sanic.response.json( {'message': 'Please Login!'},
                                        headers={'WWW-Authenticate': 'Basic realm="User Visible Realm"'},
                                        status=401 )

        # ret_val = sanic.response.text("Test complete !")
        return ret_val


    @app.route("/")
    async def test(request):
        html = """<p>Welcome to the ZooBot station!</p>"""
        ret_val =  sanic.response.html(html)
        return ret_val


    @app.route("/ui")
    async def ui_base(request):
        with open("html/index.html",'r') as fp:
            html = fp.read()
        return sanic.response.html(html)


    @app.route("/menu_sample", methods=["GET","POST",])
    async def get_post_menu_sample(request):

        html = f"""<p>This is a test</p></p>
        <form action="test" method="get">
          First name: <input type="text" name="fname"><br>
          Last name: <input type="text" name="lname"><br>
          <button type="submit">Submit</button>
          <button type="submit" formmethod="post">Submit using POST</button>
        </form>"""
        ret_val =  sanic.response.html(html)
        return ret_val


    @app.route("/menu", methods=["GET","POST",])
    async def get_post_menu(request):

        html = f"""<p>Main Menu</p></p>
        <form action="menu/sensors" method="get">
          <button type="submit" formmethod="get">Sensors</button>
        </form>"""
        ret_val =  sanic.response.html(html)
        return ret_val


    @app.route("/menu/sensors", methods=["GET","POST",])
    async def get_post_sensors(request):

        html = f"""<p>Sensors Menu</p></p>
        WIP!"""
        ret_val =  sanic.response.html(html)
        return ret_val


    @app.listener('before_server_start')
    async def before_server_start(app, loop):
        SanicMgr.log.info("Server Startup")
        SanicMgr.log.info(f"Running sanic {sanic.__version__}")


    @app.listener('after_server_start')
    async def after_server_start(app, loop):
        SanicMgr.log.info("Server Startup Completed")


    @app.listener('before_server_stop')
    async def before_server_stop(app, loop):
        SanicMgr.log.info("Server Shutdown")


    @app.listener('after_server_stop')
    async def after_server_stop(app, loop):
        SanicMgr.log.info("Server Shutdown Completed")


    ##################
    ### MIDDLEWARE ###
    ##################


    @app.middleware('request')
    async def print_on_request(request):
        SanicMgr.log.info(f"{request.method} {request.url}")
        if request.path.startswith("/control"):
            if 'authorization' in request.headers:
                authString = base64.urlsafe_b64decode(request.headers['authorization'].split()[1]).decode()
                # authString = str(authString)
                username,password = authString.split(":")
                if username == 'user' and password == 'password':
                    return
            ret_val = sanic.response.json( {'message': 'Please Login!'},
                                            headers={'WWW-Authenticate': 'Basic realm="User Visible Realm"'},
                                            status=401 )
            return ret_val
        else:
            SanicMgr.log.debug("No auth needed, continue!")


    @app.middleware('response')
    async def print_on_response(request, response):
        SanicMgr.log.info(f"{request.method} {request.url} {response.status}")


    ##################
    ### EXCEPTIONS ###
    ##################


    @app.exception(NotFound)
    async def handle_404(request, exception):
        SanicMgr.log.error(f"File not found: {request.url}")
        ret_val =  sanic.response.text(f"Woops! I couldn't find {request.url}", status=exception.status_code)
        SanicMgr.log.info(f"{exception.status_code} {request.url} {ret_val.status}")
        return ret_val    


    @app.exception(ServerError)
    async def handle_error(request, exception):
        SanicMgr.log.error(f"Server Error on: {request.url}")
        ret_val =  sanic.response.text(f"Woops! I couldn't find {request.url}", status=exception.status_code)
        SanicMgr.log.info(f"{exception.status_code} {request.url} {ret_val.status}")
        return ret_val


    @app.exception(RequestTimeout)
    async def handle_timeout(request, exception):
        SanicMgr.log.error(f"Request timed out! Oh well?")
        SanicMgr.log.error(exception)
        SanicMgr.log.error(dir(exception))
        SanicMgr.log.error(exception.args)
        SanicMgr.log.error(exception.status_code)
        SanicMgr.log.error(exception.with_traceback)
        return sanic.response.text("OK!")


    @app.exception(InvalidUsage)
    async def handle_usage(request, exception):
        SanicMgr.log.debug(exception.status_code)
        ret_val = sanic.response.text(f"Method {request.method} not allowed on URL {request.path}", status=exception.status_code)
        SanicMgr.log.exception(ret_val)
        return ret_val
