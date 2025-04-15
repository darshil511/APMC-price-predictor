resource "digitalocean_droplet" "tfm-apmc-db" {
  image = "ubuntu-22-04-x64"
  name = "tfm-apmc-db"
  region = var.region
  size = "s-1vcpu-1gb"
  vpc_uuid = digitalocean_vpc.tfm-apmc-vpc.id
  ssh_keys = ["APMC-key_pair"]
  user_data = file("${path.module}/../User-data/script-db.sh")
}

resource "digitalocean_droplet" "tfm-apmc-app" {
  image = "ubuntu-22-04-x64"
  name = "tfm-apmc-app"
  region = var.region
  size = "s-1vcpu-1gb"
  vpc_uuid = digitalocean_vpc.tfm-apmc-vpc.id
  ssh_keys = ["APMC-key_pair"]
  user_data = file("${path.module}/../User-data/script-app.sh")
}