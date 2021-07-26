// When the (fake?) file button is clicked...
var fileBtnDiv = document.getElementById("fileButtonDiv");
//var fileBtn = document.getElementById("fileButton")
var fileInput = document.getElementById("file")


// Putting the click on the div increases the clickable range
fileBtnDiv.addEventListener("click", function() { 
    fileInput.click();
});

fileInput.addEventListener("change", function() {
    // Not getting fileSpan or fileButton on load since they don't
    // need any events hooked into them, so it's a waste of resources
    // to do it at load time
    document.getElementById("fileSpan").innerText = fileInput.files[0].name;
});

function rotate(){
    document.getElementById("crest").classList.add('rotate');
}