document.addEventListener("DOMContentLoaded", () => {

  const imagens = [
    "/static/imagens/imagens2.png",
    "/static/imagens/imagens3.png",
    "/static/imagens/imagens4.png",
    "/static/imagens/imagens5.png",
    "/static/imagens/imagens6.png",
    "/static/imagens/imagens7.png"
  ];

  let indice = 0;

  window.avancar = function () {
    indice = (indice + 1) % imagens.length;
    document.getElementById("imagem").src = imagens[indice];
  }

  window.voltar = function () {
    indice = (indice - 1 + imagens.length) % imagens.length;
    document.getElementById("imagem").src = imagens[indice];
  }

});
