let favorite = document.getElementById('favorite')
favorite.onsubmit = async function(e) {
    e.preventDefault()
    dish_id = window.location.pathname.split('/')[2]
    // console.log(dish_id);
    let form = new FormData(favorite)
    let response = await fetch(`http://localhost:5000/favorite/${dish_id}`,{method:'POST',body:form})
    if (response) {
        favorite.remove()
    } else {
        console.log("failed to favorite.");
    }
}