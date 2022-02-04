jQuery(function ($) {
    function reset() {
      $('#error').html('').hide();
      $('#locations').html('');
      $('#foods').html('');
    }

    function runDemo() {
      var credentials = {
        'x-app-id':  $('#x-app-id').val(),
        'x-app-key': $('#x-app-key').val()
      };

      var center = {
        lat: 38.8982919,
        lng: -77.0273156
      };

      reset();

      $.ajax({
          url:         'https://trackapi.nutritionix.com/v2/locations',
          headers:     Object.assign({}, credentials),
          method:      'GET',
          contentType: 'application/json',
          data:        {
            ll:       center.lat + ',' + center.lng,
            distance: '5km',
            limit:    20
          }
        })
        .then(function (response) {
          var brand_ids = response.locations.map(
            function (location) {return location.brand_id}
          );

          console.log(response);

          $('#locations').JSONView(response, {collapsed: true});

          return $.ajax({
            url:         'https://trackapi.nutritionix.com/v2/search/instant',
            headers:     Object.assign({}, credentials),
            method:      'GET',
            contentType: 'application/json',
            data:        {
              query:     'salad',
              branded:   true,
              self:      false,
              common:    false,
              brand_ids: JSON.stringify(brand_ids)

            }
          })
        })
        .then(function (response) {
          console.log(response);

          $('#foods').JSONView(response, {collapsed: true});
        })
        .catch(function (response) {
          console.error(response);
          $('#error').show().JSONView(response.responseJSON);
        });
    }

    runDemo();

    $('#run-demo').click(runDemo);
  });