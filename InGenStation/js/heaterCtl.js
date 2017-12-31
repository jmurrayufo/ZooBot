

function heaterState( newState ) {
  
  var xhttp = new XMLHttpRequest();
  
  if (newState == 'on') {
    xhttp.open("POST", "/heater/on", true);
  } else if (newState == 'off') {
    xhttp.open("POST", "/heater/off", true);
  } else if (newState == 'disable') {
    xhttp.open("POST", "/heater/disable", true);
  }

  xhttp.send();
  
}

function getHeaterSettings() {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            var data = JSON.parse(xmlHttp.responseText)
            for (x in data) {
                element = document.getElementById(x);
                if (element != null) {
                    element.value = data[x];
                }
            }
        }
    }
    xmlHttp.open("GET", "/heater/settings", true); // true for asynchronous 
    xmlHttp.send(null);
}

function setHeaterSettings( button ){
    var formData = new FormData();
    for (x in button.parentElement.elements) {
        if (button.parentElement.elements[x].id != null && button.parentElement.elements[x].id != '') {
            formData.append(
                button.parentElement.elements[x].id,
                button.parentElement.elements[x].value);
        }
    }
    var request = new XMLHttpRequest();
    request.open("POST", "/heater/settings");
    request.send(formData);
}