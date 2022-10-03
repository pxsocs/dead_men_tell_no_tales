# Start Flask Server
from application_factory import main

app = main(debug=True, reloader=True)

if __name__ == '__main__':
    import os
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

    # ------------------------------
    # Run after exiting Server
    # ------------------------------
    print("Exiting...")
    from backend.config import Config
    # clean debug.log
    try:
        os.remove(Config.debug_file)
    except Exception:
        pass

    # Stop Onion Server if running
    if app.settings['SERVER'].getboolean('onion_server'):
        from backend.tor import stop_hidden_services
        stop_hidden_services(app)