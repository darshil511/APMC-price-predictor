resource "digitalocean_domain" "tfm-apmc-domain" {
  name = "APMC-price_predictor.ld"
}

resource "digitalocean_record" "application" {
    domain = digitalocean_domain.tfm-apmc-domain.id
    type = "A"
    name = "app"
    value = digitalocean_droplet.tfm-apmc-app.ipv4_address_private
}

resource "digitalocean_record" "database" {
    domain = digitalocean_domain.tfm-apmc-domain.id
    type = "A"
    name = "db"
    value = digitalocean_droplet.tfm-apmc-db.ipv4_address_private
}