function validarFormulario() {
    for (var i = 1; i <= 29; i++) {
        var nomeDoGrupo = "nivel" + i;
        var radioButtons = document.querySelectorAll('input[name="' + nomeDoGrupo + '"]');

        var peloMenosUmSelecionado = Array.from(radioButtons).some(function(radioButton) {
            return radioButton.checked;
        });

        if (!peloMenosUmSelecionado) {
            Swal.fire({
                icon: 'warning',
                title: 'Não foi possivel enviar as respostas!',
                text: 'Verifique se todas as questões foram respondidas.',
            });
            return false;
        }
    }
    return true;
}