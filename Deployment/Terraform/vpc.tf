resource "digitalocean_vpc" "tfm-apmc-vpc"{
    name = "tfm-apmc-vpc"
    region = var.region
    ip_range = "10.10.10.0/24"
}