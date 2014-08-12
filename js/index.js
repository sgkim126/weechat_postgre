var appendLogList,
    newLogDiv,
    newLogList;

newLogDiv = function (time, nick, message) {
  var messageDiv,
      nickDiv,
      timeDiv;
  nickDiv = $('<div>').addClass('col-xs-1').addClass('text-center').text(nick);
  timeDiv = $('<div>').addClass('col-xs-3').text(time);
  messageDiv = $('<div>').addClass('col-xs-8').text(message);
  return $('<div>').addClass('row').append(nickDiv).append(messageDiv).append(timeDiv);
}
newLogList = function (id, command, time, nick, message) {
  return $('<li>').attr('id', 'wlv-log-' + id).addClass('wlv-cmd-' + command).append(
    newLogDiv(time, nick, message));
}
appendLogList = function(id, command, time, nick, message) {
      $('#wlv-log-list').append(newLogList(id, command, time, nick, message));
}
