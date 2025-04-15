variable "do_token" {
  description = "DigitalOcean Personal Access Token"
  type        = string
}

variable "region" {
  description = "Deployment region"
  type        = string
  default     = "sfo3"
}