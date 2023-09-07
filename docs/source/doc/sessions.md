# Sessions

A session is the main object ab-online manipulates.

A session is described in a json files. This file describes how many machines to launch and the Activity Browser configuration :
- projects to create
- databases to import in projects
- plugins to activate in projects

## File format

Exemple:

```json
{
    "name": "example",
    "password": "azerty",
    "machines": 1,
    "ab_channel": "conda-forge",
    "ab_version": "2.9.0",
    "databases": [
        {   
            "name"      : "Biosphere",
            "filename"  : "biosphere3.bw2package",
            "location"  : "local"
        },
        {   
            "name"      : "Idemat",
            "filename"  : "Idemat.bw2package",
            "location"  : "local"
        }
    ],
    "plugins": [
        {   
            "name"      : "notebook",
            "ab_channel": "pan6ora",
            "version"   : "0.2.4"
        }
    ],
    "projects": [
        { 
            "name" : "example",
            "databases" : [
                "Biosphere",
                "Idemat"
            ],
            "plugins"   : [
                "notebook"
            ]
        },
        { 
            "name" : "second project",
            "databases" : [
                "Biosphere"
            ],
            "plugins"   : []
        }
    ]
}

For the complete description of sessions file see the json schema in **code reference**.
```