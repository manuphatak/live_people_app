var CONNECTION = {
  OPENED: 'live',
  CONNECTING: 'connecting',
  CLOSED: 'closed',
};

new Vue({
  el: '#app',
  data: {
    notify: {},
    people: [],
    newPerson: {},
    connection: CONNECTION.CONNECTING,
  },
  init: function() {
    this.ws = new AppSocket();
  },
  ready: function() {
    this.ws.onopen = this._handleSocketOpen;
    this.ws.onmessage = this._handleSocketMessage;
    this.ws.onreconnectstart = this._handleSocketReconnectStart;
    this.ws.onclose = this._handleSocketClose;
    this.ws.onerror = this._handleSocketError;
    this.ws.open();
  },
  methods: {
    createPerson: function() {
      this.sendPersonAction(null, 'create', this.newPerson);
      this.newPerson = {};
    },
    _createPerson: function(person) {
      console.log("creating person", person);
      this.people.push(person);
    },
    updatePerson: function(person) {
      this.sendPersonAction(person.pk, 'update', person.fields);
      this.toggleEdit(person, false)
    },
    _updatePerson: function(person) {
      console.log("updating person", person);
      var index = this.people.findIndex(function(p) {return p.pk === person.pk;});
      this.people.$set(index, person);
    },
    cancelUpdate: function(person) {
      this.sendSyncAction(person.pk);
      this.toggleEdit(person, false);
    },
    deletePerson: function(person) {
      this.sendPersonAction(person.pk, 'delete');
    },
    _deletePerson: function(person) {
      console.log("deleting person", person);
      var target = this.people.find(function(p) {return p.pk === person.pk;});
      this.people.$remove(target);
    },
    toggleEdit: function(person, force) {
      var value = force === undefined ? !person.editing : force;
      Vue.set(person, 'editing', value);
    },
    setConnectionStatus: function(status) {
      this.$set('connection', status);
      if (status === CONNECTION.OPENED) this.sendSyncAction();
    },
    _setPeople: function(people) {
      console.log("syncing people", people);
      this.$set('people', people.map(function(person) {
        person.fields.created = new Date(person.fields.created);
        return person;
      }));
    },
    sendPersonAction: function(pk, action, data) {
      this.ws.send('Person', { pk: pk, action: action, data: data });
    },
    sendSyncAction: function(pk) {
      var payload = pk ? { pk: pk, action: 'details' } : { action: 'list' };
      this.ws.send('Sync', payload);
    },
    dismissNotification: function() {
      this.$set('notify', {});
    },
    _getPerson: function(payload) {
      const person = {
        pk: payload.pk,
        model: payload.model,
        fields: payload.data,
      };
      person.fields.created = new Date(person.fields.created);
      return person;
    },
    _handleSocketMessage: function(message) {
      switch (message.stream) {
        case 'Sync':
          return this._handleSyncAction(message.payload);
        case 'Person':
          return this._handlePersonAction(message.payload);
        case 'Notification':
          return this._handleNotificationAction(message.payload);
        default:
          return console.error('unknown stream=%s', message.stream);
      }
    },
    _handleSyncAction: function(payload) {
      switch (payload.action) {
        case 'list':
          return this._setPeople(payload.data);
        case 'details':
          return this._updatePerson(this._getPerson(payload));
        default:
          return console.error('unknown action=%s', payload.action);
      }
    },
    _handlePersonAction: function(payload) {
      switch (payload.action) {
        case 'create':
          return this._createPerson(this._getPerson(payload));
        case 'update':
          return this._updatePerson(this._getPerson(payload));
        case 'delete':
          return this._deletePerson(this._getPerson(payload));
        default:
          return console.error('unknown action=%s', payload.action);
      }
    },
    _handleNotificationAction: function(payload) {
      var self = this;
      self.$set('notify', {
        action: payload.action,
        html: payload.data.html,
        show: true,
      });
      setTimeout(self.dismissNotification, payload.data.timeout * 1000);

      return this.sendSyncAction();
    },
    _handleSocketOpen: function() {
      this.setConnectionStatus(CONNECTION.OPENED);
    },
    _handleSocketReconnectStart: function() {
      this.setConnectionStatus(CONNECTION.CONNECTING);
    },
    _handleSocketClose: function() {
      this.setConnectionStatus(CONNECTION.CLOSED);
    },
    _handleSocketError: function() {},
  },

});

function AppSocket() {
  const self = this;
  const scheme = window.location.protocol === 'https:' ? 'wss:' : 'ws:';

  self.path = scheme + '//' + window.location.host;
  self.ws = null;
  self.reconnectDelay = 1000;
  self._timeouts = [];

  self.open = open;
  self.close = close;
  self.send = send;

  self.onopen = noop;
  self.onmessage = noop;
  self.onreconnectstart = noop;
  self.onclose = noop;
  self.onerror = noop;

  return self;

  function open() {
    const ws = new WebSocket(self.path);

    ws.onopen = handleOpen;
    ws.onmessage = handleMessage;
    ws.onclose = handleClose;
    ws.onerror = handleError;
    self.ws = ws;
  }

  function close() {
    self._timeouts.forEach(function(id) {clearTimeout(id);})
  }

  function send(stream, payload) {
    self.ws.send(JSON.stringify(({ stream: stream, payload: payload })))
  }

  function handleOpen(event) {
    return self.onopen(event)
  }

  function handleMessage(event) {
    const message = JSON.parse(event.data);
    console.group('handling action=%s stream=%s', message.payload.action, message.stream);
    const results = self.onmessage(message);
    console.groupEnd();
    return results;
  }

  function handleClose(event) {
    self.ws = null;
    if (event.wasClean) {
      return self.onclose(event);
    }
    else {
      timeout(self.open);

      return self.onreconnectstart(event);
    }
  }

  function handleError(event) {
    return self.onerror(event)
  }

  function timeout(func) {
    self._timeouts.push(setTimeout(func.bind(self), self.reconnectDelay))
  }

  function noop() {}
}
