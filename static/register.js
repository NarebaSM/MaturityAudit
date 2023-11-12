function validaEmail() {
    var email = document.getElementById('email').value;
    var emailErr = document.getElementById('emailErr');

    const regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if(regexEmail.test(email)){
        emailErr.innerHTML = '';
        return true;
    } else{
        emailErr.innerHTML = 'Formato de email invalido';
        return false;
    }
}

function validaCnpj(cnpj) {
    cnpj = cnpj.replace(/[^\d]/g, '');

    if (cnpj.length !== 14) {
        return false;
    }
    if (/^(\d)\1+$/.test(cnpj)) {
        return false;
    }

    let tamanho = cnpj.length - 2;
    let numeros = cnpj.substring(0, tamanho);
    let digitos = cnpj.substring(tamanho);
    let soma = 0;
    let pos = tamanho - 7;

    for (let i = tamanho; i >= 1; i--) {
        soma += numeros.charAt(tamanho - i) * pos--;
        if (pos < 2) {
            pos = 9;
        }
    }

    let resultado = soma % 11 < 2 ? 0 : 11 - (soma % 11);

    if (resultado !== parseInt(digitos.charAt(0), 10)) {
        return false;
    }

    tamanho = tamanho + 1;
    numeros = cnpj.substring(0, tamanho);
    soma = 0;
    pos = tamanho - 7;

    for (let i = tamanho; i >= 1; i--) {
        soma += numeros.charAt(tamanho - i) * pos--;
        if (pos < 2) {
            pos = 9;
        }
    }

    resultado = soma % 11 < 2 ? 0 : 11 - (soma % 11);

    if (resultado !== parseInt(digitos.charAt(1), 10)) {
        return false;
    }

    return true;
}

function checkCnpj() {
    var cnpjInput = document.getElementById("CNPJ").value;
    var cnpjDiv = document.getElementById("cnpjErr");

    var cnpj = cnpjInput.replace(/\D/g, '');

    var cnpjValido = validaCnpj(cnpj);

    if(!cnpjValido){
        cnpjDiv.innerHTML = "Formato Invalido para CNPJ";
        return false;
    }else{
        cnpjDiv.innerHTML = "";
        return true;
    }

}

function checkPasswordMatch() {
    var password = document.getElementById("password").value;
    var confirmPassword = document.getElementById("passwordConfirm").value;
    var matchDiv = document.getElementById("password-match");

    if (password !== confirmPassword) {
        matchDiv.innerHTML = "Passwords do not match";
        return false;
    } else {
        matchDiv.innerHTML = "";
        return true;
    }
}


function checkPasswordStrength() {
    var password = document.getElementById("password").value;
    var strengthDiv = document.getElementById("password-strength");

    var regex = /^(?=.*[A-Z])(?=.*[a-z])(?=.*[^A-Za-z0-9]).*$/;

    if(password.length >= 8 && regex.test(password)){
        strengthDiv.innerHTML = "password strength: Strong"
        strengthDiv.className = "Strong";
        return true;
    }else if (password.length >= 8) {
        strengthDiv.innerHTML = "Password strength: Medium";
        strengthDiv.className = "Medium";
        return false;
    } else {
        strengthDiv.innerHTML = "Password strength: Weak";
        strengthDiv.className = "Weak";
        return false;
    }
}

function submitValidation() {
    var submitButton = document.getElementById("submitButton");

    var emailCheck = validaEmail();
    var passCheck = checkPasswordMatch();
    var cnpjValid = checkCnpj();
    var passStrength = checkPasswordStrength();

    if(!emailCheck || !passCheck || !cnpjValid || !passStrength){
        submitButton.disabled = true;
    }else {
        submitButton.disabled = false;
    }
}