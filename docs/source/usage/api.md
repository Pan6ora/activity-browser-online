# Using the API

The API is a set of commands a user can use to interact with ab-online.

For the complete list of available commands go to the [Code reference]() section.

This API can be used in two different ways.

## As a python library

AB Online can be used directly from a python script as a library:

```python
from ab_online import API

API.session.list()
```

This can be useful to do complex stuff or create a write an interface in Python.

## As a Web API

In an effort to make user able to create web interfaces without using a Python framework the API can also be accessed through web requests.

- start the local server with: `ab-online server`
- send requests on [https://localhost:5000/api/v1](https://localhost:5000/api/v1)

Ex:

Get the list of existing sessions with [https://localhost:5000/api/v1/sessions/list](https://localhost:5000/api/v1/sessions/list)


 