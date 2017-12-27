function temperatureHandler( temp ) {
  
  var xhttp = new XMLHttpRequest();
  
    xhttp.open("POST", "/test", true);
  	var formData = new FormData();
	formData.append('newTemp',temp);
  	xhttp.send(formData); 

  
}