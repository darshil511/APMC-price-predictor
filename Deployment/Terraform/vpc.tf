resource "digitalocean_vpc" "tfm-apmc-vpc"{
    name = "tfm-apmc-vpc"
    region = var.region
    ip_range = "10.10.10.0/24"
}
resource "time_sleep" "wait_44_seconds_to_destroy" {
  depends_on = [digitalocean_vpc.tfm-apmc-vpc]
  destroy_duration = "44s"
}
resource "null_resource" "placeholder" {
  depends_on = [time_sleep.wait_44_seconds_to_destroy]
}