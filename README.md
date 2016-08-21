# live_people_app
Manage people with channel model bindings and vue.js

See it live!  https://live-people-app.herokuapp.com/

## Features

* 3 way model binding. All clients are in sync all the time.
* Uses Django Channels / model binding to push model changes.
* Uses `vue.js` for a lightweight interactive experience.

&nbsp;

* `vue.ModelForm` class providing vue integration with django's forms for validation and data cleaning.

  see [live_people_app/utils/vue.py](live_people_app/utils/vue.py)

* Management command that periodically resets the database and syncs & notifies connected clients of the update.

  see [live_people_app/people/management/commands/populate.py](live_people_app/people/management/commands/populate.py)

* (Technical Jargon:) Custom websocket reply channel consumer that allows individual clients to request information from the server via websocket.

  see [live_people_app/utils/consumers.py](live_people_app/utils/consumers.py#L76-L125)
  
* Custom Reconnecting WebSocket object

  see [live_people_app/static/js/project.js](live_people_app/static/js/project.js#L149-L221)
  
* Vue.js integration

  see [live_people_app/people/templates/people/home.html](live_people_app/people/templates/people/home.html)

* Not TOTALLY ugly (it is).  I like this live icon: 

  ![live](live.png)


## Up and Running

1. `git clone git@github.com:bionikspoon/live_people_app.git`
1. `cd live_people_app`
1. `mkvirtualenv -p python3 people`
1. `sudo bash ./utility/install_os_dependencies.sh install`           
1. `bash ./utility/install_python_dependencies.sh`  
1. `docker-compose up -d`
1. `chmod +x ./manage.py`
1. `./manage.py migrate`
1. `./manage.py runserver`
