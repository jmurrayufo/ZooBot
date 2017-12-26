function myFunction() {
  setTimeout(function(){
    console.log("I just log to console!");
    document.getElementById("demo").innerHTML = "Js works!";
  }, 1000)
}