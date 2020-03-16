import asyncio
import hdu_ics

from aiohttp import web

routes = web.RouteTableDef()

@routes.get('/ics')
async def hello(request):
    await asyncio.sleep(0.1)
    html = """
        <h1>Wlecome to use HDU Calender Generator</h1>
    """
    return web.Response(body='{}'.format(html), headers={'content-type': 'text/html'})

@routes.get('/ics/{account}/{password}')
async def entry(request):
    await asyncio.sleep(0.1)
    account = request.match_info['account']
    password = request.match_info['password']
    spider = hdu_ics.Schedule2ICS(account, password, 1)
    result = spider.run()
    return web.Response(body='{}'.format(result),
                        headers={'content-type': 'text/calendar',
                                 'content-disposition': "attachment; filename=\"{}.ics\"".format(account)
                                 }
                        )

app = web.Application()
app.add_routes(routes)
web.run_app(app, port=9898)