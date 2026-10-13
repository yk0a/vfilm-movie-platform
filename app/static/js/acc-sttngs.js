function changeProfilePic(radio) {
    var selectedImg = radio.value;
    
    document.getElementById('user-pp').src = selectedImg;
}