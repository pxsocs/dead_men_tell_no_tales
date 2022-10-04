# Start Flask Server
from application_factory import main

app = main()

if __name__ == '__main__':
    from waitress import serve
    # Production Server
    serve(app,
          host=app.settings['SERVER'].get('host'),
          port=app.settings['SERVER'].getint('port'))

    # Development Server -- Flask
    # app.run(debug=True,
    #         threaded=True,
    #         host=app.settings['SERVER'].get('host'),
    #         port=app.settings['SERVER'].getint('port'),
    #         use_reloader=False)
