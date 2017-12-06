import sanic
# from sanic.response import text, html
from sanic.exceptions import NotFound, ServerError, RequestTimeout,\
                             InvalidUsage
import logging

class SanicMgr:
    from sanic.config import Config
    Config.KEEP_ALIVE = False
    app =  sanic.Sanic(__name__, log_config=None)
    def __init__(self, args):
        # Not sure how to just pull this from __main__....
        global log
        if args.purpose == 'dragon':
            log = logging.getLogger('DragonHab')

        elif  args.purpose == 'bug':
            log = logging.getLogger('BugHab')

        elif  args.purpose == 'test':
            log = logging.getLogger('DevHab')


    @app.route("/test", methods=["GET","POST",])
    def test(request):
        log.info(f"Got request {request} on endpoint '/test'")
        if request.method == 'GET':
            ret_val = sanic.response.json(request.args)
        elif request.method == 'POST':
            ret_val = sanic.response.json(request.form)

        # ret_val = sanic.response.text("Test complete !")
        return ret_val


    @app.route("/")
    def test(request):
        log.info(f"Got request {request} on endpoint '/'")
        html = """<p>Welcome to the ZooBot station!</p>"""
        ret_val =  sanic.response.html(html)
        return ret_val


    @app.route("/menu", methods=["GET","POST",])
    def post_test(request):

        html = f"""<p>This is a test</p></p>
        <form action="test" method="get">
          First name: <input type="text" name="fname"><br>
          Last name: <input type="text" name="lname"><br>
          <button type="submit">Submit</button>
          <button type="submit" formmethod="post">Submit using POST</button>
        </form>"""
        ret_val =  sanic.response.html(html)
        return ret_val


    @app.listener('before_server_start')
    async def setup_db(app, loop):
        log.info("Server Startup")
        log.info(f"Running sanic {sanic.__version__}")


    @app.listener('after_server_start')
    async def notify_server_started(app, loop):
        log.info("Server Startup Completed")


    @app.listener('before_server_stop')
    async def notify_server_stopping(app, loop):
        log.info("Server Shutdown")


    @app.listener('after_server_stop')
    async def close_db(app, loop):
        log.info("Server Shutdown Completed")


    @app.middleware('request')
    async def print_on_request(request):
        log.info(f"{request.method} {request.url}")


    @app.middleware('response')
    async def print_on_response(request, response):
        log.info(f"{request.method} {request.url} {response.status}")


    @app.exception(NotFound)
    def handle_404(request, exception):
        log.error(f"File not found: {request.url}")
        ret_val =  sanic.response.text(f"Woops! I couldn't find {request.url}", status=exception.status_code)
        log.info(f"{exception.status_code} {request.url} {ret_val.status}")
        return ret_val    


    @app.exception(ServerError)
    def handle_error(request, exception):
        log.error(f"Server Error on: {request.url}")
        ret_val =  sanic.response.text(f"Woops! I couldn't find {request.url}", status=exception.status_code)
        log.info(f"{exception.status_code} {request.url} {ret_val.status}")
        return ret_val


    @app.exception(RequestTimeout)
    def handle_timeout(request, exception):
        log.error(f"Request timed out! Oh well?")
        log.error(exception)
        log.error(dir(exception))
        log.error(exception.args)
        log.error(exception.status_code)
        log.error(exception.with_traceback)
        return sanic.response.text("OK!")


    @app.exception(InvalidUsage)
    def handle_usage(request, exception):
        log.debug(exception.status_code)
        ret_val = sanic.response.text(f"Method {request.method} not allowed on URL {request.path}", status=exception.status_code)
        log.exception(ret_val)
        return ret_val
