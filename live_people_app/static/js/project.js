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
    return self.onmessage(event)
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
$(function() {
  var ws = new AppSocket();
  ws.onopen = function(event) {
    console.log('onopen event', event);
  };
  ws.onclose = function(event) {
    console.log('onclose event', event);
  };
  ws.onerror = function(event) {
    console.log('onerror event', event);
  };
  ws.onmessage = function(event) {
    console.log('onmessage event', event);
  };
  ws.onreconnectstart = function(event) {
    console.log('onopen event', event);
  };
  ws.open();
});

