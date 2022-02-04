let demo_button = document.getElementById('run-demo')

async function runDemo() {
    let credentials = {
        x_app_id : document.getElementById("x-app-id").value,
        x_app_key : document.getElementById("x-app-key").value,
    }
    var center = {
        lat: 38.8982919,
        lng: -77.0273156
    }
    let query = `?ll=${center.lat},${center.lng}&distance=${'5km'}&limit=50`
    let response = await fetch('https://trackapi.nutritionix.com/v2/locations'+query,{
        headers: new Headers({
            'x-app-id' : document.getElementById("x-app-id").value,
            'x-app-key' : document.getElementById("x-app-key").value,
            contentType: 'application/json'
        }),
        method: 'GET',
    })
    restaurant_results = response.json()
    console.log(restaurant_results);
}

demo_button.onclick = function(e) {
    runDemo()
}