output "env_file_content" {
    value = <<EOT
    DB_HOST=${digitalocean_droplet.tfm-apmc-db.ipv4_address_private}
    HOST=${digitalocean_droplet.tfm-apmc-app.ipv4_address_private}
    EOT
}
