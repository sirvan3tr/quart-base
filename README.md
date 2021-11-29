# Flask Base API
**Documentation available at [http://hack4impact.github.io/flask-base](http://hack4impact.github.io/flask-base).**

## TODO
- Code climate and circle have been removed.
- Redis

### .env file
`.env` file should contain the following at the very least:
1. SECRET_KEY
2. QUART_APP
3. QUART_ENV
4. MAIL_SERVER
5. MAIL_PORT
6. EMAIL_SENDER
7. MAIL_USERNAME
8. MAIL_PASSWORD
9. DEV_DATABASE_URL
10. DATABASE_URL

### Email
We are using Sendgrid for the email service. Sendgrid is connected to the @innovationlab.uk email addresses which are hosted on AWS. System emails are sent from noreply@innovationlab.uk. All of these are managed from the Sendgrid and AWS platforms.

## Intalling postgresql
* On macos start postgresql brew services start postgresql
* If installed via brew on macos then need to run `/usr/local/opt/postgres/bin/createuser -s postgres`
* Create a database called `your-db-name`
* set `.env` line: `DEV_DATABASE_URL="postgresql:///your-db-name"`

## Setting up

##### Initialize a virtual environment
Unix/MacOS:
```
$ pipenv shell
$ pipenv install
```
Learn more in [the documentation](https://docs.python.org/3/library/venv.html#creating-virtual-environments).

##### (If you're on a Mac) Make sure xcode tools are installed

```
$ xcode-select --install
```

##### Add Environment Variables

You will need to add `QUART_APP=manage.py:app` and the `QUART_CONFIG=development`

Create a file called `.env` that contains environment variables. **Very important: do not include the `.env` file in any commits. This should remain private.** You will manually maintain this file locally, and keep it in sync on your host.

Variables declared in file have the following format: `ENVIRONMENT_VARIABLE=value`. You may also wrap values in double quotes like `ENVIRONMENT_VARIABLE="value with spaces"`.

1. In order for Flask to run, there must be a `SECRET_KEY` variable declared. Generating one is simple with Python 3:

   ```
   $ python3 -c "import secrets; print(secrets.token_hex(16))"
   ```

   This will give you a 32-character string. Copy this string and add it to your `.env`:

   ```
   SECRET_KEY=Generated_Random_String
   ```

2. The mailing environment variables can be set as the following.
   We recommend using [Sendgrid](https://sendgrid.com) for a mailing SMTP server, but anything else will work as well.

   ```
   MAIL_USERNAME=SendgridUsername
   MAIL_PASSWORD=SendgridPassword
   ```

Other useful variables include:

| Variable        | Default   | Discussion  |
| --------------- |-------------| -----|
| `ADMIN_EMAIL`   | `flask-base-admin@example.com` | email for your first admin account |
| `ADMIN_PASSWORD`| `password`                     | password for your first admin account |
| `DATABASE_URL`  | `data-dev.sqlite`              | Database URL. Can be Postgres, sqlite, etc. |
| `REDISTOGO_URL` | `http://localhost:6379`        | [Redis To Go](https://redistogo.com) URL or any redis server url |
| `RAYGUN_APIKEY` | `None`                         | API key for [Raygun](https://raygun.com/raygun-providers/python), a crash and performance monitoring service |
| `QUART_CONFIG`  | `default`                      | can be `development`, `production`, `default`, `heroku`, `unix`, or `testing`. Most of the time you will use `development` or `production`. |


##### Install the dependencies

```
$ pipenv install
```

##### Other dependencies for running locally

* **Sass:** `gem install sass`
* **Redis:** 
  * MAC: `brew install redis`
  * Linux: `sudo apt-get install redis-server`
* **PostgresQL**
  * MAC: `brew install postgresql`
  * Linux: `sudo apt-get install libpq-dev`


##### Create the database

```
$ python manage.py recreate_db
```

##### Other setup (e.g. creating roles in database)

```
$ python manage.py setup_dev
```

Note that this will create an admin user with email and password specified by the `ADMIN_EMAIL` and `ADMIN_PASSWORD` config variables. If not specified, they are both `flask-vuejs-admin@example.com` and `password` respectively.

##### [Optional] Add fake data to the database

```
$ python manage.py add_fake_data
```

## Running the app

```
$ source env/bin/activate
$ honcho start -e .env -f Local
```

For Windows users having issues with binding to a redis port locally, refer to [this issue](https://github.com/hack4impact/flask-base/issues/132).


## Gettin up and running with Docker

Currently we have a `Dockerfile` intended for testing purposes and it automates the whole cycle of running the application, setting up the database and redis.


##### How to use the docker file
In only three simple steps :
- change the variables `MAIL_USERNAME` , `MAIL_PASSWORD` and `SECRET_KEY`
- `docker build -t <image_name> .
- `docker run -it -d -p 5000:5000 --name <container name> <image_name> /bin/bash`
- To run in foreground mode `docker run -it -p 5000:5000 --name <container name> <image_name> /bin/bash`

##### Note

A more robust version with docker-compose is being developed to separate redis in separate container and allow the deployment of production-level applications automatically without the need of manual provisioning

## Formatting code

Before you submit changes to flask-base, you may want to autoformat your code with `python manage.py format`.


## Contributing

Contributions are welcome! Please refer to our [Code of Conduct](./CONDUCT.md) for more information.

## Documentation Changes

To make changes to the documentation refer to the [Mkdocs documentation](http://www.mkdocs.org/#installation) for setup.

To create a new documentation page, add a file to the `docs/` directory and edit `mkdocs.yml` to reference the file.

When the new files are merged into `master` and pushed to github. Run `mkdocs gh-deploy` to update the online documentation.
