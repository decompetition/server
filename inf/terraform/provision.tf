variable "envname" {
  description = "Environment Name"
  type        = string
}

variable "aws_region" {
  default     = "us-west-1"
  description = "AWS Region"
  type        = string
}

variable "aws_instance" {
  default     = "t3.micro"
  description = "AWS Instance Type"
  type        = string
}

variable "aws_access_key" {
  description = "AWS Access Key"
  type        = string
}

variable "aws_secret_key" {
  description = "AWS Secret Key"
  type        = string
}

variable "aws_keypair" {
  description = "AWS SSH Keypair"
  type        = string
}

variable "app_servers" {
  default     = 2
  description = "Number of App Servers"
  type        = number
}


# Prevent lots and lots of useless warnings...
# https://github.com/hashicorp/terraform/issues/22004
variable "sql_database"      {default = ""}
variable "sql_username"      {default = ""}
variable "sql_password"      {default = ""}
variable "app_secret"        {default = ""}
variable "app_start_time"    {default = ""}
variable "app_end_time"      {default = ""}


provider "aws" {
  region     = var.aws_region
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
}

data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}


resource "aws_security_group" "all" {
  name        = "${var.envname}-all"
  description = "Decompetition instance."

  ingress { # SSH
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # https://stackoverflow.com/a/59529259
  ingress { # Ping
    from_port   =  8
    to_port     = -1
    protocol    = "icmp"
    self        = true
  }

  egress { # Outbound
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.envname}-all"
  }
}

resource "aws_security_group" "web" {
  name        = "${var.envname}-web"
  description = "Decompetition web server."

  ingress { # HTTP
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress { # HTTPS
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.envname}-web"
  }
}

resource "aws_security_group" "app" {
  name        = "${var.envname}-app"
  description = "Decompetition app worker."

  ingress { # uWSGI
    from_port       = 9999
    to_port         = 9999
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
  }

  tags = {
    Name = "${var.envname}-app"
  }
}

resource "aws_security_group" "db" {
  name        = "${var.envname}-db"
  description = "Decompetition database."

  ingress { # PostgreSQL
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  tags = {
    Name = "${var.envname}-db"
  }
}


resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.aws_instance
  key_name      = var.aws_keypair

  security_groups = [
    aws_security_group.all.name,
    aws_security_group.web.name
  ]

  tags = {
    Name = "${var.envname}-web"
    Nick = "web"
  }

  lifecycle {
    ignore_changes = [ami]
  }
}

resource "aws_instance" "app" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.aws_instance
  key_name      = var.aws_keypair
  count         = var.app_servers

  root_block_device {
    volume_size = 16 #GB
  }

  security_groups = [
    aws_security_group.all.name,
    aws_security_group.app.name
  ]

  tags = {
    Name = "${var.envname}-app-${count.index}"
    Nick = "app-${count.index}"
  }

  lifecycle {
    ignore_changes = [ami]
  }
}

resource "aws_instance" "db" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.aws_instance
  key_name      = var.aws_keypair

  security_groups = [
    aws_security_group.all.name,
    aws_security_group.db.name
  ]

  tags = {
    Name = "${var.envname}-db"
    Nick = "db"
  }

  lifecycle {
    ignore_changes = [ami]
  }
}


resource "local_file" "inventory" {
  filename        = "../vars/${var.envname}/inventory.ini"
  file_permission = "0644"

  content = templatefile("templates/inventory.tmpl", {
    env = var.envname
    web = aws_instance.web
    app = aws_instance.app
    db  = aws_instance.db
  })
}

resource "local_file" "ssh_config" {
  filename        = "../vars/${var.envname}/ssh_config"
  file_permission = "0644"

  content = templatefile("templates/ssh_config.tmpl", {
    env = var.envname
    web = aws_instance.web
    app = aws_instance.app
    db  = aws_instance.db
  })
}
