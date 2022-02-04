console.log("hello world");
async function remove_favorite(element,dish_id) {
    // console.log("hello");
    // console.log(dish_id);
    let response = await fetch(`/user/remove_favorite/${dish_id}`)
    message = await response.json()
    console.log(message.message);
    let card = document.getElementById(dish_id)
    card.remove()
}