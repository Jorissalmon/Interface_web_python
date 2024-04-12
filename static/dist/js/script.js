document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("#myForm");

    form.addEventListener("submit", async (event) => {
            event.preventDefault(); // Empêcher le formulaire de se soumettre normalement

            $('#submitBtn').prop('disabled', true); // Désactiver le bouton "Envoyer"
            $('.spinner').removeClass('hidden'); // Afficher l'icône de chargement
            $('.button-text').empty(); // Vider le texte du bouton

            const productUrl = document.querySelector("#product_url").value;
            const apiKey = document.querySelector("#api_key").value;

            // Effectuer une requête AJAX vers le serveur Flask
            $.ajax({
                type: 'POST',
                url: '/',
                data: {
                    product_url: productUrl,
                    api_key: apiKey
                },
                success: function (data) {
                    console.log(data);
                    // Séparer les avis positifs et négatifs
                    var positifs = data[0];
                    var negatifs = data[1];
                    // Afficher les avis positifs
                    $('#resultat1').html('<h3>Avis positifs :</h3><p>' + positifs + '</p>');
                    // Afficher les avis négatifs
                    $('#resultat2').html('<h3>Avis négatifs :</h3><p>' + negatifs + '</p>');

                    $('.spinner').addClass('hidden');
                    $('#submitBtn').prop('disabled', false);
                    $('.button-text').text("Analyser");
                },
                error: function (xhr, status, error) {
                    console.error('Erreur lors de la soumission du formulaire: ', error);
                }
        })
            ;
        }
    )
    ;
});
