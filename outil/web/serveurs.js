"use strict";
/* Onglet « Serveurs » : les serveurs Odoo (gadget externe, facultatif) et les
   serveurs de dev des projets (commandes définies dans l'onglet Projets).
   Le contenu est dans hub.html (#vue-serveurs) ; les états sont relus toutes
   les 5 secondes (chargerServeurs, chargerServeursProjets). */
(() => {
  VUES.serveurs = {
    afficher: () => { rafraichirServeurs(); I18N.traduirePage($("#vue-serveurs")); },
    titre: "Serveurs", icone: icone("monitor"), groupe: "dev", ordre: 5,
  };
})();
