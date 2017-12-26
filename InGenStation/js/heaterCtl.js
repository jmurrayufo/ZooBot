

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