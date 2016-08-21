new Vue({
  el: '#app',
  data: {
    people: [],
    newPerson: {},
  },
  init: function() {
    this.ws = new AppSocket();
  },
  ready: function() {
    this.ws.onopen = this._handleSocketOpen;
    this.ws.onmessage = this._handleSocketMessage;
    this.ws.onreconnectstart = this._handleSocketReconnectstart;
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
      console.log("person", person);
      this.people.push(person);
    },
    deletePerson: function(person) {
      this.sendPersonAction(person.pk, 'delete');
    },
    toggleEdit: function(person, force) {
      var value = force === undefined ? !person.editing : force;
      Vue.set(person, 'editing', value);
    },
    _setPeople: function(people) {
      this.$set('people', people.map(function(person) {
        person.fields.created = new Date(person.fields.created);
        return person;
      }));
    },
    sendPersonAction: function(pk, action, data) {
      this.ws.send('Person', { pk: pk, action: action, data: data });
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
    _handleSyncAction: function(payload) {
      switch (payload.action) {
        case 'list':
          return this._setPeople(payload.data);
      }
    },
    _handlePersonAction: function(payload) {
      switch (payload.action) {
        case 'create':
          return this._createPerson(this._getPerson(payload));
      }
    },
    _handleSocketOpen: function() {
      this.ws.send('Sync', { action: 'list' })
    },
    _handleSocketMessage: function(message) {
      switch (message.stream) {
        case 'Sync':
          return this._handleSyncAction(message.payload);
        case 'Person':
          return this._handlePersonAction(message.payload);
      }
    },
    _handleSocketReconnectstart: function() {},
    _handleSocketClose: function() {},
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
// $(function() {
//   var ws = new AppSocket();
//   ws.onopen = function(event) {
//     console.log('onopen event', event);
//   };
//   ws.onclose = function(event) {
//     console.log('onclose event', event);
//   };
//   ws.onerror = function(event) {
//     console.log('onerror event', event);
//   };
//   ws.onmessage = function(event) {
//     console.log('onmessage event', event);
//   };
//   ws.onreconnectstart = function(event) {
//     console.log('onopen event', event);
//   };
//   ws.open();
// });
//
