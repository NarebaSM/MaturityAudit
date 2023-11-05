function validaEmail() {
    var email = document.getElementById('email').value;
    var emailErr = document.getElementById('emailErr');
    var submitEmail = document.getElementById('submitEmail');

    const regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if(regexEmail.test(email)){
        emailErr.innerHTML = '';
        submitEmail.disabled = false;
    } else{
        emailErr.innerHTML = 'Formato de email invalido';
        submitEmail.disabled = true;
    }
}