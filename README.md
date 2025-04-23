# HomeLab Database-as-a-Service (DBaas)

This project allows for the creation of a home Database as a Service for local development. 

My goal is to have an interface where I can quickly spin up some common databases on my Home Lab K3s cluster.

## Functionality

From a web application, users will customize their DB by:

1. Providing a name for their database, e.g. `myprojectDB`
2. Selecting their database application:
    - mongoDB
    - postgres
    - kafka
    - mySQL

Once this is done, the backend will process this request and create a deployment matching their spec.

It will then return on the web app the following information:

1. Credentials with pre-generated usernames and passwords:
    - admin creds e.g. `myprojectDB-postgres_admin`
    - read-only user creds e.g. `myprojectDB-postgres_ro`
2. A link to a Graphana dashboard which shows the status of their database.
