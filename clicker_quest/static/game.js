<!--
(function() {
  // I am writing JavaScript!  OH NO!
  var game_data;


  $('section').on('click', 'li', function(){
    if (this.class === 'building' || this.class === 'upgrade') {
      $.post(
        url: '/test/',
        data: {
          csrfmiddlewaretoken: getCookie('csrftoken'),
          this.attr('class'): true,
          name: this.attr('id'),
        },
        // TODO:  WRITE ACTUAL SUCCESS / UPDATE FUNCTION
        success: window.location.reload();
        // success: update_info(data);
      );
    };
  });

  // function update_info(data); {
  //
  // }


  $().ready(load);

  // var game_data
  function load() {
    $.get(
      url: '/test/',
      success: function(data) {
        game_data = data;
      },
      type: 'json',
    );

    setInterval(calc_data(game_data), 1000)
  }

  function calc_data(game_data) {
    for (var resource in game_data.resources) {
      if (game_data.resources.hasOwnProperty(resource)) {
        resource.owned += income;
        update_resource(resource)
      }
    }
  }

  function update_resource(resource) {
    $(resource + '_current').text(resource.owned);
  }


});
 -->
