# Decompetition Server

## Quickstart

Decompetition runs as a simple Python (Flask) server.  Make sure you have all
the dependencies, initialize your database, and run it:

```sh
pip3 install -r requirements.txt
./server.py --init-db
./server.py
```

If everything worked, you'll have a local Decompetition server listening on port
5000.  The first user you create will automatically become an admin.

This will create a SQLite DB file called `development.db`.  If you want to use a
PostgreSQL DB like the AWS environment does, stand one up locally and use the
"staging" config (or use it as an example and write your own config):

```sh
./server.py app/config/staging.json
```


## Development

All code for the webserver is in the `app` directory.  Most importantly:

- `app/__init__.py`  Startup code for the web server.
- `app/lib`          Python "library" code (SQLAlchemy models and other non-web-endpoint code).
- `app/web`          Handler code, forms, and Jinja templates for all the web endpoints.

There are also some supporting directories:

- `app/config`       Config files, used when starting the server.
- `app/static`       Static UI files (images, stylesheets, and JavaScript).
- `app/templates`    A few more Jinja templates, plus symlinks to the main templates.
- `app/tests`        Partial unit tests for the web server (`cd app && pytest`).


## Running on AWS

0.  Make sure you have Terraform and Ansible installed locally.

1.  `./deploy.sh init ENVNAME` \
    Create a new environment named `ENVNAME`.

2.  Edit the `inf/vars/ENVNAME/config.json` file to add your AWS credentials.
    If your challenges should always be available, delete the `start` and `stop`
    items from the JSON.

3.  `./deploy.sh provision ENVNAME` \
    Use Terraform to create the AWS infrastructure you need.  You can find your
    servers' IP addresses in the `inf/vars/ENVNAME/ssh_config` file afterwards.

4.  `./deploy.sh configure ENVNAME` \
    Use Ansible to configure your machines.  Your app will be accessible through
    the web server after this step.

5.  Create a user account in the web UI; the first user will automatically
    become an administrator.  Go to the challenge page and use the "Bulk Upload"
    link to add your challenges (challenges are `rsync`ed to the `/app` folder).

6.  Run a competition!

7.  `./deploy.sh teardown ENVNAME` \
    Destroy all your AWS infrastructure.

8.  `./deploy.sh delete ENVNAME` \
    Delete all local config files.


## Other Resources

- You can download Terraform here:\
  https://learn.hashicorp.com/tutorials/terraform/install-cli
- And you can download Ansible here:\
  https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html
- How to create / upload an AWS keypair:\
  https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html
- How to get your AWS access key and secret key:\
  https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html
