$("#phone_number").change(function () {  
    var thisObj = $(this).val();
    var phoneno = /^(\+\d{1,3}[- ]?)?\d{10}$/;
    const message = document.getElementById("phone_number");
    message.innerHTML = "";
    
    console.log("this obj",thisObj)
    
    if((thisObj.match(phoneno))){
      return true
    }
    else{
      try{
        throw "Not valid Mobile Number"
      }
      catch(err){
        console.log("errr" , err)
        message.innerHTML = err
      }
    }
  });