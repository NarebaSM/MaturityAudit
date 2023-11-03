function validaEmail() {
    var email = document.getElementById('email').value;
    var emailErr = document.getElementById('emailErr');
    var submitButton = document.getElementById('submitButton');

    const regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if(regexEmail.test(email)){
        emailErr.innerHTML = '';
        submitButton.disabled = false;
        checkPasswordMatch();
    } else{
        emailErr.innerHTML = 'Formato de email invalido';
        submitButton.disabled = true;
    }
}

function checkPasswordMatch() {
    var password = document.getElementById("password").value;
    var confirmPassword = document.getElementById("passwordConfirm").value;
    var matchDiv = document.getElementById("password-match");
    var submitButton = document.getElementById("submitButton");

    if (password !== confirmPassword) {
        matchDiv.innerHTML = "Passwords do not match";
        submitButton.disabled = true; // Desativa o botão de submit
    } else {
        matchDiv.innerHTML = "";
        submitButton.disabled = false; // Ativa o botão de submit
        validaEmail();
    }
}


function checkPasswordStrength() {
    var password = document.getElementById("password").value;
    var strengthDiv = document.getElementById("password-strength");

    // Adicione aqui lógica para verificar a força da senha
    // Você pode usar bibliotecas JavaScript ou implementar sua própria lógica.

    // Exemplo simples: verifica se a senha tem pelo menos 8 caracteres.
    if (password.length >= 8) {
        strengthDiv.innerHTML = "Password strength: Strong";
    } else {
        strengthDiv.innerHTML = "Password strength: Weak";
    }
}