# Zentry

A Zen version of Sentry.

Build by [Anton Pirker](https://github.com/antonpirker) during Sentry Hackweek 2024.

## Configure

The app excepts the following environment variables to be set:

- `SENTRY_API_AUTH_TOKEN`

    The User Auth Token that is used for connecting to the Sentry API. In Sentry.io click on your name in the top left corner and go to "User Settings" > "User Auth Tokens".

- `SENTRY_BACKEND_PROJECT_ID`

    The Sentry project ID of your backend.

- `SENTRY_BACKEND_ENVIRONMENT`

    The Sentry environment of your backend you want to monitor.

- `SENTRY_FRONTEND_PROJECT_ID`

    The Sentry project ID of your frontend.

- `SENTRY_FRONTEND_ENVIRONMENT`

    The Sentry environment of your backend you want to monitor.

- `SENTRY_DSN` (optional)  
    If you want to send error and performancne data of Zentry to Sentry give a DSN.


## Run

```bash
./run.sh
```

This will create a Python virtual environment, install all the requirements and run the app. 

Point your browser to: [http://localhost:5001](http://localhost:5001)
