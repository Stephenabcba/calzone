
// let key = 'AIzaSyBrlaKmNtNUyggA1GleE_o8eC8BbGym-e8'
let xapp = '86b63d84'
let xid = '869750a3fb85d9b755712baf44ffcdf2'

// async function getZipCenter(link) {
//     let result = await fetch(link)
//     let location = await result.json()
//     // console.log(location.results[0]);
//     let center = {
//         lat: location.results[0].geometry.location.lat,
//         lng: location.results[0].geometry.location.lng
//     }
//     // console.log(center.lat);
//     return center
// }

// async function findRestaurants(center) {
//     let query = `?ll=${center.lat},${center.lng}&distance=${'5km'}&limit=50`
//     let response = await fetch('https://trackapi.nutritionix.com/v2/locations'+query,{
//         headers: new Headers({
//             'x-app-id' : xapp,
//             'x-app-key' : xid,
//             contentType: 'application/json'
//         }),
//         method: 'GET',
//     })
//     restaurant_results = await response.json()
//     console.log(restaurant_results);
// }


//  break in to 2 functions
searchForm.onsubmit = async function(e) {
    e.preventDefault()
    let zipSearchInput = document.getElementById('zip_search_input')
    let zipMap = document.getElementById('zipMap')
    let searchForm = document.getElementById('searchForm')
    // let zipCode = parseInt(zipSearchInput.value)
    // if (zipCode >= 10000 && zipCode <= 99999) {
        // function 1
        // zipMap.src=`https://www.google.com/maps/embed/v1/search?key=${key}&q=restaurant+in+zipcode+${zipCode}&zoom=12`

        let form = new FormData(searchForm)
        let center = await getLatLng(form)
        if (center) {
            let data = await getRestaurants(form,center)
            // console.log(data);
            if (data) {
                // console.log(data["locations"])
                if (data['locations'].length > 0) {
                    let menu = await getMenu(data)
                    let menu_to_print = []
                    if (data['calories'] < 0){
                        menu_to_print = menu
                    } else {
                        for (let menu_item of menu) {
                            // console.log(menu_item.nf_calories);
                            if (menu_item.nf_calories < data['calories'] && menu_item.nf_calories > data['calories']-200) {
                                console.log(menu_item);
                                menu_to_print.push(menu_item)
                            }
                        }
                    }
                    clearResults()
                    number = 1
                    for (let menu_item of menu_to_print) {
                        let dish = {
                            number: number,
                            restaurantName:menu_item.brand_name,
                            dishName:menu_item.food_name,
                            calories:menu_item.nf_calories,
                            dishId: menu_item.nix_item_id
                        }
                        addDish(dish)
                        number++
                    }
                    // let query = `?query=${data['locations'][0].name}&brand_ids=${data['locations'][0].brand_id}&common=false`
                    // let response = await fetch('https://trackapi.nutritionix.com/v2/search/instant'+query,{
                    //     headers: new Headers({
                    //         'x-app-id' : xapp,
                    //         'x-app-key' : xid,
                    //         // contentType: 'application/json'
                    //     }),
                    //     method: 'GET',
                    // })
                    // menu_results = await response.json()
                    // console.log(menu_results.branded);
                }
            }
        }

}

async function getLatLng(form) {
    let zipResponse = await fetch('http://localhost:5000/searchZip',{method:'POST',body:form})
    let data = await zipResponse.json()
    // console.log(data);
    let errorBox = document.getElementById('form_error')
    if (data.error) {
        for (let error_msg of data.error_msgs) {
            errorBox.innerHTML += `<p>Invalid Zipcode: ${error_msg}</p>`
        }
        return false
    }
    errorBox.innerHTML = ""
    zipMap.src = data.zip_map_src
    let center = {
        lat: data.results[0].geometry.location.lat,
        lng: data.results[0].geometry.location.lng
    }
    return center
}

async function getRestaurants(form, center) {
    form.append('lat',center.lat)
    form.append('lng',center.lng)
    let response = await fetch('http://localhost:5000/searchRestaurant',{method:'POST',body:form})
    let data = await response.json()
    let errorBox = document.getElementById('form_error')
    if (data.error) {
        console.log(data);
        for (let error_msg of data.error_msgs) {
            errorBox.innerHTML += `<p>Invalid Input: ${error_msg}</p>`
        }
        return false
    }
    errorBox.innerHTML = ""
    return data
}

async function getMenu(restaurantData) {
    let restaurantLocations = restaurantData['locations']
    let menu_items = []
    for (let restaurant of restaurantLocations) {
        let form = new FormData()
        form.append("name",restaurant.name)
        form.append("brand_id",restaurant.brand_id)
        let response = await fetch('http://localhost:5000/searchMenu',{method:'POST',body:form})
        let data = await response.json()
        // console.log(data.branded);
        for (let menu_item of data.branded) {
            // console.log(brand);
            menu_items.push(menu_item)
        }
        // console.log(menu_items);
    }
    return menu_items
}

function addDish(dish) {
    dishHTML = `<div class="border border-solid border-gray-200 rounded p-8 mb-4">
        <div class="flex justify-between">
            <div>
                <p class="text-lg"><a href="/show/${dish.dishId}" class="text-blue-500">Option ${dish.number}</a> ${dish.restaurantName}</p>
                <ul>
                    <li>${dish.dishName}</li>
                </ul>
            </div>
            <div>
                <p class="mb-3">Calories: ${dish.calories}</p>
                <a href="/comingsoon" class="px-5 py-3 bg-blue-500 text-white rounded">Order!</a>
            </div>
        </div>
    </div>`
    let dishes = document.getElementById('dishes')
    dishes.innerHTML += dishHTML
}

function clearResults() {
    let dishes = document.getElementById('dishes')
    dishes.innerHTML = ""
}